# Name: Adaptive Dissolving
# Description: Dissolving polygons until all polygons have attribute values that are equal or greater than a minimum value.
# Author: O. Kounadi, 6/03/2015
# Reference: This code is part of a code written for an adaptive geographical masking method that is published in:  
# Kounadi, O., & Leitner, M. (2016). Adaptive areal elimination (AAE): A transparent way of disclosing protected spatial datasets.
# Computers, Environment and Urban Systems, 57, 59-67.

# Copy polygon file as "areas" to a new personal geodatabase
# Working output will be saved in the geodatabase
# --------------------------------------------

# Set workspace variable
workspace = r"D:\mask.mdb"

# Set disclosure value 
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

# Define variable to check for disclosure value
arcpy.CopyFeatures_management(path, "areas_new")
arcpy.SelectLayerByAttribute_management ("areas_new", "NEW_SELECTION",'[RORI] in (SELECT min( [RORI] ) FROM areas_new)')
check1 = arcpy.SearchCursor("areas_new")
for row in check1:
   dv =  row.getValue("RORI")
del check1, row

# Dissolving process
while dv < Ka :
   arcpy.SelectLayerByLocation_management("areas_new","SHARE_A_LINE_SEGMENT_WITH","","","NEW_SELECTION")
   arcpy.Dissolve_management("areas_new","new","#","RORI SUM")
   arcpy.AddField_management("new","RORI", "LONG")
   arcpy.CalculateField_management('new', 'RORI', '[SUM_RORI]', 'VB', '#')
   arcpy.DeleteField_management("new","SUM_RORI")
   arcpy.SelectLayerByAttribute_management("areas_new","CLEAR_SELECTION")                          
   arcpy.Update_analysis("areas_new","new","new1")
   arcpy.CopyFeatures_management("new1", path)
   arcpy.Delete_management(path2)
   arcpy.Delete_management(path3)
   arcpy.Delete_management(path4)
   arcpy.CopyFeatures_management(path, "areas_new")
   arcpy.SelectLayerByAttribute_management ("areas_new", "NEW_SELECTION",'[RORI] in (SELECT min( [RORI] ) FROM areas_new)')
   cursor = arcpy.SearchCursor("areas_new")
   for row in cursor:
      dv =  row.getValue("RORI")
   del cursor, row
     
else :
   arcpy.CopyFeatures_management("areas_new",path)
   print "K-anonymized areas are created."
   

# Finish Process
arcpy.Delete_management(path2)
arcpy.RefreshCatalog(workspace)

print "Process completed."

