data = [9,9,9]
R = data[0]
z= data[0]
for n in range(1,len(data)):
    if data[n]>=R:
        R = data[n]
    elif data[n]<=z:
        z = data[n]
print n  
if data[n] == z and data[n] == R:
    print "Please enter at least two different numbers"
else:
    print "The maximum value in data is: " + str(R)
    print "The minimum value in data is: " + str(z)