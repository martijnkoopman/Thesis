# MSc Geomatics thesis: 3D path-finding in a voxelized model of an indoor environment 

## Synopsis
This repository contains 14 programmable filters for [ParaView](http://www.paraview.org). These filters should be executed in consequtive order to enable hierarchical path-finding in a model of an indoor environment. The path-finding method supports different kinds of actors by incorporating their size (diameter & height) and mode of locomotion (drive, walk, fly). The input model is decomposed into cells and a graph is derived from this cell decomposition. Path-finding is then performed on two levels: first in the graph and then in the cell decomposition. 

### Input model

The input model must be of type vtkImageData (file extension .vtk or .vti). Empty space has value 0 and non-empty space has value > 0.

## Usage

The entire methodology involves 4 steps. The first 3 steps have to be performed only once while the 4th step - the actual path-finding - can be performed multiple times.

1. Dilation the input model
2. Semantic labelling of the dilated model
3. Cell-and-portal graph (CPG) generation
4. Hierarchical path-finding


![Script execution order](doc/flow.png)


### 1. Dilation of the input model
The size of the actor is incorporated by dilating the input model.
The input model is dilated by creating a horizontal buffer around the geometry and extruding the geometry downwards. 
The radius of the buffer should be half the diameter of the actor and the downward extrusion should be the height of the actor - 1.

Define variables: *radius* and *vertical_extrusion*

Run script: *1_dilate.py*

### 2. Semantic labelling of the dilated model
Distinction between the three different modes of locomotion (drive, walk, fly) is made by constructing the correct navigable spaces.
Driving actors are only capable of navigating over flat floors, walking actors are also capable of navigating over stairs and flying actors are also capable of navigating over obstacles. Next to that, walking and driving actors are bound to a ground surface while a flying actor can freely move up and down. It is therefore required that the space is semantically labelled by one of the following classes: floor (1), stairs (2) or obstacle (3).

Semantically labelling of the dilated model involves 5 steps:

1. Extraction of horizontal surfaces
2. Segmentation of horizontal surfaces
3. Selection of floor segment
4. Labelling stairs by slope estimation
5. Upwards propagation of labels

#### 2.1. Extraction of horizontal surfaces
Horizontal surfaces are extracted from the model by selecting all non-empty space voxels that have an empty space voxel above it. Only these voxels are required for the semantic labelling process.

Run script: *2_1_horizontal_surfaces.py* 

#### 2.2. Segmentation of horizontal surfaces
The horizontal surfaces are segmented using a flood-fill algorithm. This flood-fill algorithm starts at the voxel with the lowest elevation and then expands in all directions. Adjacent voxels are assigned to the same segment whereas disconnected voxels are assigned to new segments. The flood-fill algorithm is capable of expanding upwards and downwards by a given predefined number (vertical footspan). This ensures that the floors and stairs are assigned to the same segment.

* Define parameter: *vertical footspan*
* Run script: *2_2_segmentation.py* 

#### 2.3. Selection of floor segment
One segment (in most situations the first one) embodies the floors and stairs. This segment is labelled floor and all other segments are labelled obstacle.

* Define parameters: *segment number* 
* Run script: *2_3_floor_labelling.py*

#### 2.4. Labelling stairs by slope estimation
Distinguishing between floor and stairs is done by computing the slope of the surface voxels. The slope is estimated by fitting a plane through the neighbourhood of a voxel. The angle between the normal vector of this plane and a vertical up vector gives the slope. All voxels with a slope above a given threshold are labelled stairs.

* Define parameters: *neighbourhood radius*, *maximum surface slope*
* Run script: *2_4_stairs_labelling.py*

#### 2.5. Upwards propagation of labels
All horizontal surfaces are now labelled as one of the three classes: floor, stairs or obstacle. These labels are propagated upwards to also label the empty space above the horizontal surfaces.

* Run script: *2_5_propagate_labels_up.py*

### 3. Cell-and-portal graph (CPG) generation
The methodology for generating cells and detecting portals is an adaptation of [Volumetric Cell-and-Portal Generation](https://hal.inria.fr/inria-00510188/file/mcp.pdf).
The methodology for constructing the graph is an adaptation of [Near Optimal Hierarchical Path-Finding](https://webdocs.cs.ualberta.ca/~mmueller/ps/hpastar.pdf).

#### 3.1. Assigning infinity to empty space
Value infinity (a very large number) is assigned to empty space voxels and 0 to non-empty space voxels. This configuration is required for the following distance transformation.

* Run script: *3_1_infinity.py*

#### 3.2. Distance transformation
A distance field is computed using [Chamfer distance transformation](https://studentportalen.uu.se/uusp-filearea-tool/download.action?nodeId=214320&toolAttachmentId=64777). Each location in the distance field indicates the
distance to the nearest geometry.

* Run script: *3_2_distance_field.py*

#### 3.3. Generating cells
The distance field is segmented into cells using a watershed transformation. The semantic model is also used in the watershed transformation. Newly created cells receive the same semantic label as the very first voxel of the cell and adjacent voxels may only be appended to the cell if they have the same semantic label.

* Set inputs: *distance field*, *semantic model*
* Run script: *3_3_cells*

#### 3.4. Compressing cells
The cells should represent parts of navigable space. Since walking and driving actor are not able to fly, are these cells compressed downwards to a thickness of 1 voxel. This step should be skipped for flying actors.

* Run script: *3_4_compress_cells*

#### 3.5. Merging cells

* Define parameters: *vertical footspan*, *allowed semantic classes*
* Run script: *3_5_merge_cells*

#### 3.6. Detecting portals

* Define parameters: *allowed semantic classes*
* Run script: *3_6_portals*

### 3.7. Graph generation

* Define parameters: *vertical footspan*
* Run script: *3_7_graph*

### 4. Hierarchical path-finding

* Define parameters: 
* Set inputs: graph, cells, start position (ProbeLocation), end position (ProbeLocation)
* Run script: *4_path*
