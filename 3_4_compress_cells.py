# Flatten navigable space to one voxel thick layer
# For walking and driving actors

# May 2016 - Martijn Koopman
 
# Input
idi = self.GetInput()
dims = idi.GetDimensions()
numTuples = dims[0]*dims[1]*dims[2]
cellsArr = idi.GetPointData().GetArray('cell_id')
typesArr = idi.GetPointData().GetArray('cell_type')
sizesArr = idi.GetPointData().GetArray('cell_size')

# Output
ido = self.GetOutput() 

outCellsArr = vtk.vtkTypeUInt32Array()
outCellsArr.SetName('cell_id')
outCellsArr.SetNumberOfComponents(1)
outCellsArr.SetNumberOfTuples(numTuples)

outTypesArr = vtk.vtkUnsignedCharArray()
outTypesArr.SetName('cell_type')
outTypesArr.SetNumberOfComponents(1)
outTypesArr.SetNumberOfTuples(numTuples)

outSizesArr = vtk.vtkTypeUInt32Array()
outSizesArr.SetName('cell_size')
outSizesArr.SetNumberOfComponents(1)
outSizesArr.SetNumberOfTuples(numTuples)

# Copy old values
for i in range(0, numTuples):
    outCellsArr.SetValue(i, 0)
    outTypesArr.SetValue(i, 0)
    outSizesArr.SetValue(i, 0)

#  Utility functions
def GetArrValue(arr, pos):
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return 0
    else:
        i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
        return arr.GetValue(i)

def SetArrValue(arr, pos, val):
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return
    i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
    arr.SetValue(i, val)
        
# Flatten cells
cell_voxels = {}
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):
            pos = (x,y,z)
            cell_id = GetArrValue(cellsArr, pos)
            cell_id_underneath = GetArrValue(cellsArr, (x,y,z-1))
            cell_type = GetArrValue(typesArr, pos)
            
            if cell_id > 0 and cell_id_underneath == 0:
                SetArrValue(outCellsArr, (x,y,z), cell_id)
                SetArrValue(outTypesArr, (x,y,z), cell_type)
                SetArrValue(outSizesArr, (x,y,z), 0)
                if not cell_id in cell_voxels:
                    cell_voxels[cell_id] = [pos]
                else:
                    cell_voxels[cell_id].append(pos)                    
# Compute new sizes
cell_sizes = {}
for cell_id in cell_voxels:
    voxels = cell_voxels[cell_id]
    cell_sizes[cell_id] = len(voxels)
    
    for voxel in voxels:
        SetArrValue(outSizesArr, voxel, len(voxels))
              
ido.GetPointData().AddArray(outCellsArr)
ido.GetPointData().AddArray(outTypesArr)
ido.GetPointData().AddArray(outSizesArr)