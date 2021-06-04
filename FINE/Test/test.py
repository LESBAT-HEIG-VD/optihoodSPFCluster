# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Workflow for a multi-regional energy system
#
# In this application of the FINE framework, a multi-regional energy system is modeled and optimized.
#
# All classes which are available to the user are utilized and examples of the selection of different parameters within these classes are given.
#
# The workflow is structures as follows:
# 1. Required packages are imported and the input data path is set
# 2. An energy system model instance is created
# 3. Commodity sources are added to the energy system model
# 4. Commodity conversion components are added to the energy system model
# 5. Commodity storages are added to the energy system model
# 6. Commodity transmission components are added to the energy system model
# 7. Commodity sinks are added to the energy system model
# 8. The energy system model is optimized
# 9. Selected optimization results are presented
#

# # 1. Import required packages and set input data path
#
# The FINE framework is imported which provides the required classes and functions for modeling the energy system.

import FINE as fn
import matplotlib.pyplot as plt
from getData import getData
import pandas as pd
import os

cwd = os.getcwd()
data = getData()


# # 2. Create an energy system model instance
#
# The structure of the energy system model is given by the considered locations, commodities, the number of time steps as well as the hours per time step.
#
# The commodities are specified by a unit (i.e. 'GW_electric', 'GW_H2lowerHeatingValue', 'Mio. t CO2/h') which can be given as an energy or mass unit per hour. Furthermore, the cost unit and length unit are specified.

locations = {'building_1', 'building_2'}
commodityUnitDict = {'electricity': r'kW$_{el}$', 'natural_gas': r'kW$_{CH4}$',
                     'space_heat' : r'kW$_{sh}$', 'domestic_hot_water' : r'kW$_{dhw}$',
                     'CO2': r'kg$_{CO_2}$/h'}
commodities = {'electricity', 'natural_gas', 'space_heat', 'domestic_hot_water', 'CO2'}
numberOfTimeSteps = data['Global, numberOfTimeSteps']
hoursPerTimeStep = 1

esM = fn.EnergySystemModel(locations=locations, commodities=commodities, numberOfTimeSteps=int(numberOfTimeSteps),
                           commodityUnitsDict=commodityUnitDict,
                           hoursPerTimeStep=hoursPerTimeStep, costUnit='Euro', lengthUnit='km', verboseLogLevel=0)

CO2_reductionTarget = 1000000000


# # 3. Add commodity sources to the energy system model

# ## Electricity grid

esM.add(fn.Source(esM=esM, name='Electricity grid', commodity='electricity',
                  hasCapacityVariable=True, capacityMax=data['Electricity grid, operationRateMax'],
                  commodityCost=data['Electricity grid, operationCost'],
                  commodityRevenue=data['Electricity grid, feedinCost']))

# ### Natural gas

esM.add(fn.Source(esM=esM, name='Natural gas', commodity='natural_gas',
                  hasCapacityVariable=False,
                  commodityCost=data['Natural gas, operationCost']))


# # 4. Add conversion components to the energy system model

# ### CHP


esM.add(fn.Conversion(esM=esM, name='CHP1', physicalUnit=r'kW$_{CH4}$',
                      commodityConversionFactors={'electricity' : 1, 'natural_gas' : -1,
                                                  'CO2' : data['Natural gas, operationGWP'] + data['CHP, operationGWP'],
                                                  'space_heat' : 1},
                      hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
                      capacityMin=data['CHP, minCapa'], capacityMax=data['CHP, maxCapa'],
                      opexPerCapacity=data['CHP, investmentCost'] * (data['CHP, maintenanceCost']
                                                                     + data['CHP, installationCost']
                                                                     + data['CHP, planificationCost']),
                      investPerCapacity=data['CHP, investmentCost'],
                      investIfBuilt=data['CHP, investmentBaseCost']
                      ))

esM.add(fn.Conversion(esM=esM, name='CHP2', physicalUnit=r'kW$_{CH4}$',
                      commodityConversionFactors={'electricity' : 1, 'natural_gas' : -1,
                                                  'CO2' : data['Natural gas, operationGWP'] + data['CHP, operationGWP'],
                                                  'space_heat' : 1},
                      hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
                      capacityMin=data['CHP, minCapa'], capacityMax=data['CHP, maxCapa'],
                      opexPerCapacity=data['CHP, investmentCost'] * (data['CHP, maintenanceCost']
                                                                     + data['CHP, installationCost']
                                                                     + data['CHP, planificationCost']),
                      investPerCapacity=data['CHP, investmentCost'],
                      investIfBuilt=data['CHP, investmentBaseCost']
                      ))

esM.add(fn.Conversion(esM=esM, name='CHP3', physicalUnit=r'kW$_{CH4}$',
                      commodityConversionFactors={'electricity' : 1, 'natural_gas' : -1,
                                                  'CO2' : data['Natural gas, operationGWP'] + data['CHP, operationGWP'],
                                                  'space_heat' : 1},
                      hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
                      capacityMin=data['CHP, minCapa'], capacityMax=data['CHP, maxCapa'],
                      opexPerCapacity=data['CHP, investmentCost'] * (data['CHP, maintenanceCost']
                                                                     + data['CHP, installationCost']
                                                                     + data['CHP, planificationCost']),
                      investPerCapacity=data['CHP, investmentCost'],
                      investIfBuilt=data['CHP, investmentBaseCost']
                      ))


# ### HP

esM.add(fn.Conversion(esM=esM, name='HP1', physicalUnit=r'kW$_{el}$',
                      commodityConversionFactors={'electricity' : -1, 'domestic_hot_water' : 1,
                                                  'CO2' : data['Electricity grid, operationGWP'] + data['HP, operationGWP']},
                      hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
                      capacityMin=data['HP, minCapa'], capacityMax=data['HP, maxCapa'],
                      opexPerCapacity=data['HP, investmentCost'] * (data['HP, maintenanceCost']
                                                                    + data['HP, installationCost']
                                                                    + data['HP, planificationCost']),
                      investPerCapacity=data['HP, investmentCost'],
                      investIfBuilt=data['HP, investmentBaseCost']
                      ))

esM.add(fn.Conversion(esM=esM, name='HP2', physicalUnit=r'kW$_{el}$',
                      commodityConversionFactors={'electricity' : -1, 'domestic_hot_water' : 1,
                                                  'CO2' : data['Electricity grid, operationGWP'] + data['HP, operationGWP']},
                      hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
                      capacityMin=data['HP, minCapa'], capacityMax=data['HP, maxCapa'],
                      opexPerCapacity=data['HP, investmentCost'] * (data['HP, maintenanceCost']
                                                                    + data['HP, installationCost']
                                                                    + data['HP, planificationCost']),
                      investPerCapacity=data['HP, investmentCost'],
                      investIfBuilt=data['HP, investmentBaseCost']
                      ))

esM.add(fn.Conversion(esM=esM, name='HP3', physicalUnit=r'kW$_{el}$',
                      commodityConversionFactors={'electricity' : -1, 'domestic_hot_water' : 1,
                                                  'CO2' : data['Electricity grid, operationGWP'] + data['HP, operationGWP']},
                      hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
                      capacityMin=data['HP, minCapa'], capacityMax=data['HP, maxCapa'],
                      opexPerCapacity=data['HP, investmentCost'] * (data['HP, maintenanceCost']
                                                                    + data['HP, installationCost']
                                                                    + data['HP, planificationCost']),
                      investPerCapacity=data['HP, investmentCost'],
                      investIfBuilt=data['HP, investmentBaseCost']
                      ))

# # 5. Add commodity storages to the energy system model

# ### Lithium ion batteries

esM.add(fn.Storage(esM=esM, name='Battery1', commodity='electricity',
                   hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
                   chargeEfficiency=data['Battery, effCharge'],
                   dischargeEfficiency=data['Battery, effDischarge'],
                   capacityMin=data['Battery, minCapa'],
                   capacityMax=data['Battery, maxCapa'],
                   stateOfChargeMin=data['Battery, minSOC'],
                   stateOfChargeMax=data['Battery, maxSOC'],
                   opexPerCapacity=data['Battery, investmentCost'] * (data['Battery, installationCost'] + data['Battery, planificationCost']),
                   investPerCapacity=data['Battery, investmentCost'],
                   investIfBuilt=data['Battery, investmentBaseCost']
                   ))

esM.add(fn.Storage(esM=esM, name='Battery2', commodity='electricity',
                   hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
                   chargeEfficiency=data['Battery, effCharge'],
                   dischargeEfficiency=data['Battery, effDischarge'],
                   capacityMin=data['Battery, minCapa'],
                   capacityMax=data['Battery, maxCapa'],
                   stateOfChargeMin=data['Battery, minSOC'],
                   stateOfChargeMax=data['Battery, maxSOC'],
                   opexPerCapacity=data['Battery, investmentCost'] * (data['Battery, installationCost'] + data['Battery, planificationCost']),
                   investPerCapacity=data['Battery, investmentCost'],
                   investIfBuilt=data['Battery, investmentBaseCost']
                   ))

esM.add(fn.Storage(esM=esM, name='Battery3', commodity='electricity',
                   hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
                   chargeEfficiency=data['Battery, effCharge'],
                   dischargeEfficiency=data['Battery, effDischarge'],
                   capacityMin=data['Battery, minCapa'],
                   capacityMax=data['Battery, maxCapa'],
                   stateOfChargeMin=data['Battery, minSOC'],
                   stateOfChargeMax=data['Battery, maxSOC'],
                   opexPerCapacity=data['Battery, investmentCost'] * (data['Battery, installationCost'] + data['Battery, planificationCost']),
                   investPerCapacity=data['Battery, investmentCost'],
                   investIfBuilt=data['Battery, investmentBaseCost']
                   ))


# # ### Hot water storage
#
# esM.add(fn.Storage(esM=esM, name='HW1', commodity='domestic_hot_water',
#                    hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
#                    chargeEfficiency=data['HW, effCharge'],
#                    dischargeEfficiency=data['HW, effDischarge'],
#                    capacityMin=data['HW, minCapa'],
#                    capacityMax=data['HW, maxCapa'],
#                    stateOfChargeMin=data['HW, minSOC'],
#                    stateOfChargeMax=data['HW, maxSOC'],
#                    opexPerCapacity=data['HW, investmentCost'] * (data['HW, installationCost'] + data['HW, planificationCost']),
#                    investPerCapacity=data['HW, investmentCost'],
#                    investIfBuilt=data['HW, investmentBaseCost']
#                    ))
#
# esM.add(fn.Storage(esM=esM, name='HW2', commodity='domestic_hot_water',
#                    hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
#                    chargeEfficiency=data['HW, effCharge'],
#                    dischargeEfficiency=data['HW, effDischarge'],
#                    capacityMin=data['HW, minCapa'],
#                    capacityMax=data['HW, maxCapa'],
#                    stateOfChargeMin=data['HW, minSOC'],
#                    stateOfChargeMax=data['HW, maxSOC'],
#                    opexPerCapacity=data['HW, investmentCost'] * (data['HW, installationCost'] + data['HW, planificationCost']),
#                    investPerCapacity=data['HW, investmentCost'],
#                    investIfBuilt=data['HW, investmentBaseCost']
#                    ))
#
# esM.add(fn.Storage(esM=esM, name='HW3', commodity='domestic_hot_water',
#                    hasCapacityVariable=True, hasIsBuiltBinaryVariable=True, bigM=300,
#                    chargeEfficiency=data['HW, effCharge'],
#                    dischargeEfficiency=data['HW, effDischarge'],
#                    capacityMin=data['HW, minCapa'],
#                    capacityMax=data['HW, maxCapa'],
#                    stateOfChargeMin=data['HW, minSOC'],
#                    stateOfChargeMax=data['HW, maxSOC'],
#                    opexPerCapacity=data['HW, investmentCost'] * (data['HW, installationCost'] + data['HW, planificationCost']),
#                    investPerCapacity=data['HW, investmentCost'],
#                    investIfBuilt=data['HW, investmentBaseCost']
#                    ))


# # 6. Add commodity transmission components to the energy system model


# # 7. Add commodity sinks to the energy system model
esM.add(fn.Sink(esM=esM, name='Electricity demand', commodity='electricity',
                hasCapacityVariable=False, operationRateFix=data['Electricity demand, operationRateFix']))

esM.add(fn.Sink(esM=esM, name='Space heat demand', commodity='space_heat',
                hasCapacityVariable=False, operationRateFix=data['Space heat demand, operationRateFix']))

esM.add(fn.Sink(esM=esM, name='Domestic hot water demand', commodity='domestic_hot_water',
                hasCapacityVariable=False, operationRateFix=data['Domestic hot water demand, operationRateFix']))


# ## 7.3. CO2 sinks

# ### CO2 exiting the system's boundary

esM.add(fn.Sink(esM=esM, name='CO2 to enviroment', commodity='CO2',
                hasCapacityVariable=False, commodityLimitID='CO2 limit', yearlyLimit=366*(1-CO2_reductionTarget)))

# # 8. Optimize energy system model

# All components are now added to the model and the model can be optimized. If the computational complexity of the optimization should be reduced, the time series data of the specified components can be clustered before the optimization and the parameter timeSeriesAggregation is set to True in the optimize call.
esM.cluster(numberOfTypicalPeriods=int(numberOfTimeSteps), numberOfTimeStepsPerPeriod=hoursPerTimeStep)

esM.optimize(timeSeriesAggregation=True)

# Plot operation time series (either one or two dimensional)

# %% tags=["nbval-skip"]
fig1, ax = fn.plotOperation(esM, 'Electricity demand', 'building_1', color='r')
fig2, ax = fn.plotOperation(esM, 'Electricity demand', 'building_2', color='r')
fig3, ax = fn.plotOperation(esM, 'CHP1', 'building_1')
fig4, ax = fn.plotOperation(esM, 'CHP1', 'building_2')
fig5, ax = fn.plotOperation(esM, 'CHP2', 'building_1')
fig6, ax = fn.plotOperation(esM, 'CHP2', 'building_2')
fig7, ax = fn.plotOperation(esM, 'CHP3', 'building_1')
fig8, ax = fn.plotOperation(esM, 'CHP3', 'building_2')
#fig88, ax = fn.plotOperation(esM, 'Battery1', 'building_1')
fig9, ax = fn.plotOperation(esM, 'Electricity grid', 'building_1', color='g')
fig10, ax = fn.plotOperation(esM, 'Electricity grid', 'building_2', color='g')
fig11, ax = fn.plotOperation(esM, 'Natural gas', 'building_1', color='g')
fig12, ax = fn.plotOperation(esM, 'Natural gas', 'building_2', color='g')


# Show optimization summary
dfss = esM.getOptimizationSummary("SourceSinkModel", outputLevel=2)
dfconv = esM.getOptimizationSummary("ConversionModel", outputLevel=2)
dfstor = esM.getOptimizationSummary("StorageModel", outputLevel=2)
with pd.ExcelWriter("Resultats.xlsx") as writer:
    dfss.to_excel(writer, sheet_name="SourceSink")
    dfconv.to_excel(writer, sheet_name="Conversion")
    dfstor.to_excel(writer, sheet_name="Storage")

# %% tags=["nbval-skip"]
#fig, ax = fn.plotOperationColorMap(esM, 'CHP1', 'building_1')


# # ### Storage
# #
# # Show optimization summary
#
# # %% tags=["nbval-skip"]
# esM.getOptimizationSummary("StorageModel", outputLevel=2)
#
# # %% tags=["nbval-skip"]
# fig, ax = fn.plotOperationColorMap(esM, 'Li-ion batteries', 'cluster_2',
#                                    variableName='stateOfChargeOperationVariablesOptimum')

plt.show()
