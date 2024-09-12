import pyomo.environ as pyo
from pyomo.opt import SolverFactory

def run():
    model = pyo.ConcreteModel()

    #Parameter and Sets
    model.T = pyo.Param(initialize=10)
    model.M = pyo.Param(initialize=4)
    model.LimProd = pyo.Param(initialize=10)
    
    model.setT = pyo.RangeSet(1, model.T)
    model.setM = pyo.RangeSet(1, model.M)
    
    #variables
    model.x = pyo.Var(model.setM, model.setT, within=pyo.Integers)
    
    #obj function
    model.obj = pyo.Objective(expr = pyo.summation(model.x), sense=pyo.maximize)
    
    #constraints
    model.C1 = pyo.Constraint(model.setT, rule=firstRule)
    model.C2 = pyo.Constraint(range(3,model.T+1), rule=secondRule)
    model.C3 = pyo.Constraint(model.setT, rule=thirdRule)
    model.C4 = pyo.Constraint(range(2,model.T+1), rule=fourthRule)
    model.C5 = pyo.Constraint(model.setM, model.setT, rule=fifthRule)
    
    #solve
    # opt = SolverFactory('glpk')
    # results = opt.solve(model, tee=True)
    opt = SolverFactory('cbc', executable="C:\\Users\\vusal.babashov\\MyPrograms\\solvers\\cbc.exe") 
    results = opt.solve(model, tee = True)
    
    print(pyo.value(model.obj))


def firstRule(model, t):
    return 2*model.x[2,t] - 8*model.x[3,t] <= 0
def secondRule(model, t):
    return model.x[2,t] - 2*model.x[3,t-2] + model.x[4,t] >= 1
def thirdRule(model, t):
    return  sum([model.x[m,t] for m in model.setM]) <= 50
def fourthRule(model, t):
    return model.x[1,t] + model.x[2,t-1] + model.x[3,t] + model.x[4,t] <= model.LimProd
def fifthRule(model, m, t):
    return pyo.inequality(0, model.x[m,t], model.LimProd)


run()







