# Name: Adaptive Voronoi Masking
# Description: Displacing points to Voronoi segments within the SKApoly (with exceptions), and then displacing to street intersections.
# Author: Fiona Polzin, f.s. 
# Reference: Adaptive Voronoi Masking: A Method to Protect Confidential Discrete Spatial Data. https://drops.dagstuhl.de/opus/volltexte/2021/14760/pdf/LIPIcs-GIScience-2021-II-1.pdf 
# This script is edited by O.Kounadi, ourania.kounadi@univie.ac.at, 2022


#The external and internal variables must be set by the user.
#Code can be executed in ArcMAP10.x and ArcGISPro.
#----------------------------------------------------------------------
#Import system modules
import arcpy

#------------------------------------------
# EXTERNAL variables to be inputed by user
workspace=r".."
# User determines the local variables of the point case file
PointFile=r"..."
BlockFile=r"..."
StreetFile=r".."
SearchRadius= "100000 Meters"

#---------------------------------------------
# Step 1: Find points for VM
pointsJoin="points_join"
pointsForVM="Points_VM"
pointsNoVM="Points_No_VM"
# Step 2: Create Thiessen and split ( Union ) them based on blocks
VoronoiPolygon="VoronoiPolygo"
VoronoiUnion="VoronoiPoly_Unio"
# Step 3: Now , snap the pointsForVM to the closest edge of their corresponding Voronoi_clip polygon or the SKApoly segment
# Step 4: Find the polygons with only data point
# Step 5: Create one random points ( points not for VM )
RandomPoints="RandomPoint"
# Step 6: Merge StreetFile
MergedStreets="UnsplitStrees"
# Step 7: Find street intersections
Intersection="Intersectio"
# Step 8: Move pointsForVM to closest intersection
# Step 9: Move pointsNoVM to closest intersection
# Step 10: merge pointsForVM and pointsNoVM to a new layer
AVM="AVM_point"

#--------------------------------------------
#Set workspace
arcpy.env.workspace=workspace
arcpy.env.overwriteOutput=True#controls whether the algorithm will replace any present output automatically
arcpy.env.addOutputsToMap=True#add output to map automatically

#----------------------------------------------
#Step1-Find points for VM and not for VM
arcpy.analysis.SpatialJoin(PointFile, BlockFile, pointsJoin, 'JOIN_ONE_TO_ONE', 'KEEP_ALL')


arcpy.analysis.Statistics(pointsJoin,"stat","id COUNT","id")
arcpy.management.CopyFeatures(BlockFile,"Blocks")
arcpy.JoinField_management("Blocks","id","stat","ID","COUNT_ID")

arcpy.SelectLayerByAttribute_management("Blocks",selection_type="NEW_SELECTION",where_clause='"COUNT_ID"=1')

arcpy.MakeFeatureLayer_management(pointsJoin, "points_lyr")
arcpy.management.SelectLayerByLocation("points_lyr", "INTERSECT", "Blocks", None, "NEW_SELECTION", "NOT_INVERT")
arcpy.CopyFeatures_management("points_lyr", pointsNoVM)

arcpy.SelectLayerByLocation_management("points_lyr",overlap_type="INTERSECT" ,select_features="Blocks",search_distance="",selection_type="SWITCH_SELECTION",invert_spatial_relationship="NOT_INVERT")

arcpy.CopyFeatures_management("points_lyr",pointsForVM)

arcpy.SelectLayerByAttribute_management("Blocks",selection_type="CLEAR_SELECTION")
arcpy.SelectLayerByAttribute_management("points_lyr",selection_type="CLEAR_SELECTION")

#-------------------------------------------
#Step2-Create Thiessen and split(Union)them based on blocks
arcpy.env.extent=BlockFile
arcpy.CreateThiessenPolygons_analysis(pointsForVM,VoronoiPolygon,"ALL")
arcpy.Union_analysis([VoronoiPolygon,BlockFile],VoronoiUnion)


#--------------------------------------------
#Step3-Snap data points to closest segment(Voronoi or SKApoly)
inFeature = pointsForVM
snap_feature = VoronoiUnion
snap_Type = "EDGE"
snap_Distance = SearchRadius

arcpy.Snap_edit(inFeature, [[snap_feature, snap_Type, snap_Distance]])

#----------------------------------------------
# Step 4 - Find all polygons which contain data points not transferred by VM
arcpy.SelectLayerByAttribute_management("Blocks",selection_type="NEW_SELECTION",where_clause='"COUNT_ID"=1')
arcpy.management.JoinField('Blocks', 'id', 'Points_No_VM', 'id', 'CID') # add CID of no VM points
arcpy.management.AddField('Points_VM','cid_VM')
arcpy.management.CalculateField("Points_VM", "cid_VM", "!CID!", "PYTHON3", '', "TEXT")
arcpy.management.DeleteField('Points_VM', 'CID')

#----------------------------------------------
# Step 5 - Create random points ( for points no VM)
arcpy.CreateRandomPoints_management(out_path=workspace,out_name=RandomPoints,constraining_feature_class="Blocks",number_of_points_or_field="COUNT_ID")
arcpy.management.JoinField(RandomPoints,'CID', 'Blocks', 'FID', 'CID') # add CID info to random points 
arcpy.management.AddField(RandomPoints,'cid_no_VM')
arcpy.management.CalculateField(RandomPoints, "cid_no_VM", "!CID_1!", "PYTHON3", '', "TEXT")
arcpy.management.DeleteField("RandomPoint", "CID;CID_1")
arcpy.SelectLayerByAttribute_management("Blocks",selection_type="CLEAR_SELECTION")


# ------------------------------ Move all data points to closest intersection----------------------------------------------
# Step 6 - To assure that the input streetfile is not divided into multiple substreets causing various streets to intersect but do not produce " cross " street intersections , streets will be " unsplitted "
in_features=StreetFile
out_feature_class=MergedStreets

#Run UnsplitLine
arcpy.UnsplitLine_management(in_features,out_feature_class)

#---------------------------------------------
# Step 7 - Use " Intersect "- tool to find street intersection and receive output as points
in_features=MergedStreets
out_feature_class=Intersection

arcpy.Intersect_analysis(in_features,out_feature_class,"","","POINT")

#---------------------------------------------
# Step 8 - Move pointsForVM to closest intersection
infc=pointsForVM
snapClass=Intersection
snapType="VERTEX"
snapDistance=SearchRadius
arcpy.Snap_edit(infc,[[snapClass,snapType,snapDistance]])

#---------------------------------------------
# Step 9 - Move " Points_Not_For_VM " to closest intersection
in_fc=RandomPoints
snapFeature=Intersection
snapChar="VERTEX"
snapWidth=SearchRadius
arcpy.Snap_edit(in_fc,[[snapFeature,snapChar,snapWidth]])

#-----------------------------------------------
# Step 10 - Merge all masked data points into a new layer
arcpy . Merge_management ('RandomPoint;Points_VM', AVM , "")
arcpy.management.AddField(AVM,'orig_CID')
arcpy.management.CalculateField("AVM_point", "orig_CID", "!cid_VM! + !cid_no_VM!", "PYTHON3", '', "TEXT") 
print (" AVM points are created ")

# Step 11 - Calculate displaced distance - AVM and original points
arcpy.analysis.GenerateOriginDestinationLinks(PointFile, AVM, "AVM_dist", "CID", "orig_CID", "PLANAR", 1, None, "KILOMETERS", "NO_AGGREGATE", None)
print (" Displaced distance calculated, Program successfully finished ")

