# Propagate labels upwards to label the empty space

# May 2016 - Martijn Koopman

# ToDo: Clean code; Pass variable dims to function GetArrValue() and SetArrValue() as arguments.

# Read input
idi = self.GetInput()
dims = idi.GetDimensions()
numTuples = dims[0]*dims[1]*dims[2]
arr = idi.GetPointData().GetScalars()

# Create output
ido = self.GetOutput()
output_arr = vtk.vtkTypeUInt32Array()
output_arr.DeepCopy(arr)
output_arr.SetName('ImageScalars')

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
    
#perform pass
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):
        
            n = GetArrValue(output_arr, (x, y, z-1))
            if GetArrValue(output_arr, (x,y,z)) ==  0:
                SetArrValue(output_arr, (x,y,z), n)
                    
ido.GetPointData().SetScalars(output_arr)