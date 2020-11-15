import random
import numpy as np
import math
import matplotlib.pyplot as plt
import os
from funtions import *
from agentpolicy import *
from Edgeserver_class import *
from Vehicle_class import *
###############Parameters##########################
Num_Users=10
Num_Edge=10
Limit=4
Max_No_Steps=3000
Num=92
#Resource Bound
bound_r=1e9*0.063
#Bandwidth Bound
bound_b=1e9

# Creating a class for vehicles for the vehiclular networking
class Vehicle():
    def __init__(self, vehicleid, data):
        self.vehicleid=vehicleid
        #coordinates x and y of the location
        self.loc=np.zeros((1,2))
        #this gives the number of steps
        self.steps=0

        #now to calculate the number of steps for the vehicle
        data=str("%03" % (data+1))
        file= "This contains the location data for the"
        f1=file.readlines()
        #reading data from the location data file
        data1=0
        for datalines in f1:
            data1+=1
        self.steps=data1*30
        #getting the vehicle coordinates
        self.veh=np.zeros((self.steps,2))

        #Now writing the data to veh(vehicle) afater getting the vehicle coordinates
        sector=0
        for datalines in f1:
            for sector1 in range(30):
                #now setting the corrdinates of the vehicle in the location
                self.veh[sector+sector1][0]=datalines.split()[1] # this the x coordiate
                self.veh[sector + sector1][1] = datalines.split()[2]  # this the y coordiate
            sector+=30
        self.loc[0]=self.veh

    #this function is used to send the request for the resource to the edge server
    def requestforresource(self,edge_id):
        self.request=vehiclerequests(self.vehicleid,edge_id)

   # this function is used to update the vehicle request to states
    def updaterequest(self):
        #request state ==5 means disconnection,  6 means migration default
        if self.request.state==5:
            self.request.timer +=1

        else:
            self.request.timer = 0
            if self.request.state==0:
                self.request.state=1
                #this is for vehicle to edge request
                self.request.veh2edgesize=self.request.tasktype.request_veh2edgesize
                self.request.veh2edgesize -= rate_transfer(self.loc,self.request.edge_location)

            elif self.request.state==1:
                if self.request.veh2edgesize>0:
                    self.request.veh2edgesize -=rate_transfer(self.loc, self.request.edge_location)

                else:
                    self.request.state=2
                    self.request.process_size=self.request.tasktype.process_loading
                    self.request.process_size-=self.request.resource
            elif self.request.state==2:
                if self.request.process_size>0:
                    self.request.process_size -= self.request.resource

                else:
                    self.request.state=3
                    self.request.edge2vehsize=self.request.tasktype.request_edge2vehsize
                    #todo taking random value for now
                    #this is for edge to vehicle request
                    self.request.edge2vehsize-=1000

            else:
                if self.request.edge2vehsize>0:
                    self.request.edge2vehsize-=1000 #formula
                else:
                    self.request.state=4
    # this function updates the mobility of the vehicle as the vehicle is moving
    def vehiclemobilityupdate(self,time):
        if time <len(self.veh[:,0]):
            self.loc[0]=self.veh[time]

        else:
            #this sets the loctation to infinity
            self.loc[0][0]=np.inf
            self.loc[0][1]=np.inf
# this class handles the request for differnt vehicles that need resources from edge
class vehiclerequests():
    def __init__(self,vehicleid,edge_id):
        #The ids of the vehicle and the edge server
        self.vehicleid=vehicleid
        self.edge_id=edge_id
        self.location_edge=0

        #taking the state for the vehicle
        self.state =5
        # state 5 is disconnect state
        self.statepre=5

        #size of trabsmission of the data
        self.veh2edgesize=0
        self.process_size=0
        self.edge2vehsize=0

        #state of the edge
        self.resource=0
        self.sizemigration=0

        #tasks of different types for
        self.tasktype=Typetask()
        self.load=0

        #defining the timer
        self.time=0


class Typetask():
    def __init__(self):
        # transmission of the task
        self.request_edge2vehsize=4*4+20*4
        self.process_loading=300*300*3*4
        self.request_veh2edgesize=300*300*3*1

        #migration of the task on the edge server
        self.sizemigration=2e9

    def informationtask(self):
        return "requst_veh2edgesize:" + str(self.request_veh2edgesize) + "\n process loading:" +str(self.process_loading) + "\n request edge 2 vehicle size" + str(self.request_edge2vehsize)


#####################################################################################################################







