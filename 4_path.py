# Compute the path between two points in space

# Input 1: vtkImageData with cells
# Input 2: vtkUnstructuredGrid with graph
# Input 3: Start location
# Input 4: End location
       
vertical_footspan = 1
 
import datetime  

##########################################################################
############################## Path finding ##############################
##########################################################################

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
    #return abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)
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

def ShortestPathGraph(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 1)  # 0
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 1  # 0
    
    while not frontier.empty():
        current = frontier.get()
        
        if current == goal:
            break
        
        # NEW - Find neighbours & determine costs
        neighbors = []
        costs = []
        it = vtk.vtkOutEdgeIterator()
        graph.GetOutEdges(current, it)
        while it.HasNext():
            edge = it.NextGraphEdge()
            cost = graph.GetEdgeData().GetArray('weight').GetValue(edge.GetId())
            costs.append(cost)
            neighbors.append(edge.GetTarget())
        
        # for next in graph.neighbors(current):
        for i, next in enumerate(neighbors):
            cost_next = costs[i]    # NEW
        
            new_cost = cost_so_far[current] + cost_next
            # new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(graph.GetPoints().GetPoint(goal), graph.GetPoints().GetPoint(next))
                frontier.put(next, priority)
                came_from[next] = current
      
    return cost_so_far 
    
def TraversePathGraph(graph, start, goal):
    vertices = []
    edges = []
    
    field = graph.GetVertexData().GetArray("field")
    
    next = goal
    vertices.append(next)
    while next != start:
        it = vtk.vtkOutEdgeIterator()
        graph.GetOutEdges(next, it)
        
        dist = 100000
        while it.HasNext():
            e = it.NextGraphEdge()
            n = e.GetTarget() 
            d = field.GetValue(n)  
            
            if d <= dist and d > 0:            # Bug was d < dist 
                dist = d
                next = n
                edge = e.GetId()
        vertices.append(next)
        edges.append(edge)
    
    return vertices, edges
    
#############################################################################
############################## Data conversion ##############################
#############################################################################
 
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
    
def Arr2Dicts(arr, dims):
    # Convert vtkDataArray to a Python dictionary of dictionaries
    vals = {}
    for x in range(dims[0]):
        for y in range(dims[1]):
            for z in range(dims[2]):
                pos = (x,y,z)
                
                val = GetArrValue(arr, dims, pos)
                if val > 0:
                    if not val in vals:
                        vals[val] = {}
                    vals[val][pos] = val
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
    
def UnstructuredGrid2Graph(ug):
    # Convert an unstructured grid to a graph
    graph = vtk.vtkMutableUndirectedGraph()
    
    # Construct vertices
    graph.SetPoints(ug.GetPoints())
    for i in range(ug.GetNumberOfPoints()):
        graph.AddVertex()

    # Construct edges
    for i in range(ug.GetNumberOfCells()):
        idList = vtk.vtkIdList()
        ug.GetCellPoints(i, idList)
        p1 = idList.GetId(0)
        p2 = idList.GetId(1)
        graph.AddGraphEdge(p1, p2)
       
    # Assign edge data
    for i in range(ug.GetCellData().GetNumberOfArrays()):
        arr = ug.GetCellData().GetArray(i)
        graph.GetEdgeData().AddArray(arr);
      
    # Assign vertex data
    for i in range(ug.GetPointData().GetNumberOfArrays()):
        arr = ug.GetPointData().GetArray(i)
        graph.GetVertexData().AddArray(arr);
        
    return graph

def Graph2UnstructuredGrid(graph):
    # Convert a graph to an unstructured grid
    ug = vtk.vtkUnstructuredGrid()

    # Construct points
    if graph.GetNumberOfVertices() != graph.GetPoints().GetNumberOfPoints():
        print 'Error: number of vertices != number of points'
        return None   
    ug.SetPoints(graph.GetPoints())
    
    # Construct lines
    lines = vtk.vtkCellArray()
    lines.Allocate(graph.GetNumberOfEdges())
    it = vtk.vtkEdgeListIterator()
    graph.GetEdges(it)
    while it.HasNext():
        e = it.NextGraphEdge()
        lines.InsertNextCell(2)
        lines.InsertCellPoint(e.GetSource())
        lines.InsertCellPoint(e.GetTarget())

    ug.SetCells(vtk.VTK_LINE, lines)
        
    # Assign point data
    for i in range(graph.GetVertexData().GetNumberOfArrays()):
        arr = graph.GetVertexData().GetArray(i)
        ug.GetPointData().AddArray(arr);
    
    # Assign line data
    for i in range(graph.GetEdgeData().GetNumberOfArrays()):
        arr = graph.GetEdgeData().GetArray(i)
        ug.GetCellData().AddArray(arr);
        
    return ug
    
# Private method
def SetArrayData(d, l, name):
    # Set values in array from dictionary
    arr = vtk.vtkTypeUInt32Array()
    arr.SetName(name)
    arr.SetNumberOfComponents(1)
    arr.SetNumberOfTuples(l)
    for i in range(l):
        arr.SetValue(i, 0)
    for k in d:
        arr.SetValue(k, d[k])
    return arr
        
def SetGraphVertexData(graph, d, name):
    # Assign value to each vertex
    arr = SetArrayData(d, graph.GetNumberOfVertices(), name)
    graph.GetVertexData().AddArray(arr)
    
def SetGraphEdgeData(graph, d, name):
    # Create array
    arr = vtk.vtkTypeUInt32Array()
    arr.SetName(name)
    arr.SetNumberOfComponents(1)
    arr.SetNumberOfTuples(graph.GetNumberOfEdges())

    # Iterate edges
    i = 0
    it = vtk.vtkEdgeListIterator()
    graph.GetEdges(it)
    while it.HasNext():
        e = it.NextGraphEdge()
        edge_id = e.GetId()
        if edge_id in d:
            val = d[edge_id]
            arr.SetValue(i, val)
        else:
            arr.SetValue(i, 0)
        i = i + 1
        
    # Assign array
    graph.GetEdgeData().AddArray(arr)
    
def GraphWeights2Dict(graph):
    # Create a dictionary of the graph's weights
    d = {}
    arr = graph.GetEdgeData().GetArray('weight')
    it = vtk.vtkEdgeListIterator()
    graph.GetEdges(it)
    while it.HasNext():
        e = it.NextGraphEdge()
        d[e.GetId()] = arr.GetValue(e.GetId())
    return d
    
def Dict2GraphWeights(graph, weights_dict):
    arr = graph.GetEdgeData().GetArray('weight')
    arr.SetNumberOfTuples(len(weights_dict))
    
    # Re-order weights
    i = 0
    it = vtk.vtkEdgeListIterator()
    graph.GetEdges(it)
    while it.HasNext():
        e = it.NextGraphEdge()
        weigth = weights_dict[e.GetId()]
        arr.SetValue(i, weigth)
        i = i + 1
       
def CopyUnstructuredGridData(ug_source, ug_target):
    ug_target.SetPoints(ug_source.GetPoints())
    ug_target.SetCells(vtk.VTK_LINE, ug_source.GetCells())
    
    # Assign point data
    for i in range(ug_source.GetPointData().GetNumberOfArrays()):
        arr = ug_source.GetPointData().GetArray(i)
        ug_target.GetPointData().AddArray(arr)
        
    # Assign line data
    for i in range(ug_source.GetCellData().GetNumberOfArrays()):
        arr = ug_source.GetCellData().GetArray(i)
        ug_target.GetCellData().AddArray(arr)
    
###################################################################################
############################## Coordinate conversion ##############################
###################################################################################
    
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
ugi = self.GetInputDataObject(0, 1)
startLocation = self.GetInputDataObject(0, 2)
endLocation = self.GetInputDataObject(0, 3)

dims = idi.GetDimensions()
arr = idi.GetPointData().GetArray('cell_id')

# Construct dictionary of cells
cells_dict = Arr2Dict(arr, dims)
cells = Arr2Dicts(arr, dims)

# Construct graph from unstructured grid
graph_in = UnstructuredGrid2Graph(ugi)
graph = vtk.vtkMutableUndirectedGraph()
graph.DeepCopy(graph_in)

# Store edge weights
weights_dict = GraphWeights2Dict(graph)

# Compute start & end position
start = WorldCoordinateToImageCoordinate(startLocation, dims)
end = WorldCoordinateToImageCoordinate(endLocation, dims)

# ########################################
# 1. Insert start & end position in graph
# ########################################

start_time = datetime.datetime.now() 

# Important note: The newly inserted vertices (2) and edges
#   do not have a portal_id or cell_id assigned to them
#   Use of portal_id_arr and cell_id_arr is therefore invalid
#   after this insertion.

cell_id_start = cells_dict[start]
cell_start = cells[cell_id_start]

graph.GetPoints().InsertNextPoint(start)
start_vertex_index = graph.AddVertex()
# Should update arrays portal_id and 

# Find nodes in start cell
cell_id_arr = graph.GetVertexData().GetArray('cell_id')
for i in range(cell_id_arr.GetNumberOfTuples()):
    if cell_id_arr.GetValue(i) == cell_id_start:
        pos = graph.GetPoints().GetPoint(i)         # Warning: world coordinate. Is atm equal to image coordinate
              
        #print 'Node ' + str(i) + ' in cell ' + str(cell_id_start) + ' is connected to start'
              
        # Create egde between start node and this node in the same cell
        edge = graph.AddGraphEdge(start_vertex_index, i)
        
        # Compute path from start to this node
        path = ShortestPathGrid(cell_start, start, pos)
       
        # Store length of path as weight
        weights_dict[edge.GetId()] = len(path)

cell_id_end = cells_dict[end]
cell_end = cells[cell_id_end]

graph.GetPoints().InsertNextPoint(end)
end_vertex_index = graph.AddVertex()

# Find nodes in end cell
cell_id_arr = graph.GetVertexData().GetArray('cell_id')
for i in range(cell_id_arr.GetNumberOfTuples()):
    if cell_id_arr.GetValue(i) == cell_id_end:
        pos = graph.GetPoints().GetPoint(i)         # Warning: world coordinate. Is atm equal to image coordinate
                                  
        #print 'Node ' + str(i) + ' in cell ' + str(cell_id_end) + ' is connected to end'
                                  
        # Create egde between end node and this node in the same cell
        edge = graph.AddGraphEdge(end_vertex_index, i)
        
        # Compute path from end to this node
        path = ShortestPathGrid(cell_end, end, pos)
        
        # Store length of path as weight
        weights_dict[edge.GetId()] = len(path)
        
Dict2GraphWeights(graph, weights_dict)

# ########################################
# 2. Path-finding in graph
# ########################################

# start_time = datetime.datetime.now()

field = ShortestPathGraph(graph, start_vertex_index, end_vertex_index)
SetGraphVertexData(graph, field, "field")
vertices, edges = TraversePathGraph(graph, start_vertex_index, end_vertex_index)

#end_time = datetime.datetime.now() 
 
#print 'Path-finding in graph: ' + str((end_time-start_time).microseconds) + ' microseconds'
  
# # Output (optional)
# path_dict = {} 
# for edge in edges:
    # path_dict[edge] = 1
# SetGraphEdgeData(graph, path_dict, "path")

# path_dict = {}
# for vertex in vertices:
    # path_dict[vertex] = 1
# SetGraphVertexData(graph, path_dict, "path")

# ########################################
# 3. Path-finding in cells
# ######################################## 

#start_time = datetime.datetime.now()

# Compute path in each cell
path_voxels = {}
cell_id_arr = graph.GetEdgeData().GetArray('cell_id')
portal_id_arr = graph.GetVertexData().GetArray('portal_id')
for i, edge in enumerate(edges):
    # Get vertices
    v1_index = vertices[i]
    v2_index = vertices[i+1]
     
    v1 = graph.GetPoints().GetPoint(v1_index)
    v2 = graph.GetPoints().GetPoint(v2_index)
    
    if cells_dict[v1] != cells_dict[v2]:
        # Two vertices is another cell (= portal)
    #if portal_id_arr.GetValue(v1_index) == portal_id_arr.GetValue(v2_index):
        # Two vertices of the same portal
        # They lie in different cells so a path can not be computed through a cell
        path_voxels[v1] = 1
        path_voxels[v2] = 1
    else:
        # Get cell
        # cell_id = cell_id_arr.GetValue(edge)      
        # Edges to and from start and end do not have an cell_id
        cell_id = cells_dict[v1]
        cell = cells[cell_id]
        
        # print 'Cell : ' + str(cell_id)

        # Compute path
        path = ShortestPathGrid(cell, v1, v2)
        
        for p in path:                  # Comment in test?
            pos, steps = p              # Comment in test?
            path_voxels[pos] = 1        # Comment in test?    

path_voxels[start] = 1
path_voxels[end] = 1
            
end_time = datetime.datetime.now() 

print 'Path-finding took: ' + str((end_time-start_time).microseconds) + ' microseconds'
print 'Path has length: ' + str(len(path_voxels))

ido = self.GetOutput()  
path_arr = Dict2Arr(path_voxels, dims, 'path')
ido.GetPointData().AddArray(path_arr)
            
# # Output to unstructured grid
# ugo = self.GetOutput()
# u = Graph2UnstructuredGrid(graph)
# CopyUnstructuredGridData(u, ugo)
