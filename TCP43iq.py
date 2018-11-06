# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 16:26:43 2018

@author: Admin
"""
import struct
import socket 
import csv

#starting string
#format  pad pad  databytes unitid/command startregister(-1) #to read
#       0000 0000   0006        4304          021b             0008 
# 0000 0000 0006 4304 021b 0008
#0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x43, 0x04, 0x02, 0x1b , 0x00, 0x08


class iq(object):
    
    def  __init__(self):
        self.ip = '192.168.1.200'
        self.port = 502
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip , self.port))

    def read_holding(self, start_adress, num_toread):
            
        """Read Holding/Input Registers reads the measurement data and current
        settings from the instrument. Issuing either of these function codes 
        will generate the same response. These functions read the contents of 
        one or more contiguous registers.
        
        Function Code         1 Byte   0x03 or 0x04
        Starting Address      2 Bytes  0x0000 to 0xFFFF
        Quantity of Registers 2 Bytes  0x0001 to 0x007D 
    
        """
        
        #convert both values to hex bytearray
        convert_adr = list(struct.pack('>h', start_adress -1))
        convert_toread = list(struct.pack('>h', num_toread))
        #add both together to prepart to add to starting array
        data = convert_adr + convert_toread
        command =[0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x43, 0x03] + data
        bytecommand = bytearray(command)
#        print(bytecommand)
        self.s.send(bytecommand)
        reply = self.s.recv(1048)
        print(reply)
        length = reply[5]
        print(length)
        returned_data = reply[8:]
        returned_data = returned_data[:-(int(num_toread)) or None]
        print(returned_data)
    
    def write_single(self, adress, write_value):
        
        """
        The Write Single Register is used to write a single register value.
                
        Function Code     1 Byte   0x06
        Starting Address  2 Bytes  0x0000 to 0xFFFF
        Register Value    2 Bytes  0x0000 to 0xFFFF 
        
        """
        
        convert_adr = list(struct.pack('>h', adress -1))
        convert_write_value = list(struct.pack('>h', write_value))
        data = convert_adr + convert_write_value
        command = [0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x43, 0x03] + data
        bytecommand = bytearray(command)
#        print(bytecommand)
        self.s.send(bytecommand)
        reply = self.s.recv(1048)
#        print(reply)
        length = reply[5]
        returned_data = reply[8:length]
        print(returned_data)
        
    def stream_data(self):
        """ streaming protocol"""
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect(('192.168.1.200',9881))
        while True:
            data = s2.recv(1048)
            data.decode()
            time = data[0:19]
            concentration = data[20:28]
            row = zip(time,concentration)
            with open('some.csv', 'a', newline = '' ) as outfile:
                writer= csv.writer(outfile)
                writer.writerow(row)
                
        
        
    #needs to be tested to understand how the data gets entered
#    def write_multiple(start_adress, quantity, write_values ):
#        
#        convert_adr = list(struct.pack('>h', start_adress -1))
#        convert_toread = list(struct.pack('>h', num_toread))
#        
#        
#        
#        command = [0x00, 0x00, 0x00, 0x00, 0x00, len_data , 0x43, 0x10]
    
   



        
        
        
    
    
    
       