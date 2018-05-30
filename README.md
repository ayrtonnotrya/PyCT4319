# PyCT4319
Python program for reading the conductivity sensor 4319 from Aanderaa
## Example
```
ct = CT4319()
ct.start_communication("/dev/ttyUSB0")
ct.set_outputdir(os.getcwd())
while True:
    #coleta por 1 minuto e calcula média
    ct.do_mean()
    
    #imprime resultado
    print(ct.data_mean)
    
    #Exporta os dados para csv
    ct.to_csv()
    
    #40 minutos entre as médias
    time.sleep(10)

```
