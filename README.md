# PyCT4319
Python program for reading the conductivity sensor 4319 from Aanderaa

## Example

```
from sensor import CT4319

ct = CT4319()
ct.start_comm(port = "/dev/ttyUSB0", baudrate = 9600)
ct.set_outputdir(output_dir = "./data/")
while True:
    #read the sensor for 10 minute and calculates average
    ct.do_mean(dt=timedelta(minutes=10))
    
    #print the pandas dataframe with the averages
    print(ct.data_mean)
    
    #Export data to csv
    ct.to_csv(data_mean = True)
    
    #50 minutes between averages
    time.sleep(50*60)
```
