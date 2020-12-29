from qgis.core import *
from pathlib import Path
import os.path
import json


PROJECT = QgsProject.instance()
ROOT = PROJECT.layerTreeRoot()
GROUP_LAYER = None
INPUTS = None
DIR_OUTPUT =  None
DIR_OUTPUT_ = None
DIR_PLUGIN = os.path.normpath(os.path.dirname(__file__))
DIR_STYLES = DIR_PLUGIN + os.sep + 'styles'
PATH_ABSOLUTE_PROJECT = os.path.normpath(PROJECT.readPath("./"))
ETUDES = None
config_data = None

with open(DIR_PLUGIN + '/config/config.json',"r") as f:
  config_data = json.load(f)

LAYERS_NAME = config_data['LAYERS_NAME']
GROUP_NAME = config_data['GROUP_NAME']
GESTIONNAIRE = config_data['GESTIONNAIRE']
