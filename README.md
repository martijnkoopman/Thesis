# MSc Geomatics thesis: 3D path-finding in a voxelized model of an indoor environment 

## Synopsis
This repository contains 14 programmable filters for [ParaView](http://www.paraview.org).

## Content

1. Dilation the input model
2. Semantical enrichment the input model
3. Generation of the cell-and-portal graph
4. Hierarchical path-finding

## 1. Dilating the input model
The input model is dilated by creating a horizontal buffer around the geometry and extruding the geometry downwards.
The radius of the horizontal buffer and amount of downward extrusion has to be defined by the user. The radius of the buffer should be half the width of the actor and the downward extrusion should be the height of the actor - 1.

Define variables *radius* and *vertical_extrusion* in script *1_dilate.py* and run script

## 2. Semantical enrichment of the input model

### 2.1. Extract horizontal surfaces

## 3. Generation of the cell-and-portal graph
