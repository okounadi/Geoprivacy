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

# Exclude unnecessary features from the dissolving process 
arcpy.CopyFeatures_management(path, "areas_new")
arcpy.SelectLayerByAttribute_management ("areas_new", "NEW_SELECTION",'[RORI]>= 5')
arcpy.CalculateField_management("areas_new","ID",'NULL')
arcpy.SelectLayerByAttribute_management("areas_new","CLEAR_SELECTION")

# Define variable to check for disclosure value
arcpy.SelectLayerByAttribute_management ("areas_new", "NEW_SELECTION",'[RORI] in (SELECT min( [RORI] ) FROM areas_new)')
check1 = arcpy.SearchCursor("areas_new")
for row in check1:
   dv =  row.getValue("RORI")
del check1, row

# Dissolving process 
while  dv < Ka :
   arcpy.SelectLayerByAttribute_management ("areas_new", "NEW_SELECTION",'[ID] in (SELECT min( [ID] ) FROM areas_new)')
   arcpy.SelectLayerByLocation_management("areas_new","SHARE_A_LINE_SEGMENT_WITH","","","NEW_SELECTION")
   # Select neighbors until min DV is reached
   list = []
   check2 = arcpy.SearchCursor("areas_new")
   for row in check2:
      dv1 = row.getValue("RORI")
      list.append (dv1)      
      dv2 = sum(list)
   del check2,list,row, dv1
   while  dv2 < Ka:
      arcpy.SelectLayerByLocation_management("areas_new","SHARE_A_LINE_SEGMENT_WITH","","","ADD_TO_SELECTION")
      list1 = []
      check3 = arcpy.SearchCursor("areas_new")
      for row in check3:
         dv1 = row.getValue("RORI")
         list1.append (dv1)      
         dv2 = sum(list1)
      del check3,list1,row, dv1
   del dv2
   # Dissolve selected features
   arcpy.Dissolve_management("areas_new","new","#","RORI SUM;ID MIN")
   arcpy.AddField_management("new","RORI", "LONG")
   arcpy.AddField_management("new","ID", "LONG")
   arcpy.CalculateField_management('new', 'RORI', '[SUM_RORI]', 'VB', '#')
   arcpy.CalculateField_management('new', 'ID', '[MIN_ID]', 'VB', '#')
   arcpy.DeleteField_management("new","SUM_RORI")
   arcpy.DeleteField_management("new","MIN_ID")
   arcpy.SelectLayerByAttribute_management("areas_new","CLEAR_SELECTION")                          
   arcpy.Update_analysis("areas_new","new","new1")
   arcpy.CopyFeatures_management("new1", path)
   # Delete unnecessary files
   arcpy.Delete_management(path2)
   arcpy.Delete_management(path4)
   arcpy.Delete_management(path3)
   # Exlude previous feature from next iteration 
   arcpy.CopyFeatures_management(path, "areas_new")
   arcpy.SelectLayerByAttribute_management ("areas_new", "NEW_SELECTION",'[ID] in (SELECT min( [ID] ) FROM areas_new)')
   arcpy.CalculateField_management("areas_new","ID",'NULL')
   # Check for the next iteration
   arcpy.SelectLayerByAttribute_management ("areas_new", "NEW_SELECTION",'[RORI] in (SELECT min( [RORI] ) FROM areas_new)')
   check4 = arcpy.SearchCursor("areas_new")
   for row in check4:
      dv =  row.getValue("RORI")
   del check4, row
   
else :
   del dv
   print "K-anonymized areas are created."
   arcpy.CopyFeatures_management("areas_new",path)

# Finish Process
arcpy.Delete_management(path2)
arcpy.RefreshCatalog(workspace)

print "Process completed."
      

