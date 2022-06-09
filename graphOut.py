import numpy as np
import matplotlib as matplotlib
import matplotlib.pyplot as plt
from datetime import datetime

rr = open("output/rr.txt", "r")

rrx = []
rryu = []
rryp = []

while True:

    line = rr.readline()

    if not line:
        break

    if "current location" in line:
        splitline = line.split()
        rrx.append(splitline[-1][0:8])

    if "Util" in line:
        temp = []
        splitline = line.split()
        temp.append(splitline[1].strip("total:,"))
        temp.append(splitline[2].strip("mean:,"))
        temp.append(splitline[3].strip("sd:,"))
        rryu.append(temp)

    if "Plays" in line:
        temp = []
        splitline = line.split()
        temp.append(splitline[1].strip("total:,"))
        temp.append(splitline[2].strip("mean:,"))
        temp.append(splitline[3].strip("sd:,"))
        rryp.append(temp)

#print(rrx)
#print(rryu)
#print(rryp)

rrx1 = list(map(lambda x : datetime.strptime(x, '%H:%M:%S'),rrx))
rrx2 = list(map(lambda x :(x-rrx1[0]).total_seconds(),rrx1))
#print(x2)

rrp = open("output/rrpred.txt", "r")

rrpx = []
rrpyu = []
rrpyp = []

while True:

    line = rrp.readline()

    if not line:
        break

    if "current location" in line:
        splitline = line.split()
        rrpx.append(splitline[-1][0:8])

    if "Util" in line:
        temp = []
        splitline = line.split()
        temp.append(splitline[1].strip("total:,"))
        temp.append(splitline[2].strip("mean:,"))
        temp.append(splitline[3].strip("sd:,"))
        rrpyu.append(temp)

    if "Plays" in line:
        temp = []
        splitline = line.split()
        temp.append(splitline[1].strip("total:,"))
        temp.append(splitline[2].strip("mean:,"))
        temp.append(splitline[3].strip("sd:,"))
        rrpyp.append(temp)


rrpx1 = list(map(lambda x : datetime.strptime(x, '%H:%M:%S'),rrpx))
rrpx2 = list(map(lambda x :(x-rrpx1[0]).total_seconds(),rrpx1))

ubs = open("output/ubs.txt", "r")

ubsx = []
ubsyu = []
ubsyp = []

while True:

    line = ubs.readline()

    if not line:
        break

    if "current location" in line:
        splitline = line.split()
        ubsx.append(splitline[-1][0:8])

    if "Util" in line:
        temp = []
        splitline = line.split()
        temp.append(splitline[1].strip("total:,"))
        temp.append(splitline[2].strip("mean:,"))
        temp.append(splitline[3].strip("sd:,"))
        ubsyu.append(temp)

    if "Plays" in line:
        temp = []
        splitline = line.split()
        temp.append(splitline[1].strip("total:,"))
        temp.append(splitline[2].strip("mean:,"))
        temp.append(splitline[3].strip("sd:,"))
        ubsyp.append(temp)

ubsx1 = list(map(lambda x : datetime.strptime(x, '%H:%M:%S'),ubsx))
ubsx2 = list(map(lambda x :(x-ubsx1[0]).total_seconds(),ubsx1))


ubsp = open("output/ubspred.txt", "r")

ubspx = []
ubspyu = []
ubspyp = []

while True:

    line = ubsp.readline()

    if not line:
        break

    if "current location" in line:
        splitline = line.split()
        ubspx.append(splitline[-1][0:8])

    if "Util" in line:
        temp = []
        splitline = line.split()
        temp.append(splitline[1].strip("total:,"))
        temp.append(splitline[2].strip("mean:,"))
        temp.append(splitline[3].strip("sd:,"))
        ubspyu.append(temp)

    if "Plays" in line:
        temp = []
        splitline = line.split()
        temp.append(splitline[1].strip("total:,"))
        temp.append(splitline[2].strip("mean:,"))
        temp.append(splitline[3].strip("sd:,"))
        ubspyp.append(temp)

ubspx1 = list(map(lambda x : datetime.strptime(x, '%H:%M:%S'),ubspx))
ubspx2 = list(map(lambda x :(x-ubspx1[0]).total_seconds(),ubspx1))

plt.plot(rrx2,list(map(lambda x : float(x[1]),rryu)),c="red",label="rr")
plt.plot(rrpx2,list(map(lambda x : float(x[1]),rrpyu)),c="orange",label="rrpred")
plt.plot(ubsx2,list(map(lambda x : float(x[1]),ubsyu)),c="blue",label="ubs")
plt.plot(ubspx2,list(map(lambda x : float(x[1]),ubspyu)),c="green",label="ubspred")
plt.legend(loc='upper right')
plt.xlabel('Time elapsed (s)')
plt.ylabel('Average Utility')
plt.show()


