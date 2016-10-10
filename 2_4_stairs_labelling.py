# Classify voxels with label 1 (floor) as stairs by estimating slope using plane fitting

# May 2016 - Martijn Koopman

# ToDo: Clean code; Pass variable dims to function GetArrValue() and SetArrValue() as arguments.

import numpy
from numpy import linalg

# User defined parameter:
radius = 1
max_angle = 0.1

# Read input
idi = self.GetInput()
dims = idi.GetDimensions()
arr = idi.GetPointData().GetScalars()

# Create output
ido = self.GetOutput()
output_arr = vtk.vtkTypeUInt32Array()
output_arr.DeepCopy(arr)
output_arr.SetName('classes')

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

# Iterate volume
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):

            if GetArrValue(arr, (x,y,z)) == 1:

                # 1. Construct neighbourhood
                neighbourhood = {}
                for x_offset in range(-radius, radius+1):
                    x_neighbour = x + x_offset
                    for y_offset in range(-radius, radius+1):
                        y_neighbour = y + y_offset

                        max_z = 0
                        for z_offset in range(-radius, radius+1):
                            z_neighbour = z + z_offset

                            if GetArrValue(arr, (x_neighbour, y_neighbour, z_neighbour)) == 1:
                                max_z = z_offset
                    
                        #print str(x_offset+1) + ', ' + str(y_offset+1) + ' = ' + str(max_z)
                        neighbourhood[(x_offset, y_offset)] = max_z


                # 2. 
                # Compute design matrix
                A = []    # Design matrix
                m = []    # Measurements vector
                for key in neighbourhood:
                    x_val = key[0]
                    y_val = key[1]
                    z_val = neighbourhood[key]

                    #print '(' + str(x_val) + ', ' + str(y_val) + ') = ' + str(z_val)

                    # Add computed coefficients to design matrix 
                    row = [x_val, y_val, 1]
                    A.append(row) 

                    # Add z value to measurement vector
                    m.append([z_val])

                #Compute coefficients
                A = numpy.matrix(A)
                m = numpy.matrix(m)
                # Y = (A'' * A) \ A' * z
                Y = linalg.solve((A.T * A), A.T) * m

                # Read coefficients
                a = Y.item(0)
                b = Y.item(1)
                c = Y.item(2)
 
                # 3. Slope  
                v = [a, b, 1]
                horiz = [0,0,1]

                angle = vtk.vtkMath.AngleBetweenVectors(horiz,v)
                angle_degree = vtk.vtkMath.DegreesFromRadians(angle)
                #print 'Angle = ' + str(vtk.vtkMath.DegreesFromRadians(angle))
                #slopeArr.SetValue(i,angle)
                if angle > max_angle:
                    SetArrValue(output_arr, (x,y,z), 2)
            #else:
                #slopeArr.SetValue(i,0)

ido.GetPointData().SetScalars(output_arr)
#ido.GetPointData().AddArray(slopeArr)