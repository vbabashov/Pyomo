import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

#Parameters and Sets
T = 10 
M = 4  


#variables
model.x = pyo.Var(range(1,M+1), range(1,T+1), within=pyo.Integers)
x = model.x

#obj function
# model.obj = pyo.Objective(expr = sum([x[m,t] for m in range(1,M+1) for t in range(1,T+1)]), sense=pyo.maximize)
model.obj = pyo.Objective(expr=pyo.summation(x), sense=pyo.maximize)


#constraints
model.C1 = pyo.ConstraintList()
for t in range(1,T+1):
    model.C1.add(expr = 2*x[2,t] - 8*x[3,t] <= 0)
    
model.C2 = pyo.ConstraintList()
for t in range(3,T+1):
    model.C2.add(expr = x[2,t] - 2*x[3,t-2] + x[4,t] >= 1)
    
model.C3 = pyo.ConstraintList()
for t in range(1,T+1):
    model.C3.add(expr = sum([x[m,t] for m in range(1,M+1)]) <= 50)

model.C4 = pyo.ConstraintList()
for t in range(2,T+1):
    model.C4.add(expr = x[1,t] + x[2,t-1] + x[3,t] + x[4,t] <= 10)

model.C5 = pyo.ConstraintList()
for m in range(1,M+1):
    for t in range(1,T+1):
        # model.C5.add(expr = x[m,t] <= 10)
        # model.C5.add(expr = x[m,t] >= 0)
        model.C5.add(pyo.inequality(0, x[m,t], 10))


#solve
# opt = SolverFactory('glpk')
opt = SolverFactory('cbc', executable="C:\\Users\\vusal.babashov\\MyPrograms\\solvers\\cbc.exe" ) 
results = opt.solve(model, tee = True)

# model.pprint()
print(pyo.value (model.obj))