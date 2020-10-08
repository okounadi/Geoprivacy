# Adaptive Geographical Masking

## Introduction

This repository contains a set of codes to perform adaptive geographical masking.

Geographical masking alters the precision or accuracy of geographical data for the purpose of anonymization.

In adaptive geographical masking the degree of &quot;alteration&quot; or &quot;masking&quot; is not a fixed value but is adapted based on the density of the underlying risk of re-identification information (RORI). Lower density requires higher masking degree and vice versa.

RORI can be the number of people, number of households, number of residential addresses, or other. If RORI is not considered and applied in geographical masking, then data linkage can occur between a private-sensitive-confidential information and the RORI. Such linkage could lead to re-identification.

## To apply the codes you will need the following datasets:
1. _Original data_: a point shapefile with the original locations of private-sensitive-confidential information.

2. _RORI polygons_: a polygon shapefile with the attribute RORI (e.g., postcodes with the number of households in each polygon)

3. _Streets_: a line shapefile that represents the road network of the study area. This is needed only for the Voronoi Masking Method.


## A brief description of the codes

### First, create spatial k-anonymized polygons - SKApoly (three options below):
1. _AdaptiveElimination_: Creates spatial K-anonymized polygons by eliminating irregular polygons

2. _AdaptiveDissolvingID_: Creates spatial K-anonymized polygons by dissolving regular polygons

3. _AdaptiveDissolvingMin_: Creates spatial K-anonymized polygons by dissolving regular polygons; iteration selects polygons based on the minimum RORI value

### Second, mask original data (three options below):
4. _PointAggregation_: original points are displaced to the centroid of their corresponding SKApoly.

5. _RandomPerturbation_: original points are randomly displaced (distance + direction) within their corresponding SKApoly.

6. _AdaptiveVoronoiMasking_: original data are displaced to the closest segment of their corresponding Voronoi polygon which is laying within their corresponding SKApoly. Two exceptions apply. If a Voronoi segment lies outside its SKApoly, the point is displaced to the boundary of the SKApoly. If there is only one point within the SKApoly, then it is randomly displaced within the SKApoly. Last, displaced points are further displaced to the closest street intersection.

## Further information
- The codes are written in Python and use the ArcPy package: https://pro.arcgis.com/en/pro-app/arcpy/get-started/what-is-arcpy-.htm
- Data should be in a shapefile format: https://desktop.arcgis.com/en/arcmap/10.3/manage-data/shapefiles/what-is-a-shapefile.htm 
- Data should additonaly be copied into a personal database (.mdb): https://desktop.arcgis.com/en/arcmap/latest/manage-data/administer-file-gdbs/create-personal-geodatabase.htm


## References

Kounadi, O., &amp; Leitner, M. (2016). [Adaptive areal elimination (AAE): A transparent way of disclosing protected spatial datasets](https://www.sciencedirect.com/science/article/pii/S0198971516300047). _Computers, Environment and Urban Systems_, _57_, 59-67

Polzin, Fiona (2020) [Adaptive Voronoi Masking: A method to protect confidential discrete spatial data](https://studenttheses.library.uu.nl/search.php?m=course&amp;course=Geographical%20Information%20Management%20and%20Applications%20%28GIMA%29&amp;language=nl). MSc Thesis, GIMA – Geographical Information Management and Applications. University of Utrecht – TU Delft – Wageningen University – University of Twente.
