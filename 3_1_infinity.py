# Scalar UChar To UInt
# Convert unsigned char (8 bit) to unsigned integer (32 bit)

# May 2016 - Martijn Koopman

idi = self.GetInput()
dims = idi.GetDimensions()
numTuples = dims[0]*dims[1]*dims[2]
input_arr = idi.GetPointData().GetScalars()

ido = self.GetOutput()
output_arr = vtk.vtkTypeUInt32Array()
output_arr.SetName('ImageScalar')
output_arr.SetNumberOfComponents(1)
output_arr.SetNumberOfTuples(numTuples) 

for i in range(0, numTuples):
    if input_arr.GetValue(i) != 0:
        output_arr.SetValue(i,0)
    else:
        # max = 2^32 - 1 = 4294967295
        output_arr.SetValue(i,1000000000)
        
ido.GetPointData().SetScalars(output_arr)