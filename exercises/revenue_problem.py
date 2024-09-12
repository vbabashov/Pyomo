import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

model.N = pyo.Var (within = Integers, bounds = (0,None))
model.p = pyo.Var(bounds = (50, 200))
N = model.N
p = model.p

model.c1 = pyo.Constraint (expr=  1001 - 5*p == N)

model.obj = pyo.Objective (expr =  p*N, sense =  maximize)

opt = SolverFactory('couenne', executable="C:\\Users\\vusal.babashov\\MyPrograms\\solvers\\couenne.exe")
# opt = SolverFactory('glpk')
opt.solve(model)
model.pprint()
N = pyo.value (N)
p = pyo.value (p)
print ("\n---------------------------------------------------------------")
print ('N =', N)
print ('p =', p)
print ('Rev:', pyo.value(model.obj))