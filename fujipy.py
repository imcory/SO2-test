# -*- coding: utf-8 -*-
"""
Fujikin MFC driver- written by Corydon Lee Myers a novice python programmer
for an internship experiment where two MFCs are inteded to be automated to 
control dilution

This module functions as a driver for the Fujikin T-1000M mass flow controlers
but should work with other models as well. A usb to RS485 adapter must be used 
to allow for serial communication.

Contained in this module is the MFC class which itself contains many attributes
and methods required to operate MFCs through serial communication. Pyserial
documentation can be referenced for ser functions. This module contains an
abbreviated series of commands formatted as given in the Fujikin RS485 Command 
Reference. These commands can be used for the automation of an expert and can
be imported to allow for construction of further functions to allow for 
continous polling of flowrate or for dilution using multiple MFC's

quick notes
    * ser.port- port will be needed to changed to the one in use
    
    * MAC ID in hex needs to be passed in the automation script to instantiate
      an MFC object eg MFC_one = fujipy.MFC(0x01)
      
    * Commands can be called with: 
        
        MFC_one.example_command() 
    
      the command may prompt an input and will automatically send and recieve 
      data
      
    * It is reccomended to close the serial port at the end of the script so as 
      not to occupy the port this can be done by with either:
          
          fujipy.MFC.ser.close()
          
      or by calling an instance of the MFC object
      
          MFC_one.ser.close()
          
      or by accessing the close_serial method through
      
          MFC_one.close_serial() or fujipy.MFC.close_serial()
"""

import serial
import csv
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class MFC(object):
    
    """This Class stores the serial attributes and allows for instatiation of
    MFC instances which can access the methods in this class to allow for
    operation of multiple MFCs
    
    Public methods include commands formatted in accordance with the fujikin
    command reference. Not all commands given in the manual are available but
    more can be added by using the existing as a template
    
    in the format of
    
    def some_command(self, some data to send):
            
        command_list = [
        self.MacID, 0x02,--> inputs instance MAC ID, 0x02 = start code
        0x81,-----------> 0x80 for read or 0x81 for write
        0x04,-----------> data bytes to send, 3 bytes for command adress+ data bytes
        0x66, 0x01, 0x02,--> Command adress as given in manual
        some data to send,-> data to send (options given in manual to write)
        0x00  -----------> indicates end of command
        ] 
        
    This next portion references the private _cmd_construct method which
    calculates and appends the checksum onto the command list. It also references
    the private send command function to send the command. Also, depending on 
    the command it can be specified to recieve an integer or text.
        
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        time.sleep(.1)
        self._receive_int() or seld._receive_tect()
    
    """
    
    ser = serial.Serial()
    ser.port = 'COM4'  #Needs to be changed depending on port being used
    ser.baudrate = 38400
    ser.timeout = 1
    ser.close()
    ser.open()
    
#    try:
#        if ser.is_open == False:
#            ser.open()
#    except SerialException:
#        print("something is occupying the port )
       
        
    def __init__(self, MacID):
        self.MacID = MacID
        #calls methods when class is instantiated to ensure the physical MFC is
        #in the correct operating state (digital mode and freeze follow off)
        print("ensuring MFC is in digital mode with freeze follow off")
        self.defualt_control_mode(0x01)
        self.freeze_follow( 0x01)
         
    def control_mode_select(self, selection): 
        command_list = [self.MacID , 0x02 , 0x81 , 0x04 ,
                        0x69, 0x01, 0x03, selection, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        self._receive_int()
 
    def defualt_control_mode(self, selection):
        command_list = [self.MacID , 0x02, 0x81, 0x04,
                        0x69, 0x01, 0x04, selection, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        self._receive_int()          
        
    def read_control_mode(self):
        command_list = [self.MacID, 0x02, 0x80, 0x03,
                        0x69, 0x01, 0x03, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        self._recieve_text()
          
    def freeze_follow(self, selection): 
        command_list = [self.MacID, 0x02, 0x81, 0x04,
                        0x69, 0x01, 0x05, selection, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        self._receive_int()
        
#    def write_macid(self, new_MacID): #FIX!!!!!
#        command_list = [self.MacID, 0x02, 0x81, 0x04,
#                        0x03, 0x01, 0x01, new_MacID, 0x00]
#        final_command = self._cmd_construct(command_list)
#        self._send_command(final_command)
#        self._receive_int()
        
    def serial_number(self):
        command_list = [self.MacID, 0x02, 0x80, 0x03,
                        0x64, 0x01, 0x07, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        self._recieve_text()
           
    def gas_identifier(self):
        command_list = [self.MacID , 0x02, 0x80, 0x03,
                        0x66, 0x01, 0x01, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        self._recieve_text()
             
    def full_scale_range(self):
        command_list = [self.MacID, 0x02, 0x80, 0x03,
                        0x66, 0x01, 0x02, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        reply = self._receive_int()
        print(reply)
        
        
    def flow_units(self):
        command_list = [self.MacID , 0x02, 0x80, 0x03,
                        0x66, 0x01, 0x03, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        self._recieve_text()
        
    def read_freeze_follow(self):
        command_list = [self.MacID, 0x02, 0x80, 0x03,
                        0x69, 0x01, 0x05, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        reply = self._receive_int()
        print(reply)
           
    def setpoint(self, target_flow): #fix note self.full scale range causes this problem
        
        #converts target to format given in MFC documentation
        convert_target = (((target_flow / 30) *32768) + 16384)
        #round to nearest digit
        rounded_target = int(convert_target)
        #convert to hex value in form 0xabcd
        hexed_target = hex(rounded_target)
        #convert to int to add to command list splits target. 
        #Val1 takes 0xab val2 takes bc
        value_1 = int(hexed_target[0:4], 16)
        value_2 = int('0x' + hexed_target[4:6] ,16)
        #insert split target in little endian order. (is there a better way?)
        print(value_1, value_2)
        command_list = [self.MacID , 0x02, 0x81, 0x05,
                        0x69, 0x01, 0xA4, value_2, value_1, 0x00]
        print(command_list)
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        reply = self._receive_int()
        print(reply)
    
    def read_setpoint(self):
        command_list = [self.MacID, 0x02, 0x80, 0x03,
                        0x69, 0x01, 0xA4, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        reply = self._receive_int()
        print(reply)
        
    def filtered_setpoint(self):
        command_list = [self.MacID, 0x02, 0x80, 0x03,
                        0x6A, 0x01, 0xA6, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        reply = self._receive_int()
        print(reply)
    
    def indicated_flow(self): 
        command_list = [self.MacID, 0x02, 0x80, 0x03,
                        0x6A, 0x01, 0xA9, 0x00]
        final_command = self._cmd_construct(command_list)
        self._send_command(final_command)
        #do reverse of setpoint() method to return flow value
        returned_value = self._receive_int()
        decoded_value = (returned_value - 16384) * (30 / 32768)
        decoded_value = round(decoded_value , 4)
        return(decoded_value)
        
    def _cmd_construct(self, command_list):
        
        """This method takes the command list from one of the command methods
        and calculates the checksum and appends it onto the end of the command
        the full command can then be sent. The checksum is the sum of all
        values after the MAC ID. This is intended as a private method only 
        accesed by the other command methods"""
        
        checksum = (sum(command_list[1:])) #sum of everything after MAC ID
        if checksum >= 255:
            checksum %= 0x100 #divides to reduce to last two digits
        command_wcheck = command_list + [checksum]
        byte_command = bytearray(command_wcheck)
        return byte_command        
   
    @staticmethod
    def _send_command(final_command):
        MFC.ser.write(final_command)
    
    @staticmethod
    def _recieve_text():
        """method decodes data sent in text format"""
        try:
            recieved = MFC.ser.read(100)
            #takes index 4 of returned byte array which represents data length
            #and converts it to an integer
            data_length =int(recieved[4]) 
            #removes all unnecsary value by slicing everything but returned
            # data from the recieved byte array                              
            returned_data = recieved[8:9+int(data_length)-4]
            print(returned_data)
        except IndexError:
            print("INDEX ERROR: No message was recieved."
                  "the command is likely being sent to an invalid MAC ID"
                  "or the MFC has no power. The port will now close to reset" 
                  "the program")
            MFC.ser.close()
            
    @staticmethod
    def _receive_int():
        try:
            recieved = MFC.ser.read(100)
            #error handling (better way?). Closes serial on error to not hug port
            if recieved == (b'\x16'):
                print("there was an error in the command sent. Closing serial "
                      "port for next attempt")
                MFC.ser.close()
            elif recieved == (b'\x06\x06'):
                print("write command has processed, change complete")
            elif recieved == (b'\x06\x16'):
                print("write command was recieved but has encountered an error")
                MFC.ser.close()
            else:
                #4th value in returned byte array is data sequence lenght
                #if value is 4 then thier is 1 byte of data as the value of 3
                #is the defualt and taken up by the commands address
                data_length = int(recieved[4])
                if data_length > 1:
                    returned_data = recieved[8:9+int(data_length)-4]
                    final = int.from_bytes(returned_data,
                                           byteorder='little', 
                                           signed =False
                                           )
                    return(final)
                    
                else:
                    returned_data = recieved[8:9+int(data_length)-4]
                    print(returned_data)
        except IndexError:
            print("INDEX ERROR: No message was recieved."
                  "the command is likely being sent to an invalid MAC ID"
                  "or the MFC has no power. The port will now close to reset" 
                  "the program")
            MFC.ser.close()
 
    @staticmethod
    def close_serial():
        MFC.ser.close()
        print(MFC.ser)
        
        """plotting and logging"""          
  
    def plotnstore(self):
        #can only be called from console and not another script why???
        fig = plt.figure(1, figsize=(10, 6), frameon=False, dpi=100)
        ax = fig.add_subplot(1,1,1)
        
        flow_lst = []
        time_lst = []
        
        outfile = open('test.csv', 'a', newline='')
        writer = csv.writer(outfile)
        #animation calls this function to continously update and format the plot    
        def animate(i, flow_lst, time_lst, outfile ,writer):

            if MFC.ser.is_open:
                
                flow = self.indicated_flow() 
                times = dt.datetime.now().strftime('%H:%M:%S.%f')
                writer.writerow([times, flow])
                outfile.flush()
                
                flow_lst.append(flow)
                time_lst.append(times)
                
                #max amount to display on plot
                time_lst = time_lst[-40:]
                flow_lst = flow_lst[-40:]
                
                ax.clear()
                ax.plot(time_lst, flow_lst)
                
                #plot format
                plt.xticks(rotation=45, ha='right')
                plt.subplots_adjust(bottom=0.30)
                plt.title('Flowrate vs Time')
                plt.ylabel('Flowrate')
                         
        ani = animation.FuncAnimation(fig , animate , fargs=(time_lst, flow_lst, outfile, writer), interval=0)
        #code stops here if not being called from console why???
        return ani
        plt.show()
        
        
        

        

    
    
    
    
    
    
  
    
    
    
    
    
    
    