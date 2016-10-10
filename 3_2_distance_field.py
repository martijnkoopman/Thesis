# Distance field 3D Chamfer 5x5x5
# Required input volume:
# - Object has value 0
# - Empty space has value infinity (A number greater than the maximum possible distance)

# May 2016 - Martijn Koopman

# ToDo: Clean code; pass variable dims to function GetArrValue() and SetArrValue() as arguments

# Read input
idi = self.GetInput()
dims = idi.GetDimensions()
arr = idi.GetPointData().GetScalars()

# Create output
ido = self.GetOutput()
distArr = vtk.vtkTypeUInt32Array()
distArr.DeepCopy(arr)
distArr.SetName('distance')

# Utility functions
def GetArrValue(arr, pos):
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return 1000000000   # 0
    else:
        i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
        return arr.GetValue(i)

def SetArrValue(arr, pos, val):
    i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
    arr.SetValue(i, val)

def check(x, y, z, dx, dy, dz, v):
    n = GetArrValue(distArr, (x+dx, y+dy, z+dz)) + v
    if GetArrValue(distArr, (x,y,z)) >  n:
        SetArrValue(distArr, (x,y,z), n)

#perform the first (forward) pass
for z in range(dims[2]):
    for y in range(dims[1]):
        for x in range(dims[0]):
            
            # a = 22, b = 31, c = 104, d = 134, e = 147, f = 180	# Old values
			# a = 22, b = 31, c = 38, d = 49, e = 54, f = 66		# New values

            # \|/ Y
            # ->  X
            
            # (z-0)
            #
            # . d . d .
            # d b a b d
            # . a - . .
            # . . . . .
            # . . . . .
                        
            check(x, y, z, -1,  0, 0, 22)   # a
            check(x, y, z,  0, -1, 0, 22)
            check(x, y, z, -1, -1, 0, 31)   # b
            check(x, y, z,  1, -1, 0, 31)
            check(x, y, z, -2, -1, 0, 49)  # d
            check(x, y, z, -1, -2, 0, 49)
            check(x, y, z,  2, -1, 0, 49)
            check(x, y, z,  1, -2, 0, 49)

            # (z-1)
            #
            # f e d e f
            # e c b c e
            # d b a b d 
            # e c b c e
            # f e d e f
            
            check(x, y, z,  0,  0, -1, 22)  # a
            check(x, y, z, -1,  0, -1, 31)  # b
            check(x, y, z,  1,  0, -1, 31)
            check(x, y, z,  0, -1, -1, 31)
            check(x, y, z,  0,  1, -1, 31)
            check(x, y, z, -1, -1, -1, 38) # c
            check(x, y, z, -1,  1, -1, 38)
            check(x, y, z,  1, -1, -1, 38)
            check(x, y, z,  1,  1, -1, 38)
            check(x, y, z, -2,  0, -1, 49) # d
            check(x, y, z,  2,  0, -1, 49)
            check(x, y, z,  0, -2, -1, 49)
            check(x, y, z,  0,  2, -1, 49)
            check(x, y, z, -1, -2, -1, 54) # e
            check(x, y, z, -1,  2, -1, 54)
            check(x, y, z, -2, -1, -1, 54)
            check(x, y, z, -2,  1, -1, 54)
            check(x, y, z,  1, -2, -1, 54)
            check(x, y, z,  1,  2, -1, 54)
            check(x, y, z,  2, -1, -1, 54)
            check(x, y, z,  2,  1, -1, 54)
            check(x, y, z, -2, -2, -1, 66) # f
            check(x, y, z, -2,  2, -1, 66)
            check(x, y, z,  2, -2, -1, 66)
            check(x, y, z,  2,  2, -1, 66)
            
            # (z-2)
            #   f   f
            # f e d e f
            #   d   d
            # f e d e f
            #   f   f
            
            check(x, y, z, -1,  0, -2, 49) # d
            check(x, y, z,  1,  0, -2, 49)
            check(x, y, z,  0, -1, -2, 49)
            check(x, y, z,  0,  1, -2, 49)
            check(x, y, z, -1, -1, -2, 54) # e
            check(x, y, z, -1,  1, -2, 54)
            check(x, y, z,  1, -1, -2, 54)
            check(x, y, z,  1,  1, -2, 54)
            check(x, y, z, -1, -2, -2, 66) # f
            check(x, y, z, -1,  2, -2, 66)
            check(x, y, z, -2, -1, -2, 66)
            check(x, y, z, -2,  1, -2, 66)
            check(x, y, z,  1, -2, -2, 66)
            check(x, y, z,  1,  2, -2, 66)
            check(x, y, z,  2, -1, -2, 66)
            check(x, y, z,  2,  1, -2, 66)
            
#perform the final (backward) pass 
for z in range(dims[2]-1,-1,-1):
    for y in range(dims[1]-1,-1,-1):
        for x in range(dims[0]-1,-1,-1):
        
            # (z+0)
            #
            # . . . . .
            # . . . . . 
            # . . - a .
            # d b a b d
            # . d . d .
        
            check(x, y, z,  1,  0, 0, 22)   # a
            check(x, y, z,  0,  1, 0, 22)
            check(x, y, z,  1,  1, 0, 31)   # b
            check(x, y, z, -1,  1, 0, 31)
            check(x, y, z,  2,  1, 0, 49)  # d
            check(x, y, z,  1,  2, 0, 49)
            check(x, y, z, -2,  1, 0, 49)
            check(x, y, z, -1,  2, 0, 49)
        
            # (z+1)
            #
            # f e d e f
            # e c b c e
            # d b a b d 
            # e c b c e
            # f e d e f
            
            check(x, y, z,  0,  0, 1, 22)  # a
            check(x, y, z, -1,  0, 1, 31)  # b
            check(x, y, z,  1,  0, 1, 31)
            check(x, y, z,  0, -1, 1, 31)
            check(x, y, z,  0,  1, 1, 31)
            check(x, y, z, -1, -1, 1, 38) # c
            check(x, y, z, -1,  1, 1, 38)
            check(x, y, z,  1, -1, 1, 38)
            check(x, y, z,  1,  1, 1, 38)
            check(x, y, z, -2,  0, 1, 49) # d
            check(x, y, z,  2,  0, 1, 49)
            check(x, y, z,  0, -2, 1, 49)
            check(x, y, z,  0,  2, 1, 49)
            check(x, y, z, -1, -2, 1, 54) # e
            check(x, y, z, -1,  2, 1, 54)
            check(x, y, z, -2, -1, 1, 54)
            check(x, y, z, -2,  1, 1, 54)
            check(x, y, z,  1, -2, 1, 54)
            check(x, y, z,  1,  2, 1, 54)
            check(x, y, z,  2, -1, 1, 54)
            check(x, y, z,  2,  1, 1, 54)
            check(x, y, z, -2, -2, 1, 66) # f
            check(x, y, z, -2,  2, 1, 66)
            check(x, y, z,  2, -2, 1, 66)
            check(x, y, z,  2,  2, 1, 66)
            
            # (z+2)
            #   f   f
            # f e d e f
            #   d   d
            # f e d e f
            #   f   f
            
            check(x, y, z, -1,  0, 2, 49) # d
            check(x, y, z,  1,  0, 2, 49)
            check(x, y, z,  0, -1, 2, 49)
            check(x, y, z,  0,  1, 2, 49)
            check(x, y, z, -1, -1, 2, 54) # e
            check(x, y, z, -1,  1, 2, 54)
            check(x, y, z,  1, -1, 2, 54)
            check(x, y, z,  1,  1, 2, 54)
            check(x, y, z, -1, -2, 2, 66) # f
            check(x, y, z, -1,  2, 2, 66)
            check(x, y, z, -2, -1, 2, 66)
            check(x, y, z, -2,  1, 2, 66)
            check(x, y, z,  1, -2, 2, 66)
            check(x, y, z,  1,  2, 2, 66)
            check(x, y, z,  2, -1, 2, 66)
            check(x, y, z,  2,  1, 2, 66)

ido.GetPointData().SetScalars(distArr)