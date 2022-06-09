import jpype
import jpype.imports
from jpype.types import *

# read visited coordinates
OUTPUT_PATH = 'output/visited.txt'
with open(OUTPUT_PATH) as f:
    visited_list = [x.rstrip() for x in f]
#print(visited_list)

# begin JPype operation
jpype.startJVM(classpath=['TTDM/target/classes'])

# print(jpype.java.lang.System.getProperty("java.class.path"))

TTDM = jpype.JClass("com.mdm.sdu.mdm.model.taxi.TTDM_Taxi")

#jpype.java.lang.System.out.println("JPype")
 
TTDM.train()
idx = "20000005,"
str = ",".join(visited_list)
#print(idx+str)
trajectory = jpype.java.lang.String(idx + str)
#testString = jpype.java.lang.String("20000005,30$93@1618927642000,30$97@1618927900000,30$98@1618927919000,30$99@1618928000000," \
#              "31$99@1618928003000,31$100@1618928039000,30$100@1618928059000,30$101@1618928072000," \
#              "30$102@1618928119000,30$103@1618928138000,31$103@1618928178000,31$102@1618928238000")

# testString2 = jpype.java.lang.String("20000005,30$104@1618928653000,30$103@1618928793000,30$102@1618928814000,"
#                                     "30$101@1618928834000,31$101@1618928854000,31$100@1618928930000,"
#                                     "31$99@1618928952000")

#output = TTDM.TTDM_Instance.predictHelper(testString)
# output2 = TTDM.TTDM_Instance.predictHelper(testString2)
output = TTDM.TTDM_Instance.predictHelper(trajectory)
#print(testString + " predicted: " + output)
# print(testString2 + " predicted: " + output2)
print(trajectory + " predicted: " + output)
jpype.shutdownJVM()
