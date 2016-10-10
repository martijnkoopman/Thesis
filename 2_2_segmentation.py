# Segment ground voxels

# May 2016 - Martijn Koopman

# ToDo: Clean code; Pass variable dims to function GetArrValue() and SetArrValue() as arguments.
# ToDo: Clean code; Use for loop to iterate over neighbours. 

from collections import deque

# User defined parameter:
vertical_footspan = 1       # Number of voxels that can be overspan vertically by one footstep

# Read input
idi = self.GetInput()
dims = idi.GetDimensions()
numTuples = dims[0]*dims[1]*dims[2]
arr = idi.GetPointData().GetScalars()

# Create output
ido = self.GetOutput()
segArr = vtk.vtkTypeUInt32Array()
segArr.SetName('segments')
segArr.SetNumberOfComponents(1)
segArr.SetNumberOfTuples(numTuples)

# Clear output
for i in range(numTuples):
    segArr.SetValue(i,0)

########## Utility functions ##########

def GetArrValue(arr, pos):
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return 0
    else:
        i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
        return arr.GetValue(i)
        
def SetArrValue(arr, pos, val):
    i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
    arr.SetValue(i, val)

####################
    
segment_num = 1

# Convert vtkImageData to Python dictionary
volume = {}
for z in range(dims[2]):
    for y in range(dims[1]):
        for x in range(dims[0]):
            pos = (x,y,z)
            if GetArrValue(arr, pos) > 0:
                volume[pos] = 1
                
segmentVolume = {}

# Find lowest occurence of ground voxel
pos_lowest = False
for pos in volume:
    if not pos_lowest or pos[2] < pos_lowest[2]:
        pos_lowest = pos
pos = pos_lowest
                
while pos:
    # Start region growing!
    queue = deque([pos]) 
    while queue:

        pos = queue.popleft()

        if pos in volume:
            # Remove ground voxel
            del volume[pos]             # Same position is deleted twice! probably

            # Add voxel to segment
            segmentVolume[pos] = segment_num
        
            ##### Check south neighbours #####
            
            # Check if those neighbours are unvisited
            visited = False
            for z_offset in range(-vertical_footspan, vertical_footspan+1):
                pos_n = (pos[0], pos[1]-1, pos[2]+z_offset)                         # Change
                if pos_n in segmentVolume:
                    visited = True
            
            if not visited:
                # Check horizontal and lower neighbours
                for z_offset in range(vertical_footspan+1):
                    pos_n = (pos[0], pos[1]-1, pos[2]-z_offset)                     # Change 
                    if pos_n in volume:
                        queue.append(pos_n)
                        visited = True
                        break
            
            if not visited:
                # Check higher neighbours
                for z_offset in range(1, vertical_footspan+1):
                    pos_n = (pos[0], pos[1]-1, pos[2]+z_offset)                     # Change 
                    if pos_n in volume:
                        queue.append(pos_n)
                        visited = True
                        break
                        
            # ##### Check west neighbours #####
            
            # Check if those neighbours are unvisited
            visited = False
            for z_offset in range(-vertical_footspan, vertical_footspan+1):
                pos_n = (pos[0]-1, pos[1], pos[2]+z_offset)                         # Change
                if pos_n in segmentVolume:
                    visited = True
            
            if not visited:
                # Check horizontal and lower neighbours
                for z_offset in range(vertical_footspan+1):
                    pos_n = (pos[0]-1, pos[1], pos[2]-z_offset)                     # Change 
                    if pos_n in volume:
                        queue.append(pos_n)
                        visited = True
                        break
            
            if not visited:
                # Check higher neighbours
                for z_offset in range(1, vertical_footspan+1):
                    pos_n = (pos[0]-1, pos[1], pos[2]+z_offset)                     # Change 
                    if pos_n in volume:
                        queue.append(pos_n)
                        visited = True
                        break
                        
            # ##### Check east neighbours #####
            
            # Check if those neighbours are unvisited
            visited = False
            for z_offset in range(-vertical_footspan, vertical_footspan+1):
                pos_n = (pos[0]+1, pos[1], pos[2]+z_offset)                         # Change
                if pos_n in segmentVolume:
                    visited = True
            
            if not visited:
                # Check horizontal and lower neighbours
                for z_offset in range(vertical_footspan+1):
                    pos_n = (pos[0]+1, pos[1], pos[2]-z_offset)                     # Change 
                    if pos_n in volume:
                        queue.append(pos_n)
                        visited = True
                        break
            
            if not visited:
                # Check higher neighbours
                for z_offset in range(1, vertical_footspan+1):
                    pos_n = (pos[0]+1, pos[1], pos[2]+z_offset)                     # Change 
                    if pos_n in volume:
                        queue.append(pos_n)
                        visited = True
                        break
                        
            # ##### Check north neighbours #####
            
            # Check if those neighbours are unvisited
            visited = False
            for z_offset in range(-vertical_footspan, vertical_footspan+1):
                pos_n = (pos[0], pos[1]+1, pos[2]+z_offset)                         # Change
                if pos_n in segmentVolume:
                    visited = True
            
            if not visited:
                # Check horizontal and lower neighbours
                for z_offset in range(vertical_footspan+1):
                    pos_n = (pos[0], pos[1]+1, pos[2]-z_offset)                     # Change 
                    if pos_n in volume:
                        queue.append(pos_n)
                        visited = True
                        break
            
            if not visited:
                # Check higher neighbours
                for z_offset in range(1, vertical_footspan+1):
                    pos_n = (pos[0], pos[1]+1, pos[2]+z_offset)                     # Change 
                    if pos_n in volume:
                        queue.append(pos_n)
                        visited = True
                        break
                    
    # End of queue
    
    segment_num = segment_num + 1

    # Find next occurrence of ground voxel
    pos_lowest = False
    for pos in volume:
        if not pos_lowest or pos[2] < pos_lowest[2]:
            pos_lowest = pos
    pos = pos_lowest
    
    
# Convert segmentVolume to vtkImageData

# Copy from dictionary
for pos in segmentVolume:
    SetArrValue(segArr, pos, segmentVolume[pos])
                    
ido.GetPointData().SetScalars(segArr) 
                    
                