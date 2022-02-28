import datetime
import sys
import threading
import numpy as np
import HslCommunication
from HslCommunication import MelsecMcNet, MelsecMcAsciiNet, MelsecA1ENet
import time 
class Global(object):
    Available_addr = tuple(np.arange(65000, 65100))
    mode_addr = 'D' + str(Available_addr[0]) #D65000 
    current_data_addr = 'D' + str(Available_addr[1]) #D65001
    plc_command_addr = 'D' + str(Available_addr[2]) #D65002
    next_data_addr = 'D' + str(Available_addr[11]) #D65011
    apc_command_addr = 'D' + str(Available_addr[12]) #D65012    

class Write_type():
    def Write_Int16(self, address, input_data):
        result, add = self.melsec.WriteInt16(address, input_data), address
        print('===================write data===================')
        print("address: {} && value: {}".format(address, input_data))


    def Write_Int32(self, address, input_data):
        result, add = self.melsec.WriteInt32(address, input_data), address
        print('===================write data===================')
        print(result.IsSuccess, input_data)


    def Write_Int64(self, address, input_data):
        result, add = self.melsec.WriteInt64(address, input_data), address
        print('===================write data===================')
        print(result.IsSuccess, input_data)

    def Write_Float(self, address, input_data):

        result, add = self.melsec.WriteFloat(address, input_data), address
        print('===================write data===================')
        print(result.IsSuccess, input_data)

        
    def Write_Bool(self, address, input_data):
        result, add = self.melsec.WriteBool(address, input_data), address
        print('===================write data===================')
        print(result.IsSuccess, input_data)

        
class Read_type():     
    def Read_Int16(self, address):

        result, add = self.melsec.Read(address, 1), address
        print('===================read data===================')
        print("address: {} && value: {}".format(address, result.Content[0]))
        return result.Content[0]

        
    def Read_Int32(self, address):

        result, add = self.melsec.ReadInt32(address, 100), address
        print('===================read data===================')
        print("address: {} && value: {}".format(address, result.Content[0]))
        return result.Content[0]

    def Read_Int64(self, address):

        result, add = self.melsec.ReadInt64(address, 101), address
        print('===================read data===================')
        print("address: {} && value: {}".format(address, result.Content[0]))

    
    def Read_Float(self, address):
 
        result, add = self.melsec.ReadFloat(address, 100), address
        print('===================read data===================')
        print("address: {} && value: {}".format(address, result.Content[0]))
        return result.Content[0]


        
    def Read_Bool(self, address):

        result, add = self.melsec.ReadBool(address, 100), address
        print('===================read data===================')
        print("address: {} && value: {}".format(address, result.Content[0]))
        return result.Content[0]

            
class Melsec_network(Read_type, Write_type):
    def __init__(self, port, host, code_name = 'ASCII'):
        self.port = port
        self.host = host
        self.code_name = code_name
        self.Connect()
        
    def Connect(self):
        if self.code_name == 'ASCII':
            self.melsec = MelsecMcAsciiNet(self.port, self.host)
            print("ASCII Connection on")
        elif self.code_name == 'BINARY':
            self.melsec = MelsecMcNet(self.port, self.host)
            print("BINARY Connection on")        
        else:
            print("Check out code name")

        self.connect = self.melsec.ConnectServer()
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
            return True
        else:
            print("\nAPC is about to check if PLC has read previous data . . .")
            result = self.Read_Int16(trans_add)
            if result == 1:
                print("\nPLC has read data, so APC is going to reset check memory")
                self.Write_Int16(trans_add, 0)
                print("\nPLC MC protocol Callback memory has been reset")
                return True
            else:
                print("\nPLC has not read data, so APC does not need to reset check memory")
                return False

class TCP_to_PLC():
    def __init__(self, plc_type, ip, port):
        self.plc_type = plc_type
        self.ip = ip 
        self.port = port
        self.connect()
        self.reconnect()

    def connect(self):
        self.try_n = 0
        print("Number of connection trial:", self.try_n)
        if self.plc_type == 'MELSEC':
            self.net = Melsec_network(self.ip, self.port, code_name = 'BINARY') 
        elif self.plc_type == 'OMRON':
            self.net = Omron_network(self.ip, self.port) 

    def reconnect(self, timeout = 10):
        connect_trial_count = 0
        if self.net.connect.IsSuccess == False:
            while True:
                time.sleep(timeout)
                self.net.Connect() 
                connect_trial_count = connect_trial_count + 1
                print('connect retrial . . . count : {}'.format(connect_trial_count))
                if connect_trial_count > 3 or self.net.connect.IsSuccess == True: 
                    print('initial connect failed. please check PLC network')
                    break
    
    def Insert_data(self, addr, data):
        self.net.Write_Int16(addr, data) 

    def Read_data(self, addr):
        out = self.net.Read_Int16(address = addr)
        return out 
    def Trans_Check_data(self, trans_address1, trans_address2):
        result = self.net.Transfer_Check(trans_add = trans_address2, trans_on = False) #PLC check if read or not
        time.sleep(1)

        if result == True:
            self.net.Transfer_Check(trans_add = trans_address1, trans_on = True) # Get PLC ready to read new data
            time.sleep(1)
        
    def Protocol_Main(self, data, interval_time):
        # data parameter's type should be dictionary(json)
        if self.net.connect.IsSuccess == True: 
            self.Insert_data(data) 
            time.sleep(interval_time)
            self.Trans_Check_data(trans_address1 = Global.trans_address1, trans_address2 = Global.trans_address2) 
            time.sleep(interval_time)





if __name__ == '__main__':
  mc_proto = TCP_to_PLC(plc_type = 'MELSEC', ip = '172.23.74.69' ,  port = 8005)
  out = mc_proto.Read_data('D65000') #check mode 
  #print(out)
  
  #current_data = mc_proto.Read_data(Global.current_data_addr)
  #print(current_data)
  
  #mc_proto.Insert_data(Global.next_data_addr, 1) #write next gap data
  #mc_proto.Insert_data(Global.apc_command_addr, 1) #command apc to plc     
  #out2 = mc_proto.Read_data(Global.plc_command_addr) #command check from plc
    