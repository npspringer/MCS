"""
 Download and install python
 Install pulp numpy and pandas.
 Then install pulp using pip.

"""

# Imports packages not built into Python
import pulp
import numpy as np
import pandas as pd
# The following data structure is very important! It preserves the order defined in the csv files.
# This is something the regular 'dict' in the tutorial does not do.
from collections import OrderedDict

# Parameters
b_issuecost = pd.read_csv('b_issuecost.csv')
b_issuecost = OrderedDict(zip(b_issuecost['Issuecost'], b_issuecost['Value']))
b = np.array(b_issuecost.values())

c_indicatorcost = pd.read_csv('c_indicatorcost.csv')
c_indicatorcost = OrderedDict(zip(c_indicatorcost['Indicatorcost'], c_indicatorcost['Value']))
c = np.array(c_indicatorcost.values())

v_issueattributeselect = pd.read_csv('v_issueattributeselect.csv')
v_issueattributeselect = OrderedDict(zip(v_issueattributeselect['Issueattributes'], v_issueattributeselect['Value']))
v = np.array(v_issueattributeselect.values())

w_indicatorattributeselect = pd.read_csv('w_indicatorattributeselect.csv')
w_indicatorattributeselect = OrderedDict(zip(w_indicatorattributeselect['Indicatorattributes'], w_indicatorattributeselect['Value']))
w = np.array(w_indicatorattributeselect.values())

#coverage_A= pd.read_csv('A_issueindicators.csv', header=0, index_col=0)
coverage_A= pd.read_csv('A_issueindicators.csv', header=0, index_col=0)
#A = coverage_A.drop(coverage_A.columns[0], axis = 1).values
Aindex = pd.MultiIndex.from_product([b_issuecost, c_indicatorcost], names=['Issues','Indicators'])
coverage_A= coverage_A.stack()
coverage_A = pd.Series(coverage_A, index=Aindex)
coverage_A = OrderedDict(coverage_A)

coverage_M= pd.read_csv('M_attributesissues.csv', header=0, index_col=0)
#A = coverage_A.drop(coverage_A.columns[0], axis = 1).values
Mindex = pd.MultiIndex.from_product([b_issuecost, v_issueattributeselect], names=['Issues','Attributes'])
coverage_M= coverage_M.stack()
coverage_M = pd.Series(coverage_M, index=Mindex)
coverage_M = OrderedDict(coverage_M)

coverage_N= pd.read_csv('N_indicatorsattributes.csv', header=0, index_col=0)
#A = coverage_A.drop(coverage_A.columns[0], axis = 1).values
Nindex = pd.MultiIndex.from_product([c_indicatorcost, w_indicatorattributeselect], names=['Indicators','Attributes'])
coverage_N= coverage_N.stack()
coverage_N = pd.Series(coverage_N, index=Nindex)
coverage_N = OrderedDict(coverage_N)

#Sets
Issues = b_issuecost.keys()
Indicators = c_indicatorcost.keys()
Attributes = v_issueattributeselect.keys()

#Indices
j_idx = np.arange(len(b))
i_idx = np.arange(len(c))
k_idx = np.arange(len(v))

#LP Define
min_covering_set = pulp.LpProblem('MCS Problem', pulp.LpMinimize)

#Variables
x = pulp.LpVariable.dicts('x_%s', Indicators, lowBound=0)
t = pulp.LpVariable.dicts('t_%s', Issues, lowBound=0)

#Objective Function
ind_cos = np.sum([c_indicatorcost[i] * x[i] for i in Indicators]) + np.sum([coverage_M[j, k] * t[j] for k in Attributes for j in Issues])
min_covering_set += ind_cos

#Constraints
#for j in Indicators:
#   Ax = np.sum([coverage_A[j, i] * x[i] for i in Issues])
for j in Issues:
    for k in Attributes:
        min_covering_set += np.sum([coverage_A[j, i] * x[i] for i in Indicators]) + (v_issueattributeselect[k] * t[j]) >= b_issuecost[j]

for i in Indicators:
    for k in Attributes:
        min_covering_set += w_indicatorattributeselect[k] * x[i] <= coverage_N[i, k]
        
#Solver
#min_covering_set.solve()
min_covering_set.solve(pulp.CPLEX_PY())

#Print the result
for i in Indicators:
    print 'The indicator %s gets a score of %s' % (i, x[i].value())
    
for i in Indicators:
    print x[i].varValue
    
for i in Indicators:
    print x[i].name
    
for i in min_covering_set.variables():
    print 'The indicator %s gets a score of' % (i)

flow = pd.Series('', index=c_indicatorcost)
for i in Indicators:
  flow[i]=x[i].varValue
  