# PyCT4319
Python program for reading the conductivity sensor 4319 from Aanderaa

## Example

```
from sensor import CT4319

ct = CT4319()
ct.start_communication("/dev/ttyUSB0")
ct.set_outputdir("./data/")
while True:
    #collection for 1 minute and calculates average
    ct.do_mean()
    
    #print result
    print(ct.data_mean)
    
    #Export data to csv
    ct.to_csv()
    
    #40 minutes between averages
    time.sleep(40*60)
```
