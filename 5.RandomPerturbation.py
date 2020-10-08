# Name: Random Perturbation
# Description: Random displacement of points within polygons.
# Author: O.Kounadi, 6/03/2015
# Reference: This code is part of a code written for an adaptive geographical masking method that is published in:
# Kounadi, O., & Leitner, M. (2016). Adaptive areal elimination (AAE): A transparent way of disclosing protected spatial datasets.
# Computers, Environment and Urban Systems, 57, 59-67.

# Copy confidential points and polygon file to a new personal geodatabase
# All working output will be saved in the geodatabase
# --------------------------------------------

# Set workspace variable
workspace = r"D:\mask.mdb"

# Set disclosure value
Ka = 5

# Set variables for paths (the file name, e.g "\areas",  should not be replaced)
path = r"D:\mask.mdb\areas"
path1= r"D:\mask.mdb\areas_new"

# Import system modules
import arcpy, os, sys
import arcpy.mapping
from arcpy import env

# Set workspace
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

# Random perturbation
arcpy.SpatialJoin_analysis("areas", "o_points", "areas_new", "JOIN_ONE_TO_MANY", "KEEP_ALL",
                           "RORI RORI true true false 4 Long 0 0 ,First,#,areas,RORI,-1,-1;origX origX true true false 4 Float 0 0 ,First,#,o_points,origX,-1,-1;origY origY true true false 4 Float 0 0 ,First,#,o_points,origY,-1,-1",
                           "CONTAINS", "#", "#")
arcpy.CreateRandomPoints_management(workspace, "m_rand_points", "areas_new", "areas_new", "Join_Count", "", "POINT", "")
arcpy.JoinField_management("m_rand_points", "CID", "areas_new", "OBJECTID", "origX;origY")
arcpy.DeleteField_management("m_rand_points", "CID")
arcpy.AddXY_management("m_rand_points")
arcpy.AddField_management("m_rand_points", "m_randomX", "FLOAT", "#", "#", "#", "#", "NULLABLE", "NON_REQUIRED", "#")
arcpy.AddField_management("m_rand_points", "m_randomY", "FLOAT", "#", "#", "#", "#", "NULLABLE", "NON_REQUIRED", "#")
arcpy.CalculateField_management("m_rand_points", "m_randomX", "[POINT_X]", "VB", "#")
arcpy.CalculateField_management("m_rand_points", "m_randomY", "[POINT_Y]", "VB", "#")
arcpy.DeleteField_management("m_rand_points", "POINT_X;POINT_Y")

# Finish Process
arcpy.Delete_management(path1)
arcpy.RefreshCatalog(workspace)

print "Points from random perturbation are created as 'm_rand_points'."
print "Process completed."

