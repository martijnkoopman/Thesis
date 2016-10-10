# Dilate 3D horizontal

# May 2016 - Martijn Koopman

# ToDo: Clean code; pass variable dims to function GetArrValue() and SetArrValue() as arguments

# User parameters
radius = 2              # 2 * 10 cm on both sides + 10 cm in middle = 50cm 
vertical_extrusion = 1  # 19 * 10 cm = 190 cm
 
# Input
idi = self.GetInput()
dims = idi.GetDimensions()
numTuples = dims[0]*dims[1]*dims[2]
input_arr = idi.GetPointData().GetScalars()

intermediate_arr = vtk.vtkTypeUInt32Array()
intermediate_arr.SetName('intermediate')
intermediate_arr.SetNumberOfComponents(1)
intermediate_arr.SetNumberOfTuples(numTuples)

# Output
ido = self.GetOutput() 
output_arr = vtk.vtkTypeUInt32Array()
output_arr.SetName('scalar')
output_arr.SetNumberOfComponents(1)
output_arr.SetNumberOfTuples(numTuples)

# Copy input array
for i in range(0, numTuples):
    if input_arr.GetValue(i) == 0:
        output_arr.SetValue(i,0)
        intermediate_arr.SetValue(i,0)
    else:
        output_arr.SetValue(i,1)
        intermediate_arr.SetValue(i,1)

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
        
        
# Dilate vertically
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):

            if GetArrValue(input_arr, (x,y,z)) > 0:
                # Found an obstacle -> create vertical buffer
                for z_offset in range(1, vertical_extrusion+1):                
                    SetArrValue(intermediate_arr, (x, y, z-z_offset), 1)
        
# Dilate horizontally
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):

            if GetArrValue(intermediate_arr, (x,y,z)) > 0:
                # Create horizontal buffer
                for x_offset in range(-radius, radius+1):
                    x_n = x + x_offset
                    for y_offset in range(-radius, radius+1):
                        y_n = y + y_offset

                        # Check if neighbour is within radius of circle
                        # X^2 + Y^2 <= R^2
                        if ((x_offset*x_offset) + (y_offset*y_offset)) <= (radius*radius):                    
                        
                            # Create buffer voxel
                            SetArrValue(output_arr, (x_n, y_n, z), 1)

ido.GetPointData().SetScalars(output_arr)