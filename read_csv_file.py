#!/bin/python
import io
string = 'KP55109 '
monid = string[2:4]
camid = string[4:7]
print(camid)
list = []
try:
   fcsv = open('/home/c4988/share/HOK.txt','r')
   for line in fcsv:
       list = []
       for a in line.split(","):
           list.append(a.rstrip("\n"))
           if monid in list and camid in list:
              print(list)
              print(list[0])
              print(list.index(camid))
           print(a)
       print(line)
except TypeError:
   print("Error")
finally:
   fcsv.close()
