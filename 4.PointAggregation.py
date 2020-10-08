# Name: Point Aggregation
# Description: Aggregation of points to the centroids of the polygons that they lie within.
# Author: O. Kounadi, 6/03/2015
# Reference: This code is part of a code written for an adaptive geographical masking method that is published in:  
# Kounadi, O., & Leitner, M. (2016). Adaptive areal elimination (AAE): A transparent way of disclosing protected spatial datasets.
# Computers, Environment and Urban Systems, 57, 59-67.

# Copy point file as "o_points" and polygon file as "areas" to a new personal geodatabase
# All working output will be saved in the geodatabase
# --------------------------------------------

# Set workspace variable
workspace = r"D:\mask.mdb"

# Set variables for paths (the file name, e.g "\o_points1",  should not be replaced)
path = r"D:\mask.mdb\areas"
path1= r"D:\mask.mdb\areas_new"
path2= r"D:\mask.mdb\o_points1"
path3= r"D:\mask.mdb\m_points1"

# Import system modules
import arcpy,os,sys
import arcpy.mapping
from arcpy import env

# Set workspace
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

# Point Aggregation
arcpy.CopyFeatures_management(path, "areas_new")
arcpy.FeatureToPoint_management("areas_new", "aggr_points")
arcpy.AddXY_management("aggr_points")
arcpy.JoinField_management("areas_new","OBJECTID","aggr_points","ORIG_FID","#")
arcpy.DeleteField_management("areas_new","ORIG_FID;RORI_1")
arcpy.AddXY_management("o_points")
arcpy.AddField_management("o_points","origX","FLOAT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
arcpy.AddField_management("o_points","origY","FLOAT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
arcpy.CalculateField_management("o_points","origX","[POINT_X]","VB","#")
arcpy.CalculateField_management("o_points","origY","[POINT_Y]","VB","#")
arcpy.DeleteField_management("o_points","POINT_X;POINT_Y")
arcpy.SpatialJoin_analysis("o_points","areas_new","o_points1","JOIN_ONE_TO_ONE","KEEP_ALL","origX origX true true false 4 Float 0 0 ,First,#,o_points,origX,-1,-1;origY origY true true false 4 Float 0 0 ,First,#,o_points,origY,-1,-1;POINT_X POINT_X true true false 8 Double 0 0 ,First,#,areas_new,POINT_X,-1,-1;POINT_Y POINT_Y true true false 8 Double 0 0 ,First,#,areas_new,POINT_Y,-1,-1","INTERSECT","#","#")
arcpy.DeleteField_management("areas_new","Point_X;Point_Y")
arcpy.DeleteField_management("o_points1","Join_Count;TARGET_FID")
arcpy.AddField_management("o_points1","MaskedX","FLOAT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
arcpy.AddField_management("o_points1","MaskedY","FLOAT","#","#","#","#","NULLABLE","NON_REQUIRED","#")
arcpy.CalculateField_management("o_points1","MaskedX","[POINT_X]","VB","#")
arcpy.CalculateField_management("o_points1","MaskedY","[POINT_Y]","VB","#")
arcpy.DeleteField_management("o_points1","POINT_X;POINT_Y")
arcpy.MakeXYEventLayer_management("o_points1","MaskedX","MaskedY","event_points")
arcpy.CopyFeatures_management("event_points","m_points1")
arcpy.CopyFeatures_management("m_points1","m_points")

# Delete unnecessary files
arcpy.DeleteField_management("aggr_points","ORIG_FID")
arcpy.Delete_management("event_points")
arcpy.Delete_management(path1)
arcpy.Delete_management(path2)
arcpy.Delete_management(path3)
print "Points from point aggregation are created as 'm_points'."
      
# Finish Process
arcpy.RefreshCatalog(workspace)
print "Process completed."