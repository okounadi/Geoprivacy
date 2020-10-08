# Name: Adaptive Voronoi Masking
# Description: Displacing points to Voronoi segments within the SKApoly (with exceptions), and then displacing to street intersections.
# Author: Fiona Polzin, f.s. polzin@students .uu.nl, July 2020
# Reference: Polzin, Fiona (2020). Adaptive Voronoi Masking: A method to protect confidential discrete spatial data
# (https://studenttheses.library.uu.nl/search.php?m=course&amp;course=Geographical%20Information%20Management%20and%20Applications%20%28GIMA%29&amp;language=nl).
# MSc Thesis, GIMA. Geographical Information Management and Applications. University of Utrecht/ TU Delft/ Wageningen University/ University of Twente.


# The external and internal variables must be set by the user.
# Code can be executed in ArcMAP 10. x and ArcGIS Pro .
# ----------------------------------------------------------------------
# Import system modules
import arcpy

# ------------------------------------------
# EXTERNAL variables to be inputed by user
workspace = r""
# User determines the local variables of the point case file
PointFile = ""
BlockFile = ""
StreetFile = ""
SearchRadius = " 100000 Meters "

# ---------------------------------------------
# Step 1: Find points for VM
pointsJoin = " points_join "
pointsForVM = " Points_VM "
pointsNoVM = " Points_No_VM "
# Step 2: Create Thiessen and split ( Union ) them based on blocks
VoronoiPolygon = " VoronoiPolygon "
VoronoiUnion = " VoronoiPoly_Union "
# Step 3: Now , snap the pointsForVM to the closest edge of their corresponding Voronoi_clip polygon or the SKApoly segment
# Step 4: Find the polygons with only data point
blocks = " Blocks "
# Step 5: Create one random points ( points not for VM )
RandomPoints = " RandomPoints "
# Step 6: Merge StreetFile
MergedStreets = " UnsplitStreets "
# Step 7: Find street intersections
Intersection = " Intersection "
# Step 8: Move pointsForVM to closest intersection
# Step 9: Move pointsNoVM to closest intersection
# Step 10: merge pointsForVM and pointsNoVM to a new layer
AVM = " AVM_points "

# --------------------------------------------
# Set workspace
arcpy . env . workspace = workspace
arcpy . env . overwriteOutput = True # controls whether the algorithm will replace any present output automatically
arcpy . env . addOutputsToMap = True # add output to map automatically

# ----------------------------------------------
# Step 1 - Find points for VM and not for VM
arcpy . analysis . SpatialJoin ( PointFile , BlockFile , " points_join ", " JOIN_ONE_TO_ONE "," KEEP_ALL ", )

arcpy . analysis . Statistics (" points_join ", " stat ", "id COUNT ", "id")
arcpy . management . CopyFeatures ( BlockFile , " Blocks ")
arcpy . JoinField_management (" Blocks ", "id", " stat ", "ID", " COUNT_ID ")

arcpy . SelectLayerByAttribute_management (" Blocks ", selection_type =" NEW_SELECTION ",where_clause ='" COUNT_ID " = 1')

arcpy . SelectLayerByLocation_management ( in_layer = PointFile , overlap_type =" INTERSECT "
, select_features =" Blocks ", search_distance ="", selection_type =" NEW_SELECTION ",invert_spatial_relationship =" NOT_INVERT ")

arcpy . SelectLayerByLocation_management ( in_layer = PointFile , overlap_type =" INTERSECT "
, select_features =" Blocks ", search_distance ="", selection_type =" NEW_SELECTION ",invert_spatial_relationship =" NOT_INVERT ")

arcpy . CopyFeatures_management ( PointFile , " Points_No_VM ")

arcpy . SelectLayerByLocation_management ( in_layer = PointFile , overlap_type =" INTERSECT "
, select_features =" Blocks ", search_distance ="", selection_type ="SWITCH_SELECTION ", invert_spatial_relationship =" NOT_INVERT ")

arcpy . CopyFeatures_management ( PointFile , " Points_VM ")

arcpy . SelectLayerByAttribute_management (" Blocks ", selection_type =" CLEAR_SELECTION ")
arcpy . SelectLayerByAttribute_management ( PointFile , selection_type =" CLEAR_SELECTION ")

# -------------------------------------------
# Step 2 - Create Thiessen and split ( Union ) them based on blocks
arcpy . env . extent = BlockFile
arcpy . CreateThiessenPolygons_analysis ( pointsForVM , VoronoiPolygon , " ALL")
arcpy . Union_analysis ([ VoronoiPolygon , BlockFile ], VoronoiUnion )


# --------------------------------------------
# Step 3 - Snap data points to closest segment (Voronoi or SKApoly)
inFeature = pointsForVM
snap_feature = VoronoiUnion
snap_Type = " EDGE "
snap_Distance = SearchRadius

arcpy . Snap_edit ( inFeature , [[ snap_feature , snap_Type , snap_Distance ]])

# ----------------------------------------------
# Step 4 - Find all polygons which contain data points not transferred by VM
arcpy . SelectLayerByAttribute_management (" Blocks ", selection_type =" NEW_SELECTION ",
where_clause ='" COUNT_ID " = 1')

# ----------------------------------------------
# Step 5 - Create random points ( for points no VM)
arcpy . CreateRandomPoints_management ( out_path = workspace , out_name = RandomPoints ,
constraining_feature_class =" Blocks ", number_of_points_or_field =" COUNT_ID ")
arcpy . SelectLayerByAttribute_management (" Blocks ", selection_type =" CLEAR_SELECTION ")


# ------------------------------ Move all data points to closest intersection
----------------------------------------------
# Step 6 - To assure that the input streetfile is not divided into multiple substreets causing various streets to intersect but do not produce " cross " street intersections , streets will be " unsplitted "
in_features = StreetFile
out_feature_class = MergedStreets

# Run UnsplitLine
arcpy . UnsplitLine_management ( in_features , out_feature_class )

# ---------------------------------------------
# Step 7 - Use " Intersect "- tool to find street intersection and receive output as points
in_features = MergedStreets
out_feature_class = Intersection

arcpy . Intersect_analysis ( in_features , out_feature_class , "", "", " POINT ")

# ---------------------------------------------
# Step 8 - Move pointsForVM to closest intersection
infc = pointsForVM
snapClass = Intersection
snapType = " VERTEX "
snapDistance = SearchRadius
arcpy . Snap_edit (infc , [[ snapClass , snapType , snapDistance ]])

# ---------------------------------------------
# Step 9 - Move " Points_Not_For_VM " to closest intersection
in_fc = RandomPoints
snapFeature = Intersection
snapChar = " VERTEX "
snapWidth = SearchRadius
arcpy . Snap_edit (in_fc , [[ snapFeature , snapChar , snapWidth ]])

# -----------------------------------------------
# Step 10 - Merge all masked data points into a new layer
arcpy . Merge_management (' RandomPoints ; Points_VM ', AVM , "")
print (" Program successfully finished : AVM points are created ")
