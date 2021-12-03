import sys
from random import random

import plotly.graph_objects as go
import pandas as pd
from plot_functions import getData
import numpy as np
from labelDict import labelDict
from labelDict import labelPositionDict
from labelDict import fullPositionDict
from matplotlib import colors

BUILDINGSLIST = [1]

RESULTSFILE = "../data/Results/results1_1_group.xlsx"

UseLabelDict=True
OPACITY=0.6
ColorDict={"elec": 'rgba' + str(colors.to_rgba("skyblue", OPACITY)),
           "gas":'rgba'+str(colors.to_rgba("darkgray", OPACITY)),
           "dhw":'rgba'+str(colors.to_rgba("red", OPACITY)),
           "sh":'rgba'+str(colors.to_rgba("magenta", OPACITY)),
           "other":'rgba'+str(colors.to_rgba("lime", OPACITY))
           }

if UseLabelDict == True:
    PositionDict = labelPositionDict
else:
    PositionDict = fullPositionDict


def addCapacities(nodes, dataDict, buildings):
    capacities = ["sufficient"] * len(nodes)
    for i in buildings:
        capTransformers=dataDict["capTransformers__Building"+str(i)]
        capStorages=dataDict["capStorages__Building"+str(i)]
        for j, k in capStorages.iterrows():
            if k[0]==0:
                continue
            if UseLabelDict == True:
                index=nodes.index(labelDict[j])
            else:
                index = nodes.index(j)
            #nodes[index]=nodes[index]+" "+str(round(k[0],2))+" kWh"
            capacities[index]=str(round(k[0],1))+" kWh"
        for j, k in capTransformers.iterrows():
            if k[0]==0:
                continue
            j=j.split("'")[1]
            if UseLabelDict == True:
                index=nodes.index(labelDict[j])
            else:
                index = nodes.index(j)
            #nodes[index]=nodes[index]+" "+str(k[0])+" kW"
            capacities[index]=str(round(k[0],1))+" kW"
    return capacities


def readResults(fileName, buildings):
    dataDict = getData(fileName)
    keys=dataDict.keys()
    nodes, sources, targets, values,x,y, linkGroup = createSankeyData(dataDict, keys, buildings)
    capacities = addCapacities(nodes, dataDict, buildings)

    nodesColors=pd.Series(createColorList(nodes))
    linksColors = nodesColors[sources]
    dhwIndex = [a and b for a, b in zip((nodesColors[targets] == ColorDict["dhw"]), (nodesColors[sources] == ColorDict["sh"]))]
    linksColors = np.where(dhwIndex, ColorDict["dhw"], linksColors)
    shIndex = [a and b for a, b in zip((nodesColors[targets] == ColorDict["sh"]), (nodesColors[sources] == ColorDict["dhw"]))]
    linksColors = np.where(shIndex, ColorDict["sh"], linksColors)
    linksColors = np.where(nodesColors[targets] == ColorDict["elec"], ColorDict["elec"], linksColors)

    data = [go.Sankey(
        arrangement="snap",
        valuesuffix="kWh",
        node={
            "pad":25,
            "thickness":15,
            "line":dict(color="black", width=0.5),
            "label":nodes,#+str(values),
            "color":nodesColors.tolist(),
            #"groups":[linkGroup],
            "customdata": capacities,
            "hovertemplate":  '%{label} has %{customdata} capacity installed',
            "x":x,
            "y":y,
            },
        link={
            "source":sources,
            "target":targets,
            "value":values,
            "color":linksColors.tolist(),
            }
        )]
    return data


def createSankeyData(dataDict, keys, buildings=[]):
    sources = []
    targets = []
    nodes = []
    values = []
    x=[]
    y=[]
    linkGroup=[]
    for key in keys:
        df = dataDict[key]
        dfKeys = df.keys()
        if "dhwStorageBus" in key:
            continue
        if all([str(i) not in key for i in buildings]):
            continue
        for dfKey in dfKeys:
            if isinstance(dfKey, int):
                continue
            dfKeySplit = dfKey.split("'")
            sourceNodeName=dfKeySplit[1]
            targetNodeName =dfKeySplit[3]

            if UseLabelDict == True:
                sourceNodeName=labelDict[sourceNodeName]
                targetNodeName=labelDict[targetNodeName]
                if sourceNodeName==targetNodeName:
                    continue
                if "exSolar" in targetNodeName:
                    continue

            if "Resource" not in sourceNodeName:
                dfKeyValues = df[dfKey].values
                value = sum(dfKeyValues)
                if value < 0.001:
                    continue
                values.append(value)
                if sourceNodeName not in nodes:
                    nodes.append(sourceNodeName)
                    if "electricityLink" in sourceNodeName or "elLink"in sourceNodeName:
                        linkGroup.append(nodes.index(sourceNodeName))
                    for posKey in PositionDict.keys():
                        if posKey in sourceNodeName and posKey[0:2] == sourceNodeName[0:2]: #second part of the term added for CHP and HP
                            x.append(PositionDict[posKey][0])
                            if "electricityLink" in sourceNodeName or "elLink"in sourceNodeName:
                                y.append((0.5-(PositionDict[posKey][1]))/len(buildings))
                            else:
                                buildingNumber=buildings.index(int(sourceNodeName[-1]))
                                temp = (PositionDict[posKey][1]) / len(buildings) + (buildingNumber) / len(buildings)
                                y.append(temp)
                sources.append(nodes.index(sourceNodeName))

                if targetNodeName not in nodes:
                    nodes.append(targetNodeName)
                    if "electricityLink" in targetNodeName or "elLink"in targetNodeName:
                        linkGroup.append(nodes.index(targetNodeName))
                    for posKey in PositionDict.keys():
                        if posKey in targetNodeName and posKey[0:2] == targetNodeName[0:2]:
                            x.append(PositionDict[posKey][0])
                            if "electricityLink" in targetNodeName or "elLink"in targetNodeName:
                                y.append((0.5-(PositionDict[posKey][1]))/len(buildings))
                            else:
                                buildingNumber=buildings.index(int(targetNodeName[-1]))
                                temp = (PositionDict[posKey][1]) / len(buildings) + (buildingNumber) / len(buildings)
                                y.append(temp)
                targets.append(nodes.index(targetNodeName))
    return nodes, sources, targets, values, x, y, linkGroup


def createColorList(inputList):
    colorsList=[]
    for n in inputList:
        if "el" in n or "El" in n or "pv" in n or "grid" in n or "Bat" in n:
            color = ColorDict["elec"]
        elif "Gas" in n:
            color = ColorDict["gas"]
        elif "sh" in n or "SH" in n or "spaceHeating" in n:
            color = ColorDict["sh"]
        elif "dhw" in n or "DHW" in n or "domestic" in n or "solar" or "sc" in n:
            color = ColorDict["dhw"]
        else:
            color = ColorDict["other"]
        colorsList.append(color)
    return colorsList


def displaySankey(fileName, buildings=[1, 2, 3, 4]):
    data = readResults(fileName, buildings)

    node = data[0]['node']
    link = data[0]['link']
    fig = go.Figure(go.Sankey(arrangement = "perpendicular",
                              link=link,
                              node=node)) #snap, perpendicular,freeform, fixed
    fig.update_layout(
        title=fileName +" for buildings " + str(buildings),
        font=dict(size=10, color='black'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    fig.add_hline(y=0, line_color='rgba(0,0,0,0)')
    if len(buildings)%2==0:
        fig.add_hline(y=0.5, line_dash="dash")
    if len(buildings)%3==0:
        fig.add_hline(y=0.33, line_dash="dash")
        fig.add_hline(y=0.66, line_dash="dash")
    if len(buildings)%4==0:
        fig.add_hline(y=0.25, line_dash="dash")
        fig.add_hline(y=0.75, line_dash="dash")
    fig.add_hline(y=1.0, line_color='rgba(0,0,0,0)')
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig

def main():
    fig=displaySankey(RESULTSFILE, BUILDINGSLIST)
    fig.show()

if __name__ == "__main__":
    sys.exit(main())