import pandas as pd, numpy as np
from ortools.sat.python import cp_model

#inputs
nodes = pd.read_excel("C:\\Users\\vusal.babashov\\OneDrive - Canadian Tire\\Desktop\\Pyomo\\data\\route_inputs.xlsx", sheet_name='nodes')
paths = pd.read_excel('C:\\Users\\vusal.babashov\\OneDrive - Canadian Tire\\Desktop\\Pyomo\\data\\route_inputs.xlsx', sheet_name='paths')
n_nodes = len(nodes)
n_paths = len(paths)

#model
model = cp_model.CpModel()
x = np.zeros(n_paths).tolist()

for p in paths.index:
    x[p] = model.NewIntVar(0, 1, 'x[{}]'.format(p))

#objective
objFun = sum([x[p]*paths.distance[p] for p in paths.index])
model.Minimize (objFun)

#constraints - sum(x) == 1 (origin and destination)
node_origin = int(nodes.node[nodes.description == 'origin'])
node_destination = int (nodes.node[nodes.description =='destination'])
model.Add (sum([x[p] for p in paths.index [paths.node_from == node_origin]]) == 1)
model.Add (sum([x[p] for p in paths.index [paths.node_to == node_destination]]) == 1)

#constraints sum(x, in) = sum (x, out)
for node in nodes.node [nodes.description == 'middle point']:
    sum_in  = sum ([x[p] for p in paths.index[paths.node_to == node]])
    sum_out = sum ([x[p] for p in paths.index[paths.node_from == node]])
    model.Add (sum_in == sum_out)
    
#solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

print('status=', solver.StatusName(status))
print('Obj=', solver.ObjectiveValue())

paths ['activated'] = 0

for p in paths.index:
    paths.activated [p] = solver.Value(x[p])
print(paths)
