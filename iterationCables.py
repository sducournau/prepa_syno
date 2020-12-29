# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import *
from qgis import processing
from qgis.utils import iface
import json
from . import utils as utils
from .utils import *

class iterationCables:

    def __init__(self):
        self.run()

    def sumpfOrder(self, k):
        return k['sum_pf']

    def capacityOrder(self, k):
        return k['capacite'],k['sum_um'],k['sum_el']

    def typeOrder(self, k):
        return k['IMB'],k['Rbal']

    def pathOrder(self, k):
        return k['order_path']

    def createGroupCables(self):

        group_cables = {}
        selection_pt_pf = []
        selection_za_pf = []
        selection_imb = []
        type_rbal = 0
        imb = 0

        for feat_cable in self.features_cable:



            if feat_cable['origine'] not in group_cables:
                group_cables[feat_cable['origine']]= {}
                group_cables[feat_cable['origine']]['sorted_data'] = []
                group_cables[feat_cable['origine']]['data'] = []
                group_cables[feat_cable['origine']]['troncon'] = feat_cable['troncon']


            if feat_cable['troncon'] == 'D1':
                # try:
                self.layers_pf['pa']['point_pa'].selectByExpression('"za_zpa" = ' + '\'' + str(feat_cable['extremite']) + '\'', QgsVectorLayer.SetSelection)
                self.layers_pf['pa']['zone_de_pa'].selectByExpression('"za_zpa" = ' + '\'' + str(feat_cable['extremite']) + '\'', QgsVectorLayer.SetSelection)
                selection_pt_pf = self.layers_pf['pa']['point_pa'].selectedFeatures()
                selection_za_pf = self.layers_pf['pa']['zone_de_pa'].selectedFeatures()

                self.layer_sites.selectByExpression('"type" = \'IMB\'', QgsVectorLayer.SetSelection)
                selection_imb = self.layer_sites.selectedFeatures()
                if len(selection_pt_pf) > 0:
                    for feat in selection_imb:
                        if selection_pt_pf[0].geometry().intersects(feat.geometry()):
                            imb = 1
                            break

                calcul_rbal = {'RAC':0, 'RAD':0, 'L':0}

                feats = [feat for feat in self.layer_rbal.getFeatures()]
                for feat in feats:
                    if selection_za_pf[0].geometry().intersects(feat.geometry()):
                        if 'RAC' in feat["type"]:
                            calcul_rbal['RAC'] += 1
                        if 'RAD' in feat["type"]:
                            calcul_rbal['RAD'] += 1
                        if 'L' in feat["type"]:
                            calcul_rbal['L'] += 1

                total = sorted(calcul_rbal.items(),reverse=True, key = lambda kv:(kv[1], kv[0]))

                for k in total:
                    print(k[0])
                    if 'RAC' in k[0]:
                        type_rbal = 0
                    if 'RAD' in k[0]:
                        type_rbal = 1
                    if 'L' in k[0]:
                        type_rbal = 2
                    break



                # except:
                #     selection_pt_pf = None
                #     print('Erreur D1')

            if feat_cable['troncon'] == 'D2':
                # try:
                type_rbal = 0
                imb = 0
                self.layers_pf['pb']['point_pb'].selectByExpression('"za_zpb" = ' + '\'' + str(feat_cable['extremite']) + '\'', QgsVectorLayer.SetSelection)
                self.layers_pf['pb']['zone_de_pb'].selectByExpression('"za_zpb" = ' + '\'' + str(feat_cable['extremite']) + '\'', QgsVectorLayer.SetSelection)
                selection_pt_pf = self.layers_pf['pb']['point_pb'].selectedFeatures()
                selection_za_pf = self.layers_pf['pb']['zone_de_pb'].selectedFeatures()

                self.layer_sites.selectByExpression('"type" = \'IMB\'', QgsVectorLayer.SetSelection)
                selection_imb = self.layer_sites.selectedFeatures()
                for feat in selection_imb:
                    if selection_pt_pf[0].geometry().intersects(feat.geometry()):
                        imb = 1
                        break

                feats = [feat for feat in self.layer_rbal.getFeatures()]
                for feat in feats:
                    if selection_za_pf[0].geometry().intersects(feat.geometry()):
                        if 'RAC' in feat["type"]:
                            type_rbal = 0
                        if 'RAD' in feat["type"]:
                            type_rbal = 1
                        if 'L' in feat["type"]:
                            type_rbal = 2
                        break
                #
                # except:
                #     selection_pt_pf = None
                #     print('Erreur D2')

            if selection_pt_pf:
                nb_um = float(selection_pt_pf[0]['nb_um'])
                nb_el = float(selection_pt_pf[0]['nb_el'])
            else:
                nb_um = float(0)
                nb_el = float(0)


            group_cables[feat_cable['origine']]['data'].append(
            {
            'id':feat_cable.id(),
            'origine' : feat_cable['origine'],
            'extremite': feat_cable['extremite'],
            'path' : [],
            'capacite' : int(feat_cable['capacite']),
            'nb_um' : nb_um,
            'nb_el' : nb_el,
            'IMB' : imb,
            'Rbal' : type_rbal,
            'ordre' : 0,
            'sum_um' : 0,
            'sum_el' : 0,
            'sum_pf' : 0
            })



        return group_cables

    def orderGroupCablesbyCapacity(self):


        for origine in self.group_cables:
            for y, cable in enumerate(self.group_cables[origine]['data']):
                sum_el = cable['nb_el']
                sum_um = cable['nb_um']
                sum_pf = 1

                for origine_ in self.group_cables:
                    for cable_ in self.group_cables[origine_]['data']:
                        if ('_'.join(cable['path']) in '_'.join(cable_['path'])) and ('_'.join(cable['path']) != '_'.join(cable_['path'])):
                            if self.group_cables[origine]['troncon'] ==  'D2' or 'PEP' in cable['extremite']:
                                sum_el += cable_['nb_el']
                                sum_um += cable_['nb_um']

                            sum_pf += 1
                                # rbal = cable_['Rbal']
                self.group_cables[origine]['data'][y]['sum_el'] = sum_el
                self.group_cables[origine]['data'][y]['sum_um'] = sum_um
                self.group_cables[origine]['data'][y]['sum_pf'] = sum_pf


        for origine in self.group_cables:
            for y, cable in enumerate(self.group_cables[origine]['data']):
                sum_el = cable['sum_el']
                sum_um = cable['sum_um']
                sum_pf = cable['sum_pf']
                rbal = 0
                for origine_ in self.group_cables:
                    for cable_ in self.group_cables[origine_]['data']:
                        if ('_'.join(cable['path']) in '_'.join(cable_['path'])) and ('_'.join(cable['path']) != '_'.join(cable_['path'])):
                            if 'PEP' in cable['extremite'] and 'PA' in cable_['extremite']:
                                sum_el = cable_['sum_el']
                                sum_um = cable_['sum_um']
                                sum_pf = cable_['sum_pf'] + 1
                                rbal = cable_['Rbal']

                                # rbal = cable_['Rbal']
                self.group_cables[origine]['data'][y]['sum_el'] = sum_el
                self.group_cables[origine]['data'][y]['sum_um'] = sum_um
                self.group_cables[origine]['data'][y]['sum_pf'] = sum_pf
                self.group_cables[origine]['data'][y]['Rbal'] = rbal



        for origine in self.group_cables:
            self.group_cables[origine]['sorted_data_by_capacity'] = sorted(self.group_cables[origine]['data'], reverse=True, key=lambda k: (self.sumpfOrder(k)))
            self.group_cables[origine]['sorted_data_by_capacity'] = sorted(self.group_cables[origine]['data'], reverse=True, key=lambda k: (self.capacityOrder(k)))
            self.group_cables[origine]['sorted_data_by_capacity'] = sorted(self.group_cables[origine]['sorted_data_by_capacity'], key=lambda k: (self.typeOrder(k)))


        for origine in self.group_cables:
            for z, parcours in enumerate(self.group_cables[origine]['sorted_data_by_capacity']):
                self.group_cables[origine]['sorted_data_by_capacity'][z]['ordre'] = z + 1

    def orderGroupCablesbyPath(self):

        self.list_cables = sorted(self.list_cables, key=lambda k: self.pathOrder(k))

    def iterateNode(self, origine, z):
        path = []
        i = 0
        while i < len(self.parcours_array):
            if self.group_cables[origine]['data'][z]['origine'] == self.parcours_array[i][-1]:
                path += self.parcours_array[i]
                path.append(self.group_cables[origine]['data'][z]['extremite'])
                break
            i += 1

        if len(path) < 1: path = [self.group_cables[origine]['data'][z]['origine'] , self.group_cables[origine]['data'][z]['extremite']]

        if self.group_cables[origine]['troncon'] == 'D1' or (self.group_cables[origine]['troncon'] == 'D2' and len(path) > 2):
            self.parcours_array.append(path)
            self.group_cables[origine]['data'][z]['path'] = path
            if self.group_cables[origine]['data'][z]['id'] in self.parcours_manquants_array:
                self.parcours_manquants_array.remove(self.group_cables[origine]['data'][z]['id'])

        else:
            self.parcours_manquants_array.append(self.group_cables[origine]['data'][z]['id'])

    def calculPath(self):


        if len(self.parcours_manquants_array) < 1:
            for origine in self.group_cables:
                for z, parcours in enumerate(self.group_cables[origine]['data']):
                    self.iterateNode(origine, z)

        else:
            for origine in self.group_cables:
                for z, parcours in enumerate(self.group_cables[origine]['data']):
                    if self.group_cables[origine]['data'][z]['id'] in self.parcours_manquants_array:
                        self.iterateNode(origine, z)

    def calculSection(self):


        for origine in self.group_cables:
            for cable in self.group_cables[origine]['sorted_data_by_capacity']:


                k = 0

                ordre = []

                try:
                    while k < len(cable['path'])-1:
                        for y, node in enumerate(self.group_cables[cable['path'][k]]['sorted_data_by_capacity']):

                            if node['extremite'] == cable['path'][k+1]:
                                if self.group_cables[cable['path'][k]]['troncon'] == 'D1':
                                    ordre.append(node['ordre'] * 100)
                                if self.group_cables[cable['path'][k]]['troncon'] == 'D2':
                                    ordre.append(node['ordre'])



                        k += 1
                        cable['order_path'] = ordre


                    self.list_cables.append(cable)


                except:
                    print(cable, ordre)

    def updateLayers(self):

        list_order_path = []
        last_d1 = 0
        incrementation_d1 = 1
        incrementation_pb = 0
        print(self.list_cables)
        self.output_layer_cable.startEditing()
        self.output_layer_pb.startEditing()
        self.output_layer_pa.startEditing()


        field_section = self.output_layer_cable.fields().indexFromName("section")
        field_num_pb = [self.output_layer_pb.fields().indexFromName("za_zpa"),self.output_layer_pb.fields().indexFromName("za_zpb")]
        field_num_pa = self.output_layer_pa.fields().indexFromName("za_zpa")
        PB = ''
        PA = ''


        # count_pb = self.output_layer_pb.featureCount()
        # len_count_pb = len(count_pb)

        for cable in self.list_cables:
            if len(cable['order_path']) < 3:
                print(cable)
            if last_d1 == cable['order_path'][0]:
                incrementation_pb += 1
                order_path_temp = cable['order_path'][1:]
                for i, value in enumerate(order_path_temp):

                    if value > 1 and order_path_temp[i] != list_order_path[i]:
                        incrementation_d1 += 1



                list_order_path = order_path_temp

                self.output_layer_cable.changeAttributeValue(cable['id'], field_section, cable['order_path'][0] + incrementation_d1)
                if 'PEP' not in cable['extremite']:
                    self.output_layer_pb.selectByExpression('"za_zpb" = ' + '\'' + str(cable['extremite']) + '\'', QgsVectorLayer.SetSelection)
                    selection =  self.output_layer_pb.selectedFeatures()
                    if len(selection) > 0:
                        sel = selection[0]
                        PB = sel['za_zpm'] + '_PB_' + str(incrementation_pb).zfill(3)
                        self.output_layer_pb.changeAttributeValue(sel.id(), field_num_pb[0], PA)
                        self.output_layer_pb.changeAttributeValue(sel.id(), field_num_pb[1], PB)
                        self.output_layer_pb.removeSelection()
                    last_d1 = cable['order_path'][0]
            else:

                if 'PEP' not in cable['origine']:
                    self.output_layer_cable.changeAttributeValue(cable['id'], field_section, cable['order_path'][0])
                if 'PEP' not in cable['extremite']:
                    self.output_layer_pa.selectByExpression('"za_zpa" = ' + '\'' + str(cable['extremite']) + '\'', QgsVectorLayer.SetSelection)
                    selection =  self.output_layer_pa.selectedFeatures()
                    if len(selection) > 0:
                        sel = selection[0]

                        PA = sel['za_zpm'] + '_PA_' + str(int(cable['order_path'][0]/100)).zfill(2)

                        self.output_layer_pa.changeAttributeValue(sel.id(), field_num_pa, PA)
                        self.output_layer_pa.removeSelection()
                    incrementation_d1 = 1
                    last_d1 = cable['order_path'][0]



        self.output_layer_cable.commitChanges()
        self.output_layer_pb.commitChanges()
        self.output_layer_pa.commitChanges()

        print(str(len(self.features_cable)) + ' sections calculées')

    def run(self):


        # try:
        self.layers_pf = {
        'pm' : {'point_pm': QgsProject.instance().mapLayersByName(LAYERS_NAME['POINT_PM']['nom'])[0], 'zone_de_pm': QgsProject.instance().mapLayersByName(LAYERS_NAME['ZONE_DE_PM']['nom'])[0]},
        'pa' : {'point_pa': QgsProject.instance().mapLayersByName(LAYERS_NAME['POINT_PA']['nom'])[0], 'zone_de_pa': QgsProject.instance().mapLayersByName(LAYERS_NAME['ZONE_DE_PA']['nom'])[0]},
        'pb' : {'point_pb': QgsProject.instance().mapLayersByName(LAYERS_NAME['POINT_PB']['nom'])[0], 'zone_de_pb': QgsProject.instance().mapLayersByName(LAYERS_NAME['ZONE_DE_PB']['nom'])[0]}
        }
        self.layer_sites = QgsProject.instance().mapLayersByName(LAYERS_NAME['SITES_SUPPORTS']['nom'])[0]
        self.layer_rbal = QgsProject.instance().mapLayersByName(LAYERS_NAME['RBAL']['nom'])[0]
        self.layer_cable =  QgsProject.instance().mapLayersByName(LAYERS_NAME['CABLE']['nom'])[0]

        self.layers_pf['pb']['point_pb'].selectAll()
        self.output_layer_pb = self.layers_pf['pb']['point_pb'].materialize(QgsFeatureRequest().setFilterFids(self.layers_pf['pb']['point_pb'].selectedFeatureIds()))
        utils.PROJECT.addMapLayer(self.output_layer_pb, True)

        self.layers_pf['pa']['point_pa'].selectAll()
        self.output_layer_pa = self.layers_pf['pa']['point_pa'].materialize(QgsFeatureRequest().setFilterFids(self.layers_pf['pa']['point_pa'].selectedFeatureIds()))
        utils.PROJECT.addMapLayer(self.output_layer_pa, True)

        # except:
        #     print('error loading layers')
        #

        self.list_cables = []

        self.layer_cable.selectByExpression('"troncon" IN (\'D1\', \'D2\') and "statut" =  \'EN ETUDE\'', QgsVectorLayer.SetSelection)
        self.output_layer_cable = self.layer_cable.materialize(QgsFeatureRequest().setFilterFids(self.layer_cable.selectedFeatureIds()))
        utils.PROJECT.addMapLayer(self.output_layer_cable, True)
        self.output_layer_cable.selectAll()
        layer_cable_selection = self.output_layer_cable.selectedFeatures()
        self.features_cable = sorted(layer_cable_selection, key=lambda f: (f['troncon'],f['origine'],f['extremite']))

        self.group_cables = self.createGroupCables()





        self.parcours_array = []
        self.parcours_manquants_array = []

        self.calculPath()
        while len(self.parcours_manquants_array) > 0:
            self.calculPath()


        self.orderGroupCablesbyCapacity()
        self.calculSection()


        self.orderGroupCablesbyPath()
        self.updateLayers()




        layers = iface.mapCanvas().layers()
        for layer in layers:
            layer.removeSelection()
