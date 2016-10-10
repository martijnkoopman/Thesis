# Extract voxels just above horizontal surfaces

# May 2016 - Martijn Koopman

# ToDo: Clean code; pass variable dims to function GetArrValue() and SetArrValue() as arguments

idi = self.GetInput()
dims = idi.GetDimensions()
numTuples = dims[0]*dims[1]*dims[2]
maxDim = max(dims)

# Read input array
arr = idi.GetPointData().GetScalars()

# Create horizontal surface array 
horizSurfArr = vtk.vtkUnsignedCharArray()
horizSurfArr.SetName('horiz_surface')
horizSurfArr.SetNumberOfComponents(1)
horizSurfArr.SetNumberOfTuples(numTuples)

# Utility functions
def GetArrValue(arr, pos):
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return 0
    else:
        i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
        return arr.GetValue(i)

def SetArrValue(arr, pos, val):
    i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
    arr.SetValue(i, val)

# Iterate volume
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):
            # Check for empty space voxel with a ground voxel underneath 
            if GetArrValue(arr, (x,y,z)) == 0 and GetArrValue(arr, (x,y,z-1)) > 0:
                SetArrValue(horizSurfArr, (x,y,z), 1)
            else:
                SetArrValue(horizSurfArr, (x,y,z), 0)

# Assign horizontal surface array
ido = self.GetOutput() 
ido.GetPointData().SetScalars(horizSurfArr) 