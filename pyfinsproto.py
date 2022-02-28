import datetime
import sys
import threading
import HslCommunication
from HslCommunication import OmronFinsNet
import time 

class Write_type():
    def Write_Int16(self, address, input_data):
        result, add = self.omron.WriteInt16(address, input_data), address
        print('===================write data===================')
        print(result.IsSuccess, input_data)

    def Write_Int32(self, address, input_data):
        result, add = self.omron.WriteInt32(address, input_data), address
        print('===================write data===================')
        print(result.IsSuccess, input_data)

    def Write_Int64(self, address, input_data):
        result, add = self.omron.WriteInt64(address, input_data), address
        print('===================write data===================')
        print(result.IsSuccess, input_data)

    def Write_Float(self, address, input_data):
        result, add = self.omron.WriteFloat(address, input_data), address
        print('===================write data===================')
        print(result.IsSuccess, input_data)
        
    def Write_Bool(self, address, input_data):
        result, add = self.omron.WriteBool(address, input_data), address
        print('===================write data===================')
        print(result.IsSuccess, input_data)
        
class Read_type():     
    def Read_Int16(self, address):
        result, add = self.omron.ReadInt16(address, 100), address
        print('===================read data===================')
        print(result.Content[0])
        return result.Content[0]
        
    def Read_Int32(self, address):
        result, add = self.omron.ReadInt32(address, 100), address
        print('===================read data===================')
        print(result.Content[0])
        return result.Content[0]

    def Read_Int64(self, address):
        result, add = self.omron.ReadInt64(address, 100), address
        print('===================read data===================')
        print(result.Content[0])
        return result.Content[0]
    
    def Read_Float(self, address):
        result, add = self.omron.ReadFloat(address, 100), address
        print('===================read data===================')
        print(result.Content[0])
        return result.Content[0]
        
    def Read_Bool(self, address):
        result, add = self.omron.ReadBool(address, 100), address
        print('===================read data===================')
        print(result.Content[0])
        return result.Content[0]
        
class Omron_network(Read_type, Write_type):
    def __init__(self, port, host):
        self.port = port
        self.host = host
        self.code_name = code_name
        self.Connect()
        
    def Connect(self):
        self.omron = OmronFinsNet(self.port, self.host)
        self.connect = self.omron.ConnectServer()
        print("connection result : ", self.connect.IsSuccess)

    def Date_Diff_From_Today(self):
        stand_date = datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
        date1 = datetime.datetime.strptime(stand_date, '%Y-%m-%d %H:%M:%S')
        date2 = datetime.datetime.now()
        timedelta = date2 - date1
        self.recent_trans_time = int((timedelta.days * 24 * 3600 + timedelta.seconds) / 60)
        
    def Health_Send(self, health_add): 
        print("\nHealth data sending . . .")
        self.Date_Diff_From_Today()
        self.Write_Int16(health_add, self.recent_trans_time)
        
    def Health_Read(self, health_add):
        print("\nHealth data reading . . .")
        self.last_trans_time = self.Read_Int16(health_add) 
        
    def Health_Check(self, cycle_time):
        self.Date_Diff_From_Today()
        trans_delta = self.recent_trans_time - self.last_trans_time
        
        if datetime.datetime.now().hour > cycle_time + 5:
            if datetime.datetime.now().minute < cycle_time:
                trans_delta = trans_delta + 1440
                # cycle time: 10min
                # last : 59min ==> next : 9min ==> 9 - 1439 + 1440 = 10
                # last : 50min ==> next : 00min ==> 0 - 1430 + 1440 = 10
                # last : 55min ==> next : 5min ==> 5 - 1435 + 1440 = 10
                # last : 00min ==> next : 10min ==> 10 - 0 = 0
        print("\ntrans_delta: ",trans_delta)
        return trans_delta
        
    def Transfer_Check(self, trans_add, trans_on):
        if trans_on == True:
            print("\nTransfer data is about to turn on . . .")
            self.Write_Int16(trans_add, 1)
        else:
            print("\nTransfer data is about to turn off . . .")
            self.Write_Int16(trans_add, 0)
    