# Compute graph from cells and portals
# Each portal is represented by two vertices. Each cell is represented by an edge.

# April 2016 - Martijn Koopman

vertical_footspan = 1

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

# ########################################
        
class Adjacency:
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
    
def Arr2Dict(arr, dims):
    # Convert VTK array to Python dictionary
    d = {}
    for x in range(dims[0]):
        for y in range(dims[1]):
            for z in range(dims[2]):
                pos = (x,y,z)
                
                val = GetArrValue(arr, dims, pos)
                if val > 0:
                    d[pos] = val
    return d
    
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
    
def ComputePortalCenter(portal):
    # Compute center of portal voxels.
    sum = (0,0,0)
    for voxel in portal:
        sum = (sum[0]+voxel[0], sum[1]+voxel[1], sum[2]+voxel[2]) 
    center = (sum[0]/len(portal), sum[1]/len(portal), sum[2]/len(portal))
    
    # Snap to closest voxel (for non-covex portals)
    closest_voxel = center
    min_dist = 99999
    for voxel in portal:
        dist = sqrt(pow(center[0]-voxel[0],2) + pow(center[1]-voxel[1],2) + pow(center[2]-voxel[2],2)) 
        if dist <= min_dist:
            min_dist = dist
            closest_voxel = voxel
    
    return closest_voxel
    
def FindTwinPortalCenter(portal, center, cells, cell_id_exclude):
    
    print 'Finding twin center for ' + str(center) + ' exclude cell ' + str(cell_id_exclude)
    
    if center == (19,50,4) or center == (19,48,4):
        print portal
    
    # Iterate neighbours of center
    center_twin = center
    
    # Vertical footspan
    for i in range(-vertical_footspan, vertical_footspan+1):
        for j in range(2):
            for k in range(-1,2,2):
                pos_n = list(center)
                pos_n[j] = pos_n[j]+k
                pos_n[2] = pos_n[2]+i
                pos_n = tuple(pos_n)
                    
    # for i in range(3):
        # for k in range(-1,2,2):
            # pos_n = list(center)
            # pos_n[i] = pos_n[i]+k
            # pos_n = tuple(pos_n)
                        
                if pos_n in portal and cells[pos_n] != cell_id_exclude:
                    center_twin = pos_n
                
    if center == center_twin:
        print 'Warning: Two portal centers coincide! Center = ' + str(center)
        print len(portal)
                
    return center_twin
    
# ########################################

# A* code from Red Blob Games (www.redblobgames.com)
# Graph type changed to vtkGraph

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
                        new_cost = cost_so_far[current] + 4
                    else:
                        new_cost = cost_so_far[current] + 3
                        
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
    
# ########################################

# Read input image data
idi_cells = self.GetInputDataObject(0, 0)       # ImageData with cells
idi_portals = self.GetInputDataObject(0, 1)     # ImageData with portals

# Read input arrays & dimensions
cells_arr = idi_cells.GetPointData().GetArray('cell_id')
portals_arr = idi_portals.GetPointData().GetArray('portal_id')
dims = idi_portals.GetDimensions()

# Create dictionary from cells
cells_all = Arr2Dict(cells_arr, dims)

# Create multiple dictionaries from cells
cells = Arr2Dicts(cells_arr, dims)

# Create multiple dictionaries from portals
portals = Arr2Dicts(portals_arr, dims)

print 'Compute centers'

# For each portal: Compute centers and corresponding cell IDs
portals_centers = {}
portals_cells = {}      # For each portal a list of cell ids (max 2)
for id, portal in portals.items():
    # Compute center
    center1 = ComputePortalCenter(portal)
    portals_centers[id] = [center1]
    
    # Determine cell ID of center 1
    center1_cell_id = cells_all[center1]
    portals_cells[id] = [center1_cell_id]
    
    # Compute twin center (in another cell)
    center2 = FindTwinPortalCenter(portal, center1, cells_all, center1_cell_id)
    portals_centers[id].append(center2)
    
    # Determine cell ID of center 2
    center2_cell_id = cells_all[center2]
    portals_cells[id].append(center2_cell_id)
  
  
# ##############################
# Compute adjacency between portals

print 'Compute adjacency between portals'

portal_adjacency = Adjacency()

for id, portal in portals.items():
    p_centers = portals_centers[id]
    p_cells = portals_cells[id]
    
    for id_n, portal_n in portals.items():
        p_centers_n = portals_centers[id]
        p_cells_n = portals_cells[id]
        
        if ((p_cells[0] in p_cells_n and not p_cells[1] in p_cells_n) or (
                p_cells[1] in p_cells_n and not p_cells[0] in p_cells_n)):
            # Portal and portal_n are adjacent
            
            portal_adjacency.set(id, id_n)
                   
# ##############################
# Generate graph

# Note: There are twice as many vertices as there are portals
# Portal numbers start at 1. Vertex index at 0
# To calculate vertex index from portal index and vertex number (1 or 2)
# Vertex index = (portal index - 1) * 2 (+ 1 for vertex number 2)
# Portal index = Vertex index / 2 IF portal index % 2 == 1 ELSE Vertex index - 1 / 2

vertex_adjacency = Adjacency()  # Data structure to prevent duplicate edges

vertices = []
vertices_portal = []    # The portal this vertex is part of
vertices_cell = []      # The cell this vertex is in

edges = []
edges_weight = []
edges_cell = []

print 'Create vertices'

# Create vertices, inner-edges and compute adjacency
for id, portal in portals.items():
    p_centers = portals_centers[id]
    p_cells = portals_cells[id]
    
    # Add vertex 1 of portal
    vertices.append(p_centers[0])
    vertices_portal.append(id)
    vertices_cell.append(p_cells[0])
    vertex1_index = len(vertices) - 1
    
    # Add vertex 2 of portal
    vertices.append(p_centers[1])
    vertices_portal.append(id)
    vertices_cell.append(p_cells[1])    
    vertex2_index = len(vertices) - 1
    
    # Create edge between the two vertices
    vertex_adjacency.set(vertex1_index, vertex2_index)
    
print 'Compute adjacency between portal vertices and other vertices'
    
# Compute adjacency between portal vertices and other vertices    
for id, portal in portals.items():
    p_centers = portals_centers[id]
    p_cells = portals_cells[id]
    
    for i in range(2):
        vertex_index = ((id-1)*2)+i
        vertex_coordinate = p_centers[i]
        vertex_cell = p_cells[i]
        
        for id_n, portal_n in portals.items():
            p_centers_n = portals_centers[id_n]
            p_cells_n = portals_cells[id_n]
            
            for i_n in range(2):
                vertex_index_n = ((id_n-1)*2)+i_n
                vertex_coordinate_n = p_centers_n[i_n]
                vertex_cell_n = p_cells_n[i_n]
                
                if vertex_cell == vertex_cell_n and vertex_index != vertex_index_n:
                    vertex_adjacency.set(vertex_index, vertex_index_n)

print 'Create edges'
                    
# Create edges
for id, portal in portals.items():
    p_centers = portals_centers[id]
    p_cells = portals_cells[id]

    for i in range(2):
        vertex_index = ((id-1)*2)+i
        vertex_cell_id = p_cells[i]
        vertex_coordinate = p_centers[i]

        vertices_adjacent = vertex_adjacency.get(vertex_index)
        
        for vertex_index_n in vertices_adjacent:
            vertex_coordinate_n = vertices[vertex_index_n]

            # Create edge and assign attributes
            edges.append((vertex_index, vertex_index_n))
            edges_cell.append(vertex_cell_id)
            
            # Compute path
            d = int(round(heuristic(vertex_coordinate, vertex_coordinate_n)))   # Distance inner-portal vertices is 1, but in another cell    
            if d <= 1:
                edges_weight.append(d) 
            else:
                path = ShortestPathGrid(cells[vertex_cell_id], vertex_coordinate, vertex_coordinate_n)
                edges_weight.append(len(path))
                
                if len(path) == 0:
                    print 'Warning: Path between ' + str(vertex_coordinate) + ' and ' + str(vertex_coordinate_n) + ' has length 0'

            # Remove adjacency to prevent duplicate edges
            vertex_adjacency.unset(vertex_index, vertex_index_n)
            
            #print 'Edge between ' + str(vertex_index) + ' ' + str(vertex_coordinate) + ' - ' + str(vertex_index_n) + ' ' + str(vertex_coordinate_n) + ' through cell ' + str(vertex_cell_id) + ' with ' + str(len(cells[vertex_cell_id])) + ' voxels'  
       
print 'Construct graph'
       
# Construct graph
graph = vtk.vtkMutableUndirectedGraph()

# Construct vertices
points = vtk.vtkPoints()
for v in vertices:
    points.InsertNextPoint(v);
graph.SetPoints(points)
for i in range(points.GetNumberOfPoints()):
    graph.AddVertex()
      
# Construct edges
for e in edges:
    graph.AddGraphEdge(e[0], e[1])
        
# Assign edge data
edges_weight_arr = vtk.vtkTypeUInt32Array()
edges_weight_arr.SetNumberOfComponents(1)
edges_weight_arr.SetName("weight")

edges_cell_arr = vtk.vtkTypeUInt32Array()
edges_cell_arr.SetNumberOfComponents(1)
edges_cell_arr.SetName("cell_id")

for i, e in enumerate(edges):
    edges_weight_arr.InsertNextValue(edges_weight[i])
    edges_cell_arr.InsertNextValue(edges_cell[i]) 
    
graph.GetEdgeData().AddArray(edges_weight_arr)
graph.GetEdgeData().AddArray(edges_cell_arr)

# Assign vertex data
vertices_portal_arr = vtk.vtkTypeUInt32Array()
vertices_portal_arr.SetNumberOfComponents(1)
vertices_portal_arr.SetName("portal_id")

vertices_cell_arr = vtk.vtkTypeUInt32Array()
vertices_cell_arr.SetNumberOfComponents(1)
vertices_cell_arr.SetName("cell_id")

for i, v in enumerate(vertices):
    vertices_portal_arr.InsertNextValue(vertices_portal[i])
    vertices_cell_arr.InsertNextValue(vertices_cell[i])
    
graph.GetVertexData().AddArray(vertices_portal_arr)
graph.GetVertexData().AddArray(vertices_cell_arr)
    
# Output to unstructured grid
ugo = self.GetOutput()
u = Graph2UnstructuredGrid(graph)
CopyUnstructuredGridData(u, ugo)