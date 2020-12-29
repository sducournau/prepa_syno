from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.utils import *
import os.path
from pathlib import Path
from .config import *
import json
import tempfile


class FilterLayers(QgsTask):


    def __init__(self,description, dockwidget,action, name):

        QgsTask.__init__(self, description)

        self.exception = None
        self.dockwidget = dockwidget
        self.action = action
        self.name = name


    def run(self):

        try:
            self.layers = QgsProject.instance().mapLayers().values()


            if self.action == 'start':
                if 'comac' in self.name:
                    selected_za_nro = self.dockwidget.comboBox_comac_select_za_nro.checkedItems()
                    selected_za_zpm = self.dockwidget.comboBox_comac_select_za_zpm.checkedItems()
                    selected_etude = self.dockwidget.comboBox_comac_select_etude.checkedItems()
                if 'capft' in self.name:
                    selected_za_nro = self.dockwidget.comboBox_capft_select_za_nro.checkedItems()
                    selected_za_zpm = self.dockwidget.comboBox_capft_select_za_zpm.checkedItems()
                    selected_etude = self.dockwidget.comboBox_capft_select_etude.checkedItems()

                filter_za_nro = '"za_nro" IN (\'' + '\',\''.join(selected_za_nro)  + '\')'
                filter_za_zpm = '"za_zpm" IN (\'' + '\',\''.join(selected_za_zpm)  + '\')'
                filter_etude = '"Etude" IN (\'' + '\',\''.join(selected_etude)  + '\')'


                for layer in self.layers:


                    if ('nro' in layer.name() and len(selected_za_nro) > 0) or (len(selected_za_nro) > 0 and len(selected_za_zpm) < 1 and len(selected_etude) < 1):
                        layer.setSubsetString(filter_za_nro)

                    elif len(selected_za_zpm) > 0:
                        layer.setSubsetString(filter_za_zpm)

                if len(selected_etude) > 0:
                    layer = PROJECT.mapLayersByName(self.name)[0]
                    layer.setSubsetString(filter_etude)

            if self.action == 'end':
                for layer in self.layers:

                    layer.setSubsetString('')
            return True


        except Exception as e:
            self.exception = e
            print(self.exception)
            return False

    def finished(self, result):
        """This function is called automatically when the task is completed and is
        called from the main thread so it is safe to interact with the GUI etc here"""
        if result is False:
            if self.exception is None:
                iface.messageBar().pushMessage('Task was cancelled')
            else:
                iface.messageBar().pushMessage('Errors occured')
                print(self.exception)

        else:
            print('Couches filtrées')


class barProgress:

    def __init__(self):
        self.prog = 0
        self.bar = None
        self.type = type
        iface.messageBar().clearWidgets()
        self.init()
        self.bar.show()

    def init(self):
        self.bar = QProgressBar()
        self.bar.setMaximum(100)
        self.bar.setValue(self.prog)
        iface.mainWindow().statusBar().addWidget(self.bar)

    def show(self):
        self.bar.show()


    def update(self, prog):
        self.bar.setValue(prog)

    def hide(self):
        self.bar.hide()

class msgProgress:

    def __init__(self):
        self.messageBar = iface.messageBar().createMessage('Doing something time consuming...')
        self.progressBar = QProgressBar()
        self.progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.cancelButton = QPushButton()
        self.cancelButton.setText('Cancel')
        self.messageBar.layout().addWidget(self.progressBar)
        self.messageBar.layout().addWidget(self.cancelButton)
        iface.messageBar().pushWidget(self.messageBar, Qgis.Info)


    def update(self, prog):
        self.progressBar.setValue(prog)

    def reset(self):
        self.progressBar.setValue(0)

    def setText(self, text):
        self.messageBar.setText(text)


class FileDialog_multi_dir(QFileDialog):
        def __init__(self, *args):
            QFileDialog.__init__(self, *args)
            self.setOption(self.DontUseNativeDialog, True)
            self.setFileMode(self.DirectoryOnly)

            for view in self.findChildren((QListView, QTreeView)):
                if isinstance(view.model(), QFileSystemModel):
                    view.setSelectionMode(QAbstractItemView.ExtendedSelection)

class selectDirectories:

    def __init__(self, dockwidget):
        self.dockwidget = dockwidget


    def select_import_folder(self):

        ex = FileDialog_multi_dir()
        ex.show()
        ex.exec_()
        dirs_input_list = ex.selectedFiles()
        self.dockwidget.mComboBox_comac_import_dir.clear()
        self.dockwidget.mComboBox_comac_import_dir.addItems(dirs_input_list)
        self.dockwidget.mComboBox_comac_import_dir.selectAllOptions()



    def select_import_files(self):
        filepaths_input= QFileDialog.getOpenFileNames(
            self.dockwidget, "Sélectionnez les C6 à importer","","C6 (*.xlsx)")
        filepaths_input_list = filepaths_input[0]
        self.dockwidget.mComboBox_capft_import_files.clear()
        self.dockwidget.mComboBox_capft_import_files.addItems(filepaths_input_list)
        self.dockwidget.mComboBox_capft_import_files.selectAllOptions()

    def select_export_folder(self):
        directory_output = QFileDialog.getExistingDirectory(
            self.dockwidget, "Sélectionnez dun dossier d'export")
        self.dockwidget.lineEdit_export_dir.setText(directory_output)




    def import_files_and_directories(self, layer_name):

        global INPUTS


        if layer_name == 'appuis_comac':
            INPUTS = self.dockwidget.mComboBox_comac_import_dir.checkedItems()

            print('input', INPUTS)

        elif layer_name == 'appuis_capft':
            INPUTS = self.dockwidget.mComboBox_capft_import_files.checkedItems()

            print('input', INPUTS)



    def init_import_directory(self):

        global DIR_OUTPUT
        global DIR_OUTPUT_
        PRECEDENT_GESTIONNAIRE = config_data['GESTIONNAIRE']

        if DIR_OUTPUT is None:

            DIR_OUTPUT =  tempfile.gettempdir()

        else:
            DIR_OUTPUT = config_data['DIR_OUTPUT']

        config_data['DIR_OUTPUT'] = DIR_OUTPUT
        DIR_OUTPUT_ = DIR_OUTPUT + os.sep + 'EXPORT_COMAC' + os.sep

        reload_config(config_data, PRECEDENT_GESTIONNAIRE)
        print('output', DIR_OUTPUT_)


    def update_import_directory(self):

        global DIR_OUTPUT
        global DIR_OUTPUT_
        PRECEDENT_GESTIONNAIRE = config_data['GESTIONNAIRE']

        if self.dockwidget.lineEdit_export_dir.editingFinished != '':
            DIR_OUTPUT = self.dockwidget.lineEdit_export_dir.text()

        config_data['DIR_OUTPUT'] = DIR_OUTPUT
        DIR_OUTPUT_ = DIR_OUTPUT + os.sep + 'EXPORT_COMAC' + os.sep
        reload_config(config_data, PRECEDENT_GESTIONNAIRE)
        print('output', DIR_OUTPUT_)




def zoom_to_features(layer):

    canvas = iface.mapCanvas()
    canvas.setExtent(layer.extent())
    canvas.refresh()


def reload_config(data, PRECEDENT_GESTIONNAIRE):

    with open(DIR_PLUGIN + '/config/config.json',"w") as outfile:
        json.dump(data, outfile)
    with open(DIR_PLUGIN + '/config/config.json',"r") as outfile:
        config_data = json.load(outfile)

    global LAYERS_NAME
    LAYERS_NAME = config_data['LAYERS_NAME']
    global GROUP_NAME
    GROUP_NAME = config_data['GROUP_NAME']
    global GESTIONNAIRE
    GESTIONNAIRE = config_data['GESTIONNAIRE']
    global DIR_OUTPUT
    DIR_OUTPUT = config_data['DIR_OUTPUT']
    DIR_OUTPUT_ = DIR_OUTPUT + os.sep + 'EXPORT_COMAC' + os.sep

    style_data = None
    with open(DIR_PLUGIN + '/styles/appuis_comac.qml', 'r') as outfile:
      style_data = outfile.read()
    style_data = style_data.replace('"' + PRECEDENT_GESTIONNAIRE + '"', '"' + data['GESTIONNAIRE'] + '"')
    style_data = style_data.replace("'" + PRECEDENT_GESTIONNAIRE + "'", "'" + data['GESTIONNAIRE'] + "'")

    with open(DIR_PLUGIN + '/styles/appuis_comac.qml', 'w') as outfile:
      outfile.write(style_data)


class populateComboBox:

    def __init__(self, dockwidget):
        self.dockwidget = dockwidget


    def onChange_tab(self, i):
        if i == 1:
            self.populate_za_nro('appuis_comac')
            self.populate_za_zpm('appuis_comac')
            self.populate_etudes('appuis_comac')


        if i == 2:
            self.populate_za_nro('appuis_capft')
            self.populate_za_zpm('appuis_capft')
            self.populate_etudes('appuis_capft')


    def populate_za_nro(self, name):

        try:
            list_za_nro = []

            layer = PROJECT.mapLayersByName(name)[0]
            idx = layer.fields().indexFromName('za_nro')
            print(name, layer, idx)
            for feature in layer.getFeatures():

                if feature.attributes()[idx] not in list_za_nro:
                    list_za_nro.append(feature.attributes()[idx])

            list_za_nro = sorted(list_za_nro)
            if 'comac' in name:
                self.dockwidget.comboBox_comac_select_za_nro.clear()
                self.dockwidget.comboBox_comac_select_za_nro.addItems(list_za_nro)

            if 'capft' in name:
                self.dockwidget.comboBox_capft_select_za_nro.clear()
                self.dockwidget.comboBox_capft_select_za_nro.addItems(list_za_nro)

        except:
            iface.messageBar().pushMessage(
                "Error", "Couche manquante : " + name,
                level=Qgis.Info, duration=5)

    def populate_za_zpm(self, name):

        try:

            list_za_zpm = []
            if 'comac' in name:
                selected_za_nro = self.dockwidget.comboBox_comac_select_za_nro.checkedItems()
            if 'capft' in name:
                selected_za_nro = self.dockwidget.comboBox_capft_select_za_nro.checkedItems()

            layer = PROJECT.mapLayersByName(name)[0]
            idx = layer.fields().indexFromName('za_zpm')

            if len(selected_za_nro) < 1:
                layer.selectAll()
                layer_selection = layer.selectedFeatures()
            else:
                layer.selectByExpression('"za_nro" IN (\'' + '\',\''.join(selected_za_nro)  + '\')', QgsVectorLayer.SetSelection)
                layer_selection = layer.selectedFeatures()

            for feature in layer_selection:
                if feature.attributes()[idx] not in list_za_zpm:
                    list_za_zpm.append(feature.attributes()[idx])

            layer.removeSelection()
            list_za_zpm = sorted(list_za_zpm)
            if 'comac' in name:
                self.dockwidget.comboBox_comac_select_za_zpm.clear()
                self.dockwidget.comboBox_comac_select_za_zpm.addItems(list_za_zpm)
            if 'capft' in name:
                self.dockwidget.comboBox_capft_select_za_zpm.clear()
                self.dockwidget.comboBox_capft_select_za_zpm.addItems(list_za_zpm)

        except:
            iface.messageBar().pushMessage(
                "Error", "Couche manquante : " + name,
                level=Qgis.Info, duration=5)



    def populate_etudes(self, name):

        try:
            list_etudes = []



            layer = PROJECT.mapLayersByName(name)[0]
            idx = layer.fields().indexFromName('Etude')
            if 'comac' in name:
                selected_za_nro = self.dockwidget.comboBox_comac_select_za_nro.checkedItems()
                selected_za_zpm = self.dockwidget.comboBox_comac_select_za_zpm.checkedItems()
            if 'capft' in name:
                selected_za_nro = self.dockwidget.comboBox_capft_select_za_nro.checkedItems()
                selected_za_zpm = self.dockwidget.comboBox_capft_select_za_zpm.checkedItems()


            if len(selected_za_nro) < 1 and len(selected_za_zpm) < 1:
                layer.selectAll()
                layer_selection = layer.selectedFeatures()
            elif len(selected_za_nro) > 0 and len(selected_za_zpm) < 1:
                layer.selectByExpression('"za_nro" IN (\'' + '\',\''.join(selected_za_nro)  + '\')', QgsVectorLayer.SetSelection)
                layer_selection = layer.selectedFeatures()
            elif len(selected_za_nro) > 0 and len(selected_za_zpm) > 0:
                layer.selectByExpression('"za_zpm" IN (\'' + '\',\''.join(selected_za_zpm)  + '\')', QgsVectorLayer.SetSelection)
                layer_selection = layer.selectedFeatures()

            for feature in layer_selection:
                if feature.attributes()[idx] not in list_etudes:
                    list_etudes.append(feature.attributes()[idx])

            layer.removeSelection()
            list_etudes = sorted(list_etudes)
            if 'comac' in name:
                self.dockwidget.comboBox_comac_select_etude.clear()
                self.dockwidget.comboBox_comac_select_etude.addItems(list_etudes)
            if 'capft' in name:
                self.dockwidget.comboBox_capft_select_etude.clear()
                self.dockwidget.comboBox_capft_select_etude.addItems(list_etudes)

        except:
            iface.messageBar().pushMessage(
                "Error", "Couche manquante : " + name,
                level=Qgis.Info, duration=5)
