import pandas as pd
import os

import pyomo.environ as pyo
# from pyomo.environ import *
from pyomo.opt import SolverFactory

base_path = 'C:\\Users\\vusal.babashov\\Documents\\AAAI_Projects\\dealer_changeover\\model\\model\\prescriptive\\data\\'
path_to_asset_count = os.path.join(base_path, 'asset_count_eligibility.csv')
path_to_changeover = os.path.join(base_path, 'consultant_store_eligibility.csv')
path_to_string = os.path.join(base_path, 'consultant_string_eligibility.csv')
path_to_store = os.path.join(base_path, 'store_dim.csv')


asset_count_csv_file = [
    os.path.join(path_to_asset_count, file) for file in os.listdir(
        path_to_asset_count,
    ) if file.split('.')[-1] == 'csv'
][0]
changeover_csv_file = [
    os.path.join(path_to_changeover, file) for file in os.listdir(
        path_to_changeover,
    ) if file.split('.')[-1] == 'csv'
][0]
string_csv_file = [
    os.path.join(path_to_string, file) for file in os.listdir(
        path_to_string,
    ) if file.split('.')[-1] == 'csv'
][0]
store_csv_file = [
    os.path.join(path_to_store, file) for file in os.listdir(
        path_to_store,
    ) if file.split('.')[-1] == 'csv'
][0]


# store-dim data
df_store = pd.read_csv(store_csv_file, sep='\t', engine='pyarrow',).query('banner_cd == "CTR" and store_status_cd == "A"')
# consultant-string-eligibility
df_string = pd.read_csv(string_csv_file, sep='\t', engine='pyarrow')
# consultant-store-eligibility
df_changeover = pd.read_csv(changeover_csv_file, sep='\t', engine='pyarrow')
# print(df_changeover)
 # asset-count-eligibility
df_asset_counts = pd.read_csv(asset_count_csv_file, sep='\t', engine='pyarrow')
# print(df_asset_counts)

# Decision Variables
df_string = df_string.query('resource_is_eligible_for_string == 1').reset_index(
        drop=True,
    ).drop_duplicates(subset=['resource_id', 'string_id']).set_index(['resource_id', 'string_id'])

# Change the type of the 'id' column from int to str
df_changeover['store_num'] = df_changeover['store_num'].astype('str', errors='ignore')
df_changeover['store_num'] = df_changeover['store_num'].str.pad(4, 'left', '0')
df_changeover_X_ik = df_changeover.query('resource_is_eligible_for_store_changeover== 1').reset_index(
        drop=True,
    ).drop_duplicates(subset=['resource_id', 'store_num']).set_index(['resource_id', 'store_num'])


df_asset_counts['store_num'] = df_asset_counts['store_num'].astype('str', errors='ignore')
df_asset_counts['store_num'] = df_asset_counts['store_num'].str.pad(4, 'left', '0')
df_asset_counts_U_ikn = df_asset_counts.query('resource_is_eligible_for_asset_counts == 1 and is_asset_counting_week == 1 and at_least_one_consultant_available == 1').reset_index(
        drop=True,
    ).drop_duplicates(subset=['resource_id', 'store_num', 'week_id']).set_index(['resource_id', 'store_num', 'week_id'])


# Check if the specific index exists
# index_to_check = ('Lynn M', "0645", '2023_02')
# if index_to_check in df_asset_counts_U_ikn.index:
#     print(df_asset_counts_U_ikn.loc[index_to_check])
# else:
#     print("Index not found.")


df_resource_weeks_D_k = (df_asset_counts.query("resource_is_eligible_for_asset_counts == 1 and is_asset_counting_week == 1 and at_least_one_consultant_available == 1").reset_index(drop=True)
    .drop_duplicates(subset=["store_num"])
    .set_index(["store_num"])
)
df_travel_distance_r_ik = (
    df_asset_counts.query("resource_is_eligible_for_asset_counts == 1 and is_asset_counting_week == 1 and at_least_one_consultant_available == 1").reset_index(drop=True)
    .drop_duplicates(subset=["resource_id", "store_num"])
    .set_index(["resource_id", "store_num"])
)

model = pyo.ConcreteModel ()

# *****************************************************************************************************************
#                                       Indexes and Sets
# *****************************************************************************************************************

string_index = list (df_string.index)  # [tuple(x) for x in df_string.index]
changeover_index = list (df_changeover_X_ik.index) #[tuple(x) for x in df_changeover_X_ik.index]
asset_count_index = list (df_asset_counts_U_ikn.index) #[tuple(x) for x in df_asset_counts_U_ikn.index]
asset_count_index_consultant = list(df_asset_counts_U_ikn.query ("resource_is_consultant == 1").index)


model.StringIndexSet = pyo.Set(initialize=string_index)
model.ChangeoverIndexSet = pyo.Set(initialize=changeover_index)
model.AssetCountIndexSet = pyo.Set(initialize=asset_count_index)
model.ExtraResourceIndexSet = pyo.Set (initialize = [(k, n) for _, k, n in asset_count_index])
model.ConsultantIndexSet = pyo.Set (initialize = asset_count_index_consultant)

# model.ConsultantIndexSet.pprint()


# *****************************************************************************************************************
#                                       Parameters
# *****************************************************************************************************************


resource_data = df_resource_weeks_D_k["num_resource_weeks_needed"].to_dict()
model.k = pyo.Set (initialize = resource_data.keys())
model.D_k  = pyo.Param(model.k, initialize=resource_data)
# model.D_k.pprint()

df_travel_distance_r_ik = df_travel_distance_r_ik ["travel_distance_km"].to_dict()
model.i_k = pyo.Set (initialize = df_travel_distance_r_ik .keys())
model.r_ik = pyo.Param(model.i_k, initialize = df_travel_distance_r_ik)
# model.r_ik.pprint()
# model.r_ik = pyo.Param(list ((i,k) for i, k, _ in asset_count_index))

# **********************************************************************************************************************
#                                       1. Decision Variables
# ***********************************************************************************************************************

# Define a decision variable with the tuple/triplet indices
model.y_ik = pyo.Var(model.StringIndexSet, within=pyo.Binary)
y_ik = model.y_ik
model.X_ik = pyo.Var(model.ChangeoverIndexSet, within=pyo.Binary)
X_ik = model.X_ik
model.U_ikn = pyo.Var(model.AssetCountIndexSet , within=pyo.Binary)
U_ikn = model.U_ikn
model.Z_kn = pyo.Var (model.ExtraResourceIndexSet, within = pyo.Integers)
Z_kn = model.Z_kn

# ************************************************************************************************************************
#                                                 2. Constraints
# ************************************************************************************************************************

# Constraing 1: If a consultant or analyst can do asset count for store k considering language, s/he is available on asset count weeks considering availablity
    # then we need to assign one of the consultants to for asset count in each store
unique_k  = []
for _, k, _ in model.U_ikn.index_set():
    unique_k.append(k)
model.k_set = pyo.Set(initialize=unique_k)

def const_rule1(model, k):
    return sum(model.Z_kn[k,n] for _, n in model.Z_kn.index_set() if _ == k) +  sum(model.U_ikn[i, k, n] for i, _, n in model.U_ikn.index_set() if _ == k)  <= model.D_k[k]
model.C1 = pyo.Constraint(model.k_set, rule=const_rule1)
# model.C1.pprint()


# # Constraint 2:  Ensures that analyst is not there alone on a given asset count week and store. There is at least one consultant
# df = df_asset_counts_U_ikn.query("resource_is_consultant == 1").to_dict()

M = 1000
unique_kn  = []
for _, k, n in model.U_ikn.index_set():
    unique_kn.append((k,n))
model.kn_set = pyo.Set(initialize=unique_kn)


def const_rule2(model, k, n):
    return sum(model.U_ikn[i, k, n] for i, _ , __ in model.U_ikn.index_set() if _ == k and __ == n)  <=  M*sum(model.U_ikn[i, k, n] for i, _, __ in model.ConsultantIndexSet if _ == k and __ == n)
model.C2 = pyo.Constraint(model.kn_set, rule=const_rule2)
# model.C2.pprint()


# Constraint 3: Max one asset count per week for each resource - sum_k (u_ikn) <= 1 for all i and n
unique_in  = []
for i, k, _ in model.U_ikn.index_set():
    unique_in.append((i,n))
model.in_set = pyo.Set(initialize=unique_in)


def const_rule3(model, i, n):
    return sum(model.U_ikn[i, k, n] for  _ , k, __ in model.U_ikn.index_set() if _ == i and __ == n)  <= 1
model.C3 = pyo.Constraint(model.in_set, rule=const_rule3)
# model.C3.pprint()

# Constraint 4: Ensure that if consultant is assigned a changeover he/she can't do asset counts on that week - u_ik'n <= (1-x_ik) for all i, k, k' and n=T_k
df1 = df_asset_counts_U_ikn.reset_index()
df2 = df_changeover_X_ik.reset_index().drop(
    columns=[
        "string_id",
        "changeover_date",
        "c445_yr_num",
        "c445_wk_num",
        "travel_distance_km",
    ],
)
df_joined = pd.merge(
    df1,
    df2,
    how="inner",
    left_on=["resource_id", "week_id"],
    right_on=[
        "resource_id",
        "changeover_week_id",
    ],
)

model.kIndexSet = pyo.Set(initialize=list(df_joined[["resource_id", "store_num_x", "store_num_y", "week_id"]].itertuples(index=False, name = None)))
# model.k_primeIndexSet = pyo.Set(initialize=list (df_joined["resource_id", "store_num_y", "changeover_week_id"].itertuples(index=False, name = None)))

# Constraint 4: Max one asset count per week for each resource - sum_k (u_ikn) <= 1 for all i and n
def const_rule4(model, i, k, k_prime, n):
    return model.U_ikn[i, k, n]  <= (1 - model.X_ik[i, k_prime])
model.C4 = pyo.Constraint(model.kIndexSet, rule=const_rule4)
# model.C4.pprint()

# Constratint 5: Each store must get one consultant for the changeover - \sum x_{ik} == 1 for each k

unique_changeover  = []
for _, k in model.X_ik.index_set():
    unique_changeover.append(k)
model.co_set = pyo.Set(initialize=unique_changeover)

def const_rule5(model, k):
    return sum(model.X_ik[i, k] for i , _ in model.X_ik.index_set() if _ == k) == 1
model.C5 = pyo.Constraint(model.co_set, rule=const_rule5)
model.C5.pprint()





# print (df_asset_counts_U_ikn.reset_index()['store_num'].astype('str').head())

# index = ('Lynn M', '645', '2023_02')

# if index in model.AssetCountIndexSet:
#     print("IT IS THERE")
# else:
#     print ("IT IS NOT THERE")
     
# model.i= pyo.Set(initialize=df_asset_counts_U_ikn.reset_index()['resource_id'].unique())
# model.i.pprint()
# model.k= pyo.Set(initialize=df_asset_counts_U_ikn.reset_index()['store_num'].astype('str').unique())
# model.k.pprint()

# def const_rule3(model, i, k):
#     return sum(model.U_ikn[i, k, n] for _, _, n in model.AssetCountIndexSet)  <= 1
# model.C3 = pyo.Constraint(model.i, model.k, rule=const_rule3)
# model.C3.pprint()

