import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

model.x = pyo.Var (bounds = (0, None))
model.y = pyo.Var (bounds =  (0, None))

x = model.x
y = model.y

model.C1 = pyo.Constraint(expr = 2*x + y <= 100)

model.obj = pyo.Objective(expr = x*y, sense = pyo.maximize)

opt = SolverFactory ('ipopt', executable = "C:\\Users\\vusal.babashov\\MyPrograms\\Ipopt-3.11.1-win64-intel13.1\\bin\\ipopt.exe")
opt.solve(model)
model.pprint()
print ("\n---------------------------------------------------------------")
print('Obj',  pyo.value(model.obj))
print ('x=',  pyo.value (x))
print ('y=',  pyo.value (x))