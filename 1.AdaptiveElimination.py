# Name: Adaptive Elimination
# Description: Eliminating polygons until all polygons have attribute values that are equal or greater than a minimum value
# Author: O. Kounadi, 6/03/2015
# Reference: This code is part of a code written for an adaptive geographical masking method that is published in:
# Kounadi, O., & Leitner, M. (2016). Adaptive areal elimination (AAE): A transparent way of disclosing protected spatial datasets.
# Computers, Environment and Urban Systems, 57, 59-67.

# Note: each polygon is merged with the neighbouring polygon that has the longest shared border. The code will not work when neighboring polygons have the same length
# for all (equilateral) or some their sides (e.g. grid cells).

# Copy polygon file as "areas" to a new personal geodatabase
# Working output will be saved in the geodatabase
# --------------------------------------------

# Set workspace variable
workspace = r"D:\mask.mdb"

# Set minimum value
Ka = 5

# Set variables for paths (the file name, e.g "\areas",  should not be replaced)
path = r"D:\mask.mdb\areas"
path2= r"D:\mask.mdb\areas_new"
path3= r"D:\mask.mdb\new"
path4= r"D:\mask.mdb\new1"

# Import system modules
import arcpy,os,sys
import arcpy.mapping
from arcpy import env

# Set workspace
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

# Define variable to check for min value
arcpy.CopyFeatures_management(path, "areas_new")
arcpy.SelectLayerByAttribute_management ("areas_new", "NEW_SELECTION",'[RORI] in (SELECT min( [RORI] ) FROM areas_new)')
check1 = arcpy.SearchCursor("areas_new")
for row in check1:
   dv =  row.getValue("RORI")
del check1, row

# Elimination process 
while dv < Ka :
   arcpy.Eliminate_management("areas_new", "new")
   arcpy.SelectLayerByAttribute_management("areas_new","CLEAR_SELECTION")
   arcpy.SpatialJoin_analysis("new","areas_new","new1","JOIN_ONE_TO_ONE","KEEP_ALL","RORI RORI true true false 4 Long 0 0 ,First,#,new,RORI,-1,-1;RORI RORI2 true true false 4 Long 0 0 ,Sum,#,areas_new,RORI,-1,-1","CONTAINS","#","#")
   arcpy.DeleteField_management("new1",["Join_Count","RORI_1","TARGET_FID"])
   arcpy.CopyFeatures_management("new1",path)
   # Delete unnecessary files
   arcpy.Delete_management(path2)
   arcpy.Delete_management(path3)
   arcpy.Delete_management(path4)
   # Check for the next iteration
   arcpy.CopyFeatures_management(path, "areas_new")
   arcpy.SelectLayerByAttribute_management ("areas_new", "NEW_SELECTION",'[RORI] in (SELECT min( [RORI] ) FROM areas_new)')
   cursor = arcpy.SearchCursor("areas_new")
   for row in cursor:
      dv =  row.getValue("RORI")
   del cursor, row

else :
   del dv
   arcpy.CopyFeatures_management("areas_new",path)
   print "K-anonymized areas are created."

# Finish Process
arcpy.Delete_management(path2)
arcpy.RefreshCatalog(workspace)

print "Process completed."


      
      

