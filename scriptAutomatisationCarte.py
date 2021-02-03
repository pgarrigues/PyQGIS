# -*- coding: utf-8 -*-

"""

• L’utilisateur saisi une valeur de buffer

• On crée un buffer autour des boites selon la valeur saisie par l’utilisateur. Le
résultat du buffer est ensuite affiché dans le projet QGIS.

• L’utilisateur saisi deux valeurs capacite et mode de pose

• Sur la couche <cables > faire un filtre sur le champ capacite supérieur à la
valeur saisie et mode_pose = au mode de pose saisi

• A partir du résultat de la sélection faire une carte avec symbologie graduée
en fonction du nombre de prises (colonne nb_prises)

"""

## Import des processing :

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingOutputNumber,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       ####
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFile,
                       QgsField,
                       QgsExpression,
                       QgsExpressionContext,
                       QgsExpressionContextUtils,
                       QgsSymbol,
                       QgsRendererRange,
                       QgsGraduatedSymbolRenderer,
                       QgsProject)
from qgis.utils import iface
import processing
import os


class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        return 'myscript'

    def displayName(self):
        return self.tr('My Script')

    def group(self):
        return self.tr('Example scripts')

    def groupId(self):
        return 'examplescripts'

    def shortHelpString(self):
        return self.tr("Example algorithm short description")
    
    
    
    #######################################################################################
    #######################################################################################
    #######################################################################################
    
    
    ### Déclaration des variables ###
    
    # Couche sur laquelle on fait le buffer :
    INPUT = 'INPUT'
    
    # Paramètre de distance du buffer :
    BUFFERDIST = 'BUFFERDIST'
    
    # Paramètre de capacité des cables :
    CAPACITE = 'CAPACITE'
    
    # Paramètre du mode de pose des cables :
    MODE_DE_POSE = 'MODE_DE_POSE'
    
    # Buffer Output :
    BUFFER_OUTPUT = 'BUFFER_OUTPUT'
    
    # Cables Output :
    CABLES_OUTPUT = 'CABLES_OUTPUT'
    
    # Output final :
    OUTPUT = 'OUTPUT'
    
    def initAlgorithm(self, config=None):
        
        # Couche buffer :
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT',
                self.tr('Couche buffer :'),
                types=[QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        # Distance buffer :
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST',
                self.tr('Distance buffer :'),
                defaultValue = 1.0,
                # Unités :
                parentParameterName='INPUT'
            )
        )
        
        # Capacité cable :
        self.addParameter(
            QgsProcessingParameterNumber(
            'CAPACITE',
            self.tr('Capacité du cable :'),
            optional = False,
            defaultValue = 1.0
            )
        )
        
        # Mode de pose du cable :
        self.addParameter(
            QgsProcessingParameterString(
            'MODE_DE_POSE',
            self.tr('Mode de pose du cable :'),
            optional = False,
            defaultValue = "AERIEN"
            )
        )
        
        # Buffer output :
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                'BUFFER_OUTPUT',
                self.tr('Buffer output'),
            )
        )
        
        # Cables output :
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                'CABLES_OUTPUT',
                self.tr('Cables output'),
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        
        # Couche buffer :
        input_featuresource = self.parameterAsSource(parameters,
                                                     'INPUT',
                                                     context)
        
        # Buffer distance :
        bufferdist = self.parameterAsDouble(parameters, 
                                            'BUFFERDIST', 
                                            context)
        
        # Check for cancelation
        if feedback.isCanceled():
            return {}
        
        
        buffer_result = processing.run(
            'native:buffer',
            {
                # Here we pass on the original parameter values of INPUT
                # and BUFFER_OUTPUT to the buffer algorithm.
                'INPUT': parameters['INPUT'],
                'OUTPUT': parameters['BUFFER_OUTPUT'],
                'DISTANCE': bufferdist,
                'SEGMENTS': 10,
                'DISSOLVE': True,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 10
            },
            # Because the buffer algorithm is being run as a step in
            # another larger algorithm, the is_child_algorithm option
            # should be set to True
            is_child_algorithm=True,
            #
            # It's important to pass on the context and feedback objects to
            # child algorithms, so that they can properly give feedback to
            # users and handle cancelation requests.
            context=context,
            feedback=feedback)


        # Check for cancelation
        if feedback.isCanceled():
            return {}
        
        
        # Selection de la couche cable :
        cables = QgsVectorLayer(
                    "/Users/pierre-loupgarrigues/Python JupyterLab/M2/pyqgis/Evaluation_pyqgis/data/cables.shp",
                    "cables", 
                    "ogr")
        cables = iface.activeLayer()
        
        # Séléction des cables en fonction des paramètres choisis :
        cables.selectByExpression(" \"capacite\" > '{}' AND \"mode_pose\" = '{}' ".format(parameters[self.CAPACITE], parameters[self.MODE_DE_POSE]))
        
        # Vérification :
        selectionCapacite = self.parameterAsDouble(parameters, 'CAPACITE', context)
        print(selectionCapacite)
        # Vérification :
        selectionModeDePose = self.parameterAsString(parameters, 'MODE_DE_POSE', context)
        print(selectionModeDePose)
        
    
        # Sauvegarde de la séléction des cables :
        cables_selection = processing.run(
            'qgis:saveselectedfeatures',
            {'INPUT':cables,
            #'OUTPUT':'memory:'
            'OUTPUT': parameters['CABLES_OUTPUT']
            },
            context=context, 
            feedback=feedback, 
            is_child_algorithm=True)
            
        
        mes_cables=cables_selection['OUTPUT']
        
        
        ### SYMBOLOGIE GRADUEE
        nb_prises = (
            ('Faible', 0, 9, 'green'),
            ('Moyen_1', 10, 25, 'yellow'),
            ('Moyen_2', 26, 100, 'orange'),
            ('Eleve', 101, 1000000, 'red'),
            
        )
        
        # creation 
        ranges = []
        for label, lower, upper, color in nb_prises:
            symbol = QgsSymbol.defaultSymbol(cables.geometryType())
            symbol.setColor(QColor(color))
            rng = QgsRendererRange(lower, upper, symbol, label)
            ranges.append(rng)

        # create the renderer and assign it to a layer
        expression = 'nb_prises' # field name
        renderer = QgsGraduatedSymbolRenderer(expression, ranges)
        cables.setRenderer(renderer)
        
        
        # Return the results
        return {
        'BUFFER_OUTPUT': buffer_result['OUTPUT'],
        'CABLES_OUTPUT' : cables_selection['OUTPUT']
        }
        