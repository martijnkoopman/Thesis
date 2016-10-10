# MSc Geomatics thesis: 3D path-finding in a voxelized model of an indoor environment 

## Synopsis
This repository contains 14 programmable filters for [ParaView](http://www.paraview.org). These filters enable hierarchical path-finding in a model of an indoor environment. This code is the implementation of my thesis research.

### Required input model

The input model has to be a vtkImageData (file extension .vtk or .vti). Empty space has value 0 and non-empty space has value > 0.

## Steps

1. Dilation the input model
2. Semantical enrichment the input model
3. Generation of the cell-and-portal graph
4. Hierarchical path-finding

### 1. Dilation of the input model
The input model is dilated by creating a horizontal buffer around the geometry and extruding the geometry downwards.
The radius of the horizontal buffer and amount of downward extrusion has to be defined by the user. The radius of the buffer should be half the width of the actor and the downward extrusion should be the height of the actor - 1.

Define variables *radius* and *vertical_extrusion* in script *1_dilate.py* and run the script.

### 2. Semantical enrichment of the input model

The dilated model is semantically enriched with the following classes: floor (1), stairs (2) or obstacle (3).

This involves 5 steps:

1. Extraction of horizontal surfaces
2. Segmentation of horizontal surfaces
3. Selection of floor segment
4. Labelling stairs by slope estimation
5. Upwards propagation of labels

#### 2.1. Extraction of horizontal surfaces
Run script: *2_1_horizontal_surfaces.py*

#### 2.2. Segmentation of horizontal surfaces
Run script: *2_2_segmentation.py*

#### 2.3. Selection of floor segment
Run script: *2_3_floor_labelling.py*

#### 2.4. Labelling stairs by slope estimation
Run script: *2_4_stairs_labelling.py*

#### 2.5. Upwards propagation of labels
Run script: *2_5_propagate_labels_up.py*

## 3. Generation of the cell-and-portal graph
...
