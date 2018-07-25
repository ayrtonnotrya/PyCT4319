import pandas as pd
import serial
import time
import datetime
import numpy as np
import threading
import os
from serial import SerialException
from queue import Queue
from threading import Thread
from datetime import timedelta
from datetime import datetime

class CT4319():
    def __init__(self):

        self.ser = serial.Serial()
        self.q = Queue()
        self.t_stop = threading.Event()
        self.t = Thread(target=self.read_thread, args=(self.ser, self.q, self.t_stop))
        self.t.setDaemon(True)
        
        self.output_dir = ""
        
        self.conductivity = []
        self.temperature = []
        self.conductance = []
        self.salinity = []
        self.density = []
        self.soundspeed = []
        self.rawdata = []
        
        self.scan = 0
        self.last_output = 0
        self.last_len_mean = 0
        
        self.data = pd.DataFrame(columns = ["Scan", "Time", "Temperature[°C]",  "Condutivity[mS/cm]", 
                                            "Salinity[PSU]", "Density[kg/m3]", "Sound Speed[m/s]", "Conductance[S]"])
        
        self.data_mean = pd.DataFrame(columns = ["Scans", "Initial Time", "Final Time", "Temperature[°C]",  
                                                 "Condutivity[mS/cm]", "Salinity[PSU]", "Density[kg/m3]", 
                                                 "Sound Speed[m/s]", "Conductance[S]"])
        
        self.properties = {"Product Name":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":31,
                                          "Use":"AADI Product name",
                                          "Access Protection":"Read Only"},
                          "Product Number":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":6,
                                          "Use":"AADI Product number",
                                          "Access Protection":"Read Only"},
                          "Serial Number":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"INT",
                                          "No of elements":1,
                                          "Use":"Serial Number",
                                          "Access Protection":"Read Only"},
                          "SW ID":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":11,
                                          "Use":"Unique identifier for internal firmware",
                                          "Access Protection":"Read Only"},
                          "Software Version":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"INT",
                                          "No of elements":3,
                                          "Use":"Software version (Major, Minor, Built)",
                                          "Access Protection":"Read Only"},
                          "HW ID X":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":19,
                                          "Use":"Hardware Identifier, X =1..3",
                                          "Access Protection":"Read Only"},
                          "HW Version X":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":9,
                                          "Use":"Hardware Identifier, X =1..3",
                                          "Access Protection":"Read Only"},
                          "System Control":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"INT",
                                          "No of elements":3,
                                          "Use":"For AADI service personnel only",
                                          "Access Protection":"Read Only"},
                          "Production Date":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":31,
                                          "Use":"AADI production date, format YYYY-MM-DD",
                                          "Access Protection":"Read Only"},
                          "Last Service":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":31,
                                          "Use":"Last service date, format YYYY-MM-DD, empty by default",
                                          "Access Protection":"Read Only"},
                          "Last Calibration":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":31,
                                          "Use":"Last calibration date, format YYYY-MM-DD",
                                          "Access Protection":"Read Only"},
                          "Calibration Interval":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"INT",
                                          "No of elements":1,
                                          "Use":"Recommended calibration interval in days",
                                          "Access Protection":"Read Only"},
                          "Interval":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":1,
                                          "Use":"Sampling Interval in seconds",
                                          "Access Protection":"Low"},
                          "Location":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":31,
                                          "Use":"User setting for location",
                                          "Access Protection":"Low"},
                          "Geographic Position":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":31,
                                          "Use":"User setting for geographic position",
                                          "Access Protection":"Low"},
                          "Vertical Position":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":1,
                                          "Use":"User setting for describing sensor position",
                                          "Access Protection":"Low"},
                          "Reference":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":31,
                                          "Use":"User setting for describing sensor reference",
                                          "Access Protection":"Low"},
                          "Pressure":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":1,
                                          "Use":"Water pressure in kPa",
                                          "Access Protection":"High"},
                          "Mode":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"ENUM",
                                          "No of elements":1,
                                          "Use":"Sets the sensor operation mode (AiCaP, Smart Sensor Terminal, AADI Real-Time, Smart Sensor Terminal FW2)",
                                          "Access Protection":"High"},
                          "Enable Sleep":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"BOOL",
                                          "No of elements":1,
                                          "Use":"Enable sleep modeSets the sensor operation mode (AiCaP, Smart Sensor Terminal, AADI Real-Time, Smart Sensor Terminal FW2)",
                                          "Access Protection":"High"},
                          "Enable Polled Mode":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"BOOL",
                                          "No of elements":1,
                                          "Use":"Enable polled mode (for RS232). When set to ‘no’ the sensor will sample at the interval given by the Interval property. When set to ‘yes’ the sensor will wait for a Do Sample command.",
                                          "Access Protection":"High"},
                          "Enable Text":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"BOOL",
                                          "No of elements":1,
                                          "Use":"Controls the insertion of descriptive text, i.e. parameter names",
                                          "Access Protection":"High"},
                          "Enable Decimalformat":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"BOOL",
                                          "No of elements":1,
                                          "Use":"Controls the use of decimal format in the output string",
                                          "Access Protection":"High"},
                          "Enable Temperature":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"BOOL",
                                          "No of elements":1,
                                          "Use":"Controls inclusion of Temperature in the output string",
                                          "Access Protection":"High"},
                          "Enable Derived Parameters":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"BOOL",
                                          "No of elements":1,
                                          "Use":"Controls inclusion of Salinity, Density and Speed of sound in the output string",
                                          "Access Protection":"High"},
                          "Enable Rawdata":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"BOOL",
                                          "No of elements":1,
                                          "Use":"Controls inclusion of Conductivity in the output string",
                                          "Access Protection":"High"},
                          "Node Description":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":31,
                                          "Use":"User text for describing node, placement etc",
                                          "Access Protection":"High"},
                          "Owner":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"String",
                                          "No of elements":31,
                                          "Use":"User setting for owner",
                                          "Access Protection":"High"},
                          "Baudrate":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"ENUM",
                                          "No of elements":1,
                                          "Use":"RS232 baudrate: 4800, 9600, 57600, or 115200. Default baudrate is 9600",
                                          "Access Protection":"High"},
                          "Flow Control":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"BOOL",
                                          "No of elements":1,
                                          "Use":"RS232 flow control: ‘None’ or ‘Xon/Xoff’",
                                          "Access Protection":"High"},
                          "Enable Comm Indicator":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"BOOL",
                                          "No of elements":1,
                                          "Use":"Enable communication sleep (’%’) and communication ready (‘!’) indicators",
                                          "Access Protection":"High"},
                          "Comm TimeOut":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"ENUM",
                                          "No of elements":1,
                                          "Use":"RS232 communication activation timeout: Always On,10 s,20 s,30 s,1 min,2 min,5 min,10 min",
                                          "Access Protection":"High"},
                          "TempCoef":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":6,
                                          "Use":"Curve fitting coefficients for the temp measurements.",
                                          "Access Protection":"High"},
                          "R0Coef0":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 0",
                                          "Access Protection":"High"},
                          "R0Coef1":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 0",
                                          "Access Protection":"High"},
                          "R0Coef2":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 0",
                                          "Access Protection":"High"},
                          "R0Coef3":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 0",
                                          "Access Protection":"High"},
                          "R0Coef4":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 0",
                                          "Access Protection":"High"},
                          "R1Coef0":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "R1Coef1":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "R1Coef2":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "R1Coef3":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "R1Coef4":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "R1Coef5":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "R1Coef6":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "R1Coef7":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "R1Coef8":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "R1Coef9":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":4,
                                          "Use":"Temp Coefficients for Loop reading to Conductance, Range 1",
                                          "Access Protection":"High"},
                          "CellCoef":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"Float",
                                          "No of elements":1,
                                          "Use":"Cell constant for converting mS to mS/cm",
                                          "Access Protection":"High"},
                          "Range":{"Value":"",
                                           "Last Value Update":"",
                                          "Type":"INT",
                                          "No of elements":1,
                                          "Use":"Range setting: -1=Auto range, 0=Low range, 1=High range",
                                          "Access Protection":"High"}}

    def start_comm(self, port, baudrate):
        try:
            self.ser.port = port
            self.ser.baudrate = baudrate
            self.ser.open()
            self.t.start()
        except SerialException:
            print("Error communicating with the device!")
            print("Make sure the device and baudrate are correct!")
            print("Device = " + port)
            print("Baudrate = " + str(baudrate))

    def close_comm(self):
        self.t_stop.set()
        self.ser.close()

    def send_cmd(self, cmd):
        if self.ser.isOpen():
            self.ser.write(cmd.encode())

    def read_thread(self, ser, q, stop_event):
        while (not stop_event.is_set()):
            if ser.isOpen():
                q.put([str(ser.readline()), datetime.now()])
                time.sleep(0.01)

    def read_serialbuff(self):
        data = []
        while self.q.qsize() > 0:
            data.append(self.q.get())

        return data
    
    def clean_serialbuff(self):
        while len(self.read_serialbuff()) > 0:
            pass
        
    def get_property(self, prop):
        if prop not in self.properties.keys():
            return "Property not found!"
        else:
            self.send_cmd("Set Passkey(1000)\r\n")
            self.clean_serialbuff()
            self.send_cmd("Get "+prop+"\r\n")
            time.sleep(0.2)
            
            ret = self.read_serialbuff()
            for line in ret:
                line_list = line[0].replace("b'","").replace("\\r\\n'","").replace("\\x13\\x11","").split("\\t")
                for item in line_list:
                    if prop.lower() == item.lower():
                        self.properties[prop]["Value"] = line_list[3:]
                        self.properties[prop]["Last Value Update"] = line[1]
                    elif "ERROR" == item.lower():
                        return line_list[-1]
                    
            self.send_cmd("Set Passkey(1)\r\n")
                    
        
        return self.properties[prop]
    
    def get_all_property(self):
        for prop in self.properties.keys():
            self.get_property(prop)
        
        return self.properties
    
    def set_outputdir(self, output_dir):
        if os.path.isdir(output_dir):
            if "/" in output_dir[-1]:
                self.output_dir = output_dir
            else:
                self.output_dir = output_dir+"/"
        else:
            print("Diretório invalido!")
            
    def to_csv(self, data_mean = False, data = False):
        if self.output_dir is not "":
            if data:
                if self.last_output < self.data["Scan"].iloc[-1]:
                    df = self.data[self.data["Scan"] > self.last_output]
                    self.last_output = self.data["Scan"].iloc[-1]
                else:
                    df = self.data

                csvFilePath = self.output_dir+"td263data.csv"
                if not os.path.isfile(csvFilePath):
                    df.to_csv(csvFilePath, mode='a', index=False)
                else:
                    df.to_csv(csvFilePath, mode='a', index=False, header=False)

            if data_mean:
                if self.last_len_mean < len(self.data_mean):
                    df = self.data_mean[self.last_len_mean:]
                    self.last_len_mean = len(self.data_mean)
                else:
                    df = self.data_mean

                csvFilePath = self.output_dir+"td263data_mean.csv"
                if not os.path.isfile(csvFilePath):
                    df.to_csv(csvFilePath, mode='a', index=False)
                else:
                    df.to_csv(csvFilePath, mode='a', index=False, header=False)
        else:
            print("Não foi configurado um diretório de destino!")
            print("Use a função set_outputdir(output_dir).")
            
    def do_measurement(self):       
        self.clean_serialbuff()
        
        self.send_cmd("Do Sample\r\n")
        
        time.sleep(1)
        
        ret = self.read_serialbuff()
        
        for line in ret:
            line_list = line[0].replace("b'","").replace("\\r\\n'","").replace("\\x13\\x11","").split("\\t")
            if "MEASUREMENT" in line_list[0]:
                self.conductivity.append([float(line_list[4]), line[1]])
                self.temperature.append([float(line_list[6]), line[1]])
                self.salinity.append([float(line_list[8]), line[1]])
                self.density.append([float(line_list[10]), line[1]])
                self.soundspeed.append([float(line_list[12]), line[1]])
                self.conductance.append([float(line_list[14]), line[1]])
                self.data.loc[self.scan] = {"Scan": self.scan, "Time": line[1], 
                                            "Temperature[°C]":    float(line_list[6]), 
                                            "Condutivity[mS/cm]": float(line_list[4]), 
                                            "Salinity[PSU]":      float(line_list[8]), 
                                            "Density[kg/m3]":     float(line_list[10]), 
                                            "Sound Speed[m/s]":    float(line_list[12]),
                                            "Conductance[S]":     float(line_list[14])}
                self.scan += 1
        
    def do_mean(self, dt=timedelta(minutes=0)):        
        
        init = self.scan
        
        start = datetime.now()
        while (datetime.now() - start) < dt:
            self.do_measurement()
        
        data = self.data[init:]
        scan = len(self.data_mean)+1
        
        self.data_mean.loc[scan] = {"Scans": (self.scan-init), "Initial Time": start, "Final Time": datetime.now(), 
                                    "Temperature[°C]":    data["Temperature[°C]"].mean(), 
                                    "Condutivity[mS/cm]": data["Condutivity[mS/cm]"].mean(), 
                                    "Salinity[PSU]":      data["Salinity[PSU]"].mean(), 
                                    "Density[kg/m3]":     data["Density[kg/m3]"].mean(), 
                                    "Sound Speed[m/s]":    data["Soundspeed[m/s]"].mean(), 
                                    "Conductance[S]":     data["Conductance[S]"].mean()}
