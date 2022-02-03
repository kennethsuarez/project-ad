import jpype
import jpype.imports
from jpype.types import *


jpype.startJVM(classpath=['/Users/Carlton/Documents/4th Year 1st Sem/CS 198199/TTDM/target/classes'])

# print(jpype.java.lang.System.getProperty("java.class.path"))

TTDM = jpype.JClass("com.mdm.sdu.mdm.model.taxi.TTDM_Taxi")

jpype.java.lang.System.out.println("JPype")
 
TTDM.main([])


jpype.shutdownJVM()
