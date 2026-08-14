"""
===========================================================================
INLAND MESH BOUNDARY GENERATOR
===========================================================================
Purpose: 
GGenerates a continuous inland boundary line for hydrodynamic mesh. 
It calculates the maximum inland extent by combining 
a 500m coastal buffer with a 20m elevation contour.

Instructions:
This code should run in the Python Console in QGIS. You can find the 
Python Console in the Plugins menu (Plugins > Python Console).

Prerequisites:
- Layers must be loaded in the QGIS project.
- 'PA_BC_500Inland' : Polygon representing land =500m from the coast.
- 'contour_20m_poly' : Polygon representing land =20m in elevation.
===========================================================================
"""

import processing
from qgis.core import QgsProject, QgsCoordinateReferenceSystem

# =========================================================
# LAYER NAMES
# =========================================================
poly_500m = 'PA_BC_500Inland'
poly_20m = 'contour_20m_poly'

target_crs = QgsCoordinateReferenceSystem('EPSG:3832')

print("1. Reprojecting 20m contour to EPSG:3832...")
rep_20m = processing.run("native:reprojectlayer", {
    'INPUT': poly_20m, 'TARGET_CRS': target_crs, 'OUTPUT': 'memory:'
})['OUTPUT']

print("2. Repairing geometries to ensure perfect Boolean math...")
fix_500 = processing.run("native:fixgeometries", {'INPUT': poly_500m, 'OUTPUT': 'memory:'})['OUTPUT']
fix_20 = processing.run("native:fixgeometries", {'INPUT': rep_20m, 'OUTPUT': 'memory:'})['OUTPUT']

print("3. Intersecting the two highland cores...")
# Intersection forces the boundary to take the MOST RESTRICTIVE path.
# It also naturally deletes any 500m small islands that lack a 20m contour.
core_intersection = processing.run("native:intersection", {
    'INPUT': fix_500,
    'OVERLAY': fix_20,
    'OUTPUT': 'memory:'
})['OUTPUT']

print("4. Dissolving to ensure a single solid landmass...")
solid_core = processing.run("native:dissolve", {
    'INPUT': core_intersection, 'OUTPUT': 'memory:'
})['OUTPUT']

print("5. Converting the perfectly intersected core into your final boundary line...")
final_line = processing.run("native:polygonstolines", {
    'INPUT': solid_core, 'OUTPUT': 'memory:'
})['OUTPUT']

print("6. Loading into map...")
final_line.setName("PACIFIC_FINAL_VALLEY_MESH")
QgsProject.instance().addMapLayer(final_line)

print("SUCCESS! Generation complete.")
