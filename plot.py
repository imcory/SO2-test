# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 11:03:23 2018

@author: Written by Corydon Lee Myers a novice python programmer for purpose of 
monitoring gas flow rate through fujikin MFC. Code adapted from sparkfun
tutorial by Shawn Himmel on plotting live sensor data. Can add another source 
of data from a second flow controller. Graph can plot at about 1 per second.

Thoughts: Data storage could be written into a seperate script to allow for
quicker data polling. Blitting would also speed up the rate at which data could
be accesed but I was unable to get it to function. Also perhaps a more efficient
method would be to write a gui to access the fujipy driver and constantly
display flow rate of both controllers and also access fujipy methods
"""
import datetime as dt
import fujipy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#import numpy as np
import csv

MFC_one = fujipy.MFC(0x34)

#create plot and initialize empty list
def plotnstore():
    fig = plt.figure(1, figsize=(10, 6), frameon=False, dpi=100)
    ax = fig.add_subplot(1,1,1)
    flow = []
    time = []
#animation calls this function to continously update and format the plot    
    def animate(i, flow, time):
        
        
        if MFC_one.ser.is_open:
           
            time.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
            flow.append(MFC_one.indicated_flow()) #add last reading to array
            
            #max amount to display on plot
            time = time[-40:]
            flow = flow[-40:]
            
            ax.clear()
            ax.plot(time, flow)
            
            #plot format
            plt.xticks(rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.30)
            plt.title('Flowrate vs Time')
            plt.ylabel('Flowrate')
            
            #once length of array holding data gets too long data is appended 
            #to a csv and array is flushed
            if len(time) >= 40:
                with open('example.csv', 'a', newline='') as outfile:
                    writer = csv.writer(outfile)
                    rows = zip(time,flow)
                    for row in rows:
                        writer.writerow(row)
                        flow.clear()
                        time.clear()
        else:
            with open('test.csv', 'a', newline='') as outfile:
                    writer = csv.writer(outfile)
                    rows = zip(time,flow)
                    for row in rows:
                        writer.writerow(row)
                        flow.clear()
                        time.clear()
                        break
                    
    # animation function calls animate()                  
    ani = animation.FuncAnimation(fig , animate , fargs=(time, flow), interval=0)
    return ani
    plt.show()


    