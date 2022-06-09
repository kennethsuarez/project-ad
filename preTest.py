import jpype
import jpype.imports
from jpype.types import *

jpype.startJVM(classpath=['/Users/Carlton/Documents/4th Year 1st Sem/CS 198199/project-ad/TTDM/target/classes'])

print("GenLocationMap")
genLocMap = jpype.JClass("com.mdm.sdu.mdm.model.taxi.GenLocationMap")
genLocMap.main([jpype.java.lang.String("/Users/Carlton/Documents/4th Year 1st Sem/CS 198199/project-ad/TTDM/input/Taxi_Train_Data.csv")])

print("GenTaxiDataGraph")
genTaxiDataGraph = jpype.JClass("com.mdm.sdu.mdm.model.taxi.GenTaxiDataGraph")
genTaxiDataGraph.main([jpype.java.lang.String("Taxi_graph.csv")])

print("MulThreadODPath")
mulThreadODPath = jpype.JClass("com.mdm.sdu.mdm.ksp.MulThreadODPath")
mulThreadODPath.main([])

print("DONE!")
