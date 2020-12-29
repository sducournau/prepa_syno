# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PrepaSyno
                                 A QGIS plugin
 Ce plugin vous permet de préparer vos données pour générer correctement un synoptique de votre APS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-12-28
        copyright            : (C) 2020 by Circet
        email                : simon.ducournau@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PrepaSyno class from file PrepaSyno.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .prepa_syno import PrepaSyno
    return PrepaSyno(iface)
