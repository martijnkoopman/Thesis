# Merge cells based on specific criteria

# May 2016 - Martijn Koopman

# Known bug: The original cells volume is updated. No copy is made.

# User input
allowed_types = [1,2,3]    # 1 = floor, 2 = stairs, 3 = obstacle
vertical_footspan = 1

# ########################################

class Cell:
    
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.voxels = {}
        self.bbox = ((0,0,0),(0,0,0))
        
    def GetNumVoxels(self):
        return len(self.voxels)
        
    def GetBoundingBox(self):
        return self.bbox
        
    def ComputeBoundingBox(self):
        min_x = max_x = min_y = max_y = min_z = max_z = 0
        defined = False
        for pos in self.voxels:
            if not defined:
                min_x = max_x = pos[0]
                min_y = max_y = pos[1]
                min_z = max_z = pos[2]
                defined = True
            else:
                if pos[0] < min_x:
                    min_x = pos[0]
                if pos[1] < min_y:
                    min_y = pos[1]
                if pos[0] < min_z:
                    min_z = pos[2]
                    
                if pos[0] > max_x:
                    max_x = pos[0]
                if pos[1] > max_y:
                    max_y = pos[1]
                if pos[2] > max_z:
                    max_z = pos[2]
        self.bbox = ((min_x, min_y, min_z), (max_x, max_y, max_z))
        return self.bbox

# ########################################

class Adjacency:
    # Store adjacency as a dictionary of sets
    
    def __init__(self):
        self.d = {}
        
    def set(self, x,y):
        # Set adjacency between x and y
        if x in self.d:
            self.d[x].add(y)
        else:
            self.d[x] = set([y])
            
        if y in self.d:
            self.d[y].add(x)
        else:
            self.d[y] = set([x])
            
    def unset(self, x,y):
        # Unset adjacency between x and y
        if x in self.d:
            self.d[x].discard(y)
        if y in self.d:
            self.d[y].discard(x)
            
    def get(self, x):
        # Get adjacency with x
        if x in self.d:
            return list(self.d[x])
        else:
            return []
            
class WeightedAdjacency:
    # Store adjacency as a dictionary
    #   key = (c_id1, c_id2)
    #   value = weight  (number of occurences)
    
    def __init__(self):
        self.d = {}
        
    def set(self, x, y):
        if (x,y) in self.d:
            self.d[(x,y)] = self.d[(x,y)] + 1
        elif (y,x) in self.d:
            self.d[(y,x)] = self.d[(y,x)] + 1
        else:
            self.d[(x,y)] = 1
            
    def unset(self, x, y):
        if (x,y) in self.d:
            val = self.d[(x,y)]
            if val > 0:
                self.d[(x,y)] = val - 1
        elif (y,x) in self.d:
            val = self.d[(y,x)]
            if val > 0:
                self.d[(y,x)] = val - 1
                
    def unsetFull(self, x, y):
        if (x,y) in self.d:
            del self.d[(x,y)]
        elif (y,x) in self.d:
            del self.d[(y,x)]
            
    def unsetFullById(self, i):
        # Find occurences of id in keys
        id_keys = []
        for id_key in self.d:
            if id_key[0] == i or id_key[1] == i:
                id_keys.append(id_key)
                    
        # Delete keys from dictionary
        for id_key in id_keys:
            self.unsetFull(id_key[0], id_key[1])

    def get(self, x, y):
        if (x,y) in self.d:
            return self.d[(x,y)]
        elif (y,x) in self.d:
            return self.d[(y,x)]
        else:
            return 0
            
    def getById(self, x):
        # return list of tuples
        # tuple element 0: Adjacent id
        # tuple element 1: weight
        result = []
        for k in self.d:
            if k[0] == x:
                result.append((k[1], self.d[k]))
            elif k[1] == x:
                result.append((k[0], self.d[k]))
        return result
        
# ########################################

def merge(cells, cell_id_from, cell_id_to, cells_arr, dims):   
    # Copy voxels and change cell id
    for voxel in cells[cell_id_from].voxels:
        cells[cell_id_to].voxels[voxel] = cell_id_to
    
        # Update cell id in array
        SetArrValue(cells_arr, dims, voxel, cell_id_to)

    # Delete cell entry
    del cells[cell_id_from]
    
    return cells

# ########################################

def Arr2Dicts(arr, dims):
    # Convert ImageData to a Python dictionary of portals (or cells)
    portals = {}
    for x in range(dims[0]):
        for y in range(dims[1]):
            for z in range(dims[2]):
                pos = (x,y,z)
                
                portal_id = GetArrValue(arr, dims, pos)
                if portal_id > 0:
                    if not portal_id in portals:
                        portals[portal_id] = {}
                    portals[portal_id][pos] = portal_id
    return portals
   
# ########################################

def GetArrValue(arr, dims, pos):
    # Get value from an array by position
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return 0
    else:
        i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
        return arr.GetValue(i)

def SetArrValue(arr, dims, pos, val):
    # Set value of an array by position
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return
    i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
    arr.SetValue(i, val)

# ########################################

# Read input
idi = self.GetInput()
dims = idi.GetDimensions()
numTuples = dims[0]*dims[1]*dims[2]
cellsArr = idi.GetPointData().GetArray('cell_id')
typesArr = idi.GetPointData().GetArray('cell_type')
sizesArr = idi.GetPointData().GetArray('cell_size')

# Create dictionary
#all_cells_dict = Arr2Dict(cellsArr, dims)
cells_dict = Arr2Dicts(cellsArr, dims)

# Create dictionary of Cell objects
cells = {}
for k in cells_dict:
    cell_voxels = cells_dict[k]
    cell_type = GetArrValue(typesArr, dims, cell_voxels.keys()[0])
    
    # Construct Cell object
    cell = Cell(k, cell_type)
    cell.voxels = cell_voxels
    
    # Add to dictonary
    cells[cell.id] = cell
    
# Iterative merging process
change = True
it = 0
while change:
    change = False
    it = it + 1
    
    print '-------------------------------------'
    print 'Iteration ' + str(it)
    
    # Compute adjacency and number of shared voxels
    # Note: each adjacency is marked twice!
    cell_adjacency = WeightedAdjacency()

    for cell_id in cells:
        cell = cells[cell_id]
        
        for voxel in cell.voxels:
        
            adjacent_cell_ids = set()
        
            # Check neighbours (4 connectivity + vertical footspan)
            for i in range(-vertical_footspan, vertical_footspan+1):
                for j in range(2):
                    for k in range(-1,2,2):
                        voxel_n = list(voxel)
                        voxel_n[j] = voxel_n[j]+k
                        voxel_n[2] = voxel_n[2]+i
                        voxel_n = tuple(voxel_n)
                            
            # # Check neighbours (6-connectivity)
            # for i in range(3):
                # for k in range(-1,2,2):
                    # voxel_n = list(voxel)
                    # voxel_n[i] = voxel_n[i]+k
                    # voxel_n = tuple(voxel_n)
            
                        # Check cell id of voxel and its neighbour
                        cell_id_n = GetArrValue(cellsArr, dims, voxel_n)
                        if cell_id_n != 0 and cell_id_n != cell.id:
                            # Mark adjacency
                            adjacent_cell_ids.add(cell_id_n)
                        
            # Save adjacency
            for adjacent_cell_id in adjacent_cell_ids:
                cell_adjacency.set(cell.id, adjacent_cell_id)

    
                            
    # Merge a cell
    for cell_id in cells:
        cell = cells[cell_id]        
        bbox = cell.ComputeBoundingBox()
        width = abs(bbox[0][0] - bbox[1][0])
        depth = abs(bbox[0][1] - bbox[1][1])
        height = abs(bbox[0][2] - bbox[1][2])
            
        to_merge = False
        if cell.GetNumVoxels() < 5:       
            to_merge = True
            print 'CELL TO SMALL'
        if ((height == 0 and (width==0 or depth==0)) or 
            (width == 0 and (depth==0 or height==0)) or
            (depth == 0 and (width==0 or height==0))):       
            to_merge = True
            print 'CELL TO NARROW'
        
        for adjacent_cell_id, adjacent_cell_weight in cell_adjacency.getById(cell.id):
            if (adjacent_cell_weight/2) > (cell.GetNumVoxels()*0.33):
                to_merge = True
                print 'CELL SHARES TOO MUCH FACES'
            
        if to_merge:
            print 'MERGING CELL ' + str(cell.id)
            print 'Merging cell ' + str(cell.id) + ' with size ' + str(cell.GetNumVoxels())
            print '   Bounding box: ' + str(bbox)
            print '   Width: ' + str(width) + ' depth: ' + str(depth) + ' height: ' + str(height)
            print '   Type: ' + str(cell.type)
            print '   Adjacent to ' + str(cell_adjacency.getById(cell.id))

            # ####################
            # Find neighbour with most shared voxels and >>equal<< type
            # ####################
            merge_neighbour_id = None
            max_shared_voxels = 0
            for adjacent in cell_adjacency.getById(cell.id):
                cell_id_neighbour = adjacent[0]
                num_shared_voxels = adjacent[1]
                
                if (cell.type == cells[cell_id_neighbour].type) and num_shared_voxels >= max_shared_voxels:
                    merge_neighbour_id = cell_id_neighbour
                    max_shared_voxels = num_shared_voxels
            
            # If found: merge
            if merge_neighbour_id:               
                print 'MERGING WITH CELL ' + str(merge_neighbour_id)
                print '    Has same cell type (' + str(cell.type) + ') and most shared voxels'
                             
                # Merge cell 'cell' with cell 'cell_neighbour'
                cells = merge(cells, cell_id, merge_neighbour_id, cellsArr, dims)
                    
                # Delete adjacency
                cell_adjacency.unsetFullById(cell_id)
                    
                change = True
                break
            else:
                # ####################
                # Find neighbour with most shared voxels and >>allowed<< type
                # ####################
                merge_neighbour_id = None
                max_shared_voxels = 0
                for adjacent in cell_adjacency.getById(cell.id):
                    cell_id_neighbour = adjacent[0]
                    num_shared_voxels = adjacent[1]
                    
                    if (cells[cell_id_neighbour].type in allowed_types) and num_shared_voxels >= max_shared_voxels:
                        merge_neighbour_id = cell_id_neighbour
                        max_shared_voxels = num_shared_voxels
                
                if merge_neighbour_id:
                    print 'MERGING WITH CELL ' + str(merge_neighbour_id)
                    print '    Has allowed cell type (' + str(cells[cell_id_neighbour].type) + ') and most shared voxels'
                    
                    # Merge
                    cells = merge(cells, cell_id, merge_neighbour_id, cellsArr, dims)
                    
                    # Delete adjacency
                    cell_adjacency.unsetFullById(cell_id)
                    
                    change = True
                    break
                else:
                    print 'Cell cannot be merged!'
                    print 'Has no neighbours with same cell type or allowed cell type'
                    print 'This cell has type ' + str(cell.type)
                    print 'DELETING CELL ' + str(cell_id)
                    
                    # Delete adjacency
                    cell_adjacency.unsetFullById(cell_id)
                    
                    # Delete from array
                    for voxel in cell.voxels:
                        SetArrValue(cellsArr, dims, voxel, 0)
                    
                    # Delete cell
                    del cells[cell_id]
                    
                    change = True
                    break
            print '-------------------------------'
    

ido = self.GetOutput()

cellsArr = vtk.vtkTypeUInt32Array()
cellsArr.SetName('cell_id')
cellsArr.SetNumberOfComponents(1)
cellsArr.SetNumberOfTuples(numTuples)

typesArr = vtk.vtkUnsignedCharArray()
typesArr.SetName('cell_type')
typesArr.SetNumberOfComponents(1)
typesArr.SetNumberOfTuples(numTuples)

for i in range(cellsArr.GetNumberOfTuples()):
    cellsArr.SetValue(i,0)
    typesArr.SetValue(i,0)

for cell_id in cells:
    cell = cells[cell_id]
    for voxel in cell.voxels:
        SetArrValue(cellsArr, dims, voxel, cell.id)
        SetArrValue(typesArr, dims, voxel, cell.type)
ido.GetPointData().AddArray(cellsArr)
ido.GetPointData().AddArray(typesArr)
