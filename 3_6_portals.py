# Generate portals
# April 2016 - Martijn Koopman

# User input
allowed_types = [1,2,3]    # 1 = floor, 2 = stairs, 3 = obstacle

# Read input
idi = self.GetInput()
cell_id_arr = idi.GetPointData().GetArray('cell_id')
cell_types_arr = idi.GetPointData().GetArray('cell_type')
cell_sizes_arr = idi.GetPointData().GetArray('cell_size')

dims = idi.GetDimensions()
numTuples = dims[0]*dims[1]*dims[2]

# #################### 
# Create output
ido = self.GetOutput()
portals_id_arr = vtk.vtkTypeUInt32Array()       # Portal IDs 
portals_id_arr.SetName('portal_id')
portals_id_arr.SetNumberOfComponents(1)
portals_id_arr.SetNumberOfTuples(numTuples)

for i in range(numTuples):
    portals_id_arr.SetValue(i, 0)

# #################### BEGIN HELPER FUNCTIONS AND CLASSES ####################

def GetArrValue(arr, pos):
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return 0        # -1 for exterior
    else:
        i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
        return arr.GetValue(i)

def SetArrValue(arr, pos, val):
    i = pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1])
    arr.SetValue(i, val)
                   
# #################### END OF HELPER FUNCTIONS AND CLASSES ####################

# #################### 
# Find shared faces between cells

portal_num = 1      # Because 0 is empty space
portal_ids = {}     # cell_id1, and cell_id2 are index. Portal_id is value
portal_voxels = {}  # portal_id is index.

for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):
            pos = (x,y,z)
            
            cell_id = GetArrValue(cell_id_arr, pos)
            cell_type = GetArrValue(cell_types_arr, pos)
            
            # print 'Cell ID: ' + str(cell_id)
            
            if cell_id != 0 and cell_type in allowed_types:
                      
                cell_id_neighbours = []
                
                # Iterate neighbours (6-connectivity)
                for i in range(3):
                    for k in range(-1,2,2):
                        pos_n = list(pos)
                        pos_n[i] = pos_n[i]+k
                        pos_n = tuple(pos_n)
                                
                        # Check cell ID of neighbours
                        cell_id_n = GetArrValue(cell_id_arr, pos_n)
                        cell_type_n = GetArrValue(cell_types_arr, pos_n)
                        
                        if cell_id_n != 0 and cell_id_n != cell_id and cell_type_n in allowed_types:
                            cell_id_neighbours.append(cell_id_n)
                
                #if cell_id == 71 or cell_id == 40 or cell_id == 36:
                #    print cell_id
                #    print cell_id_neighbours
                
                # Portal voxel
                cell_id_neighbours = list(set(cell_id_neighbours))
                if len(cell_id_neighbours) == 1:
                    # Only create a portal between two different cells
                        
                    cell_id_n = cell_id_neighbours[0]
                    
                    portal_id = 0
                    if (cell_id, cell_id_n) in portal_ids:
                        portal_id = portal_ids[(cell_id, cell_id_n)]
                    elif (cell_id_n, cell_id) in portal_ids:
                        portal_id = portal_ids[(cell_id_n, cell_id)]
                    else:                                    
                        portal_id = portal_num
                        portal_ids[(cell_id, cell_id_n)] = portal_num
                        portal_num = portal_num + 1

                    # Add voxel to portal 
                    if not portal_id in portal_voxels:
                        portal_voxels[portal_id] = [pos]
                    else:
                        portal_voxels[portal_id].append(pos)
                        
print str(len(portal_ids)) + " portals."


# ########################################
# Output portal ids and size
# ########################################
for portal_id in portal_voxels:
    voxels = portal_voxels[portal_id]
    for voxel in voxels:
        SetArrValue(portals_id_arr, voxel, portal_id)
        
ido.GetPointData().AddArray(portals_id_arr)
