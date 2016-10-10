# Find path in a voxelized model
#
# Input 1: Navigable space (ImageData with navigable space = 1, non-navigable space = 0)
# Input 2: Start position (Probe location)
# Input 3: End position (Probe location)

# June 2016 - Martijn Koopman

# User defined parameter:
vertical_footspan = 1

import datetime

##########################################################################
############################## Path-finding ##############################
##########################################################################

# A* code from Red Blob Games (www.redblobgames.com)

import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

def heuristic(a, b):
    (x1, y1, z1) = a
    (x2, y2, z2) = b
    # return abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)
    return sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2) + pow(z1 - z2, 2))

def ShortestPathGrid(voxels, start, end):
    path_found = False

    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()
        
        if current == end:
            path_found = True
            break
        
        # 8 connectivity + vertical footspan
        for z_r in range(-vertical_footspan, vertical_footspan+1):
            z_n = current[2] + z_r
            for y_r in range(-1,2):
                y_n = current[1] + y_r
                for x_r in range(-1,2):
                    x_n = current[0] + x_r    
                    next = (x_n,y_n,z_n)
                       
                    if x_r != 0 and y_r != 0:
                        new_cost = cost_so_far[current] + 4 + abs(z_r)
                    else:
                        new_cost = cost_so_far[current] + 3 + abs(z_r)
                        
                    if next in voxels and (next not in cost_so_far or new_cost < cost_so_far[next]):
                        cost_so_far[next] = new_cost
                        priority = new_cost + heuristic(end, next)
                        frontier.put(next, priority)
                        came_from[next] = current
           
    path = []
    if path_found:
        pos = end
        steps = cost_so_far[pos]
        while steps > 3:
            lowest_next_steps = steps

            # 8 connectivity + vertical footspan
            for z_r in range(-vertical_footspan, vertical_footspan+1):
                z_n = pos[2] + z_r
                for y_r in range(-1,2):
                    y_n = pos[1] + y_r
                    for x_r in range(-1,2):
                        x_n = pos[0] + x_r    
                        next_pos = (x_n,y_n,z_n)

                        if next_pos in cost_so_far:
                            next_steps = cost_so_far[next_pos]

                            if next_steps < lowest_next_steps and next_steps > 0:       # next_steps = always 1? 
                                lowest_next_pos = next_pos
                                lowest_next_steps = next_steps

            # Next neighbour
            pos = lowest_next_pos
            steps = lowest_next_steps

            # Append to path
            path.append((pos,steps))
            
    return path
    
###################################################################################
############################## Coordinate conversion ##############################
###################################################################################
    
def Arr2Dict(arr, dims):
    # Convert vtkDataArray to a Python dictionary
    vals = {}
    for x in range(dims[0]):
        for y in range(dims[1]):
            for z in range(dims[2]):
                pos = (x,y,z)
                
                val = GetArrValue(arr, dims, pos)
                if val > 0:
                    vals[pos] = val
    return vals
    
def Dict2Arr(d, dims, name):
    num_tuples = dims[0]*dims[1]*dims[2]
    arr = vtk.vtkTypeUInt32Array()
    arr.SetName(name)
    arr.SetNumberOfComponents(1)
    arr.SetNumberOfTuples(num_tuples)
    
    for x in range(dims[0]):
        for y in range(dims[1]):
            for z in range(dims[2]):
                pos = (x,y,z)
                if pos in d:
                    SetArrValue(arr, dims, pos, d[pos])
                else:
                    SetArrValue(arr, dims, pos, 0)
            
    return arr
    
def WorldCoordinateToImageCoordinate(location, dims):
    worldCoordinate = location.GetPoint(0)
    index = idi.FindPoint(worldCoordinate)
    i = index
    z = i / (dims[0] * dims[1])
    i -= (z * dims[0] * dims[1])
    y = i / dims[0]
    x = i % dims[0]
    return (x,y,z)

##############################################################################
############################## Volume accessors ##############################
##############################################################################
    
def GetArrValue(arr, dims, pos):
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return 0
    else:
        i = int(pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1]))
        return arr.GetValue(i)

def SetArrValue(arr, dims, pos, val):
    if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or pos[1] >= dims[1] or pos[2] < 0 or pos[2] >= dims[2]:
        return
    i = int(pos[0] + (pos[1] * dims[0]) + (pos[2] * dims[0] * dims[1]))
    arr.SetValue(i, val)
    
################################################################################
################################################################################    
################################################################################

##################################
########### Read inputs ##########
##################################

idi = self.GetInputDataObject(0, 0)
startLocation = self.GetInputDataObject(0, 1)
endLocation = self.GetInputDataObject(0, 2)

dims = idi.GetDimensions()
arr = idi.GetPointData().GetScalars()

# Construct dictionary of navigable space
navigable_space = Arr2Dict(arr, dims)

# Compute start & end position
start = WorldCoordinateToImageCoordinate(startLocation, dims)
end = WorldCoordinateToImageCoordinate(endLocation, dims)

#print 'Start: ' + str(start)
#print 'End: ' + str(end)

start_time = datetime.datetime.now()

# Compute path from start to end
path = ShortestPathGrid(navigable_space, start, end)

end_time = datetime.datetime.now() 

print 'Path-finding took: ' + str((end_time-start_time).microseconds) + ' microseconds.'

# Output
path_voxels = {}
path_voxels[start] = 1
path_voxels[end] = 1
for p in path:
    pos, steps = p
    path_voxels[pos] = 1
    
print 'Path has length: ' + str(len(path_voxels))

ido = self.GetOutput()
path_arr = Dict2Arr(path_voxels, dims, 'path')
ido.GetPointData().SetScalars(path_arr)
