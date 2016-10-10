# Cell generation
#
# Generate cells from a distance field by applying watershed algorithm
# Cells start growing at local minima in the distance field (a certain iso value)
# Cells expand by decreasing the iso value.
# New cells are detected using a flood fill with 26-connectivity
# Existing cells are expanded using 6-connectivity

# May 2016 - Martijn Koopman

from collections import deque

# Read input
idi1 = self.GetInputDataObject(0, 0)     # ImageData with distance field
idi2 = self.GetInputDataObject(0, 1)     # ImageData with classes (1 = plane, 2 = stairs, 3 = obstacle)

dims = idi1.GetDimensions()
numTuples = dims[0]*dims[1]*dims[2] 
distArr = idi1.GetPointData().GetScalars()
classArr = idi2.GetPointData().GetScalars()

ido = self.GetOutput()

# #################### BEGIN HELPER FUNCTIONS AND CLASSES ####################
# Classes
class Cell:
    
    def __init__(self, id, type):
        self.id = id
        self.type = type
        #self.changed = True
        self.voxels = {}
        
    def GetNumVoxels(self):
        return len(self.voxels)

# Functions
def GetArrValue(arr, pos):
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return 0
    else:
        i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
        return arr.GetValue(i)

def SetArrValue(arr, pos, val):
    i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
    arr.SetValue(i, val)
                
# #################### END OF HELPER FUNCTIONS AND CLASSES ####################

min_distance, max_distance = distArr.GetValueRange()
print 'Distance range: ' + str(min_distance) + ' - ' + str(max_distance)

# Convert distance field to dictionary (sparse data structure)
distanceVolume = {}
for z in range(dims[2]):
    for y in range(dims[1]):
        for x in range(dims[0]):
            pos = (x,y,z)
            distance = GetArrValue(distArr, pos)
            distanceVolume[pos] = distance

# Watershed
cell_num = 1    # Because 0 is empty space. Note: Cell num = cell index + 1
cells = []
for isoValue in range(max_distance, min_distance, -1): # (min_distance, max_distance):
    print 'IsoValue = ' + str(isoValue)
    
    ###############################################################
    #################### Dilate existing cells ####################
    ###############################################################
    
    # As long as they keep changing
    changed = True
    while changed:
        changed = False
        
        # Dilate existing cells
        for cell_i, cell in enumerate(cells):

            # Dilate this cell 
               
            # Add voxels to OPEN list
            open = cells[cell_i].voxels         # OPEN list     (To process)
            closed = {}                         # CLOSED list   (Processed)
            
            while any(open):
                pos, val = open.popitem()
                closed[pos] = cell.id
                                           
                # Check neighbours (6 connectivity)
                for i in range(3):
                    for k in range(-1,2,2):
                        pos_n = list(pos)
                        pos_n[i] = pos_n[i]+k
                        pos_n = tuple(pos_n)

                        if pos_n in distanceVolume and distanceVolume[pos_n] == isoValue and GetArrValue(classArr, pos_n) == cell.type:
                            # Add neighbour to processed voxels
                            closed[pos_n] = cell.id

                            # Remove distance value from distance field (destructive)
                            distanceVolume[pos_n] = 0
                                                        
                            # Changed?
                            changed = True
                            
            cells[cell_i].voxels = closed
   
    #########################################################    
    #################### Find new cells #####################
    #########################################################

    # Find first occurence of isoValue in distance field
    pos_start = None
    for pos in distanceVolume:
        if distanceVolume[pos] == isoValue:
            pos_start = pos
            
    while pos_start != None:
        # Found isoValue occurence!
        # Create cell
                
        cell = Cell(cell_num, GetArrValue(classArr, pos_start))
        cell_num = cell_num + 1
        #cell.changed = True
        voxels = {}
        
        # Flood fill a cell
        queue = deque([pos_start]) 
        while queue:

            pos = queue.popleft()
         
            if pos in distanceVolume and distanceVolume[pos] == isoValue and GetArrValue(classArr, pos) == cell.type:
                # Add voxel to cell
                voxels[pos] = cell.id
                
                # Remove distance value from distance field (destructive)
                distanceVolume[pos] = 0
         
                # 26 connectivity
                for x_r in range(-1,2):
                    x_n = pos[0] + x_r
                    for y_r in range(-1,2):
                        y_n = pos[1] + y_r
                        for z_r in range(-1,2):
                            z_n = pos[2] + z_r
                
                            # Add neighbour to queue
                            queue.append((x_n, y_n, z_n)) 

        cell.voxels = voxels
        cells.append(cell)
              
        # Find next occurence of isoValue
        pos_start = None
        for pos in distanceVolume:
            if distanceVolume[pos] == isoValue:
                pos_start = pos
                
# Aggregate segments to cells or portals
print 'Has ' + str(len(cells)) + ' cells'
        
# Output
cellsArr = vtk.vtkTypeUInt32Array()
cellsArr.SetName('cell_id')
cellsArr.SetNumberOfComponents(1)
cellsArr.SetNumberOfTuples(numTuples)

typesArr = vtk.vtkUnsignedCharArray()
typesArr.SetName('cell_type')
typesArr.SetNumberOfComponents(1)
typesArr.SetNumberOfTuples(numTuples)

sizesArr = vtk.vtkTypeUInt32Array()
sizesArr.SetName('cell_size')
sizesArr.SetNumberOfComponents(1)
sizesArr.SetNumberOfTuples(numTuples)
    
# Empty array
for i in range(0, numTuples):
    cellsArr.SetValue(i, 0)
    typesArr.SetValue(i, 0)
    sizesArr.SetValue(i, 0)

for cell in cells:   
    for pos in cell.voxels:
        SetArrValue(cellsArr, pos, cell.id)
        SetArrValue(typesArr, pos, cell.type)
        SetArrValue(sizesArr, pos, cell.GetNumVoxels())
    
ido.GetPointData().AddArray(cellsArr)
ido.GetPointData().AddArray(typesArr)
ido.GetPointData().AddArray(sizesArr)
