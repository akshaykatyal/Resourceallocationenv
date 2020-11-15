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

# creating a class for the edge server so that it can accept requests from vehicles for allocation of the resources

class Server():
    def __init__(self, edge_id, location):
        # the edge server unique id
        self.edge_id=edge_id
        #getting the location
        self.location=location
        #capability of the server
        self.capability=1e9*0.063
        #roups of differeent edge server
        self.group=[]
        #defing the limit of server
        self.serverlimit=Limit
        #definig the connection number that contains number of connections to server
        self.connection_number=0

    #function to maintain the vehicle requests
    def requestmaintain(self, Vehicle, Request):
        for vehicle in Vehicle:
            #the number of vehicles connected
            self.connection_number=0
            for vehicleid in self.group:
                # checking whether the state is not 6
                if Vehicle[vehicleid].request.state !=6:
                   #this updates the number of connecton to the server
                    self.connection_number+=1


            #maintaining vehicle request
            if vehicle.request.edge_id==self.edge_id and self.capability- Request[vehicle.vehicleid] > 0:
                #maintaing the vehicle connection to the server
                if vehicle.request.vehicleid not in self.group and self.connection_number+1 <= self.serverlimit:
                    #the first time do not belong to any  group
                    self.group.append(vehicle.vehicleid) # adding vehicle to group
                    vehicle.request.state=0 # making vehicle connect
                    # notify the server for vehicle for the request
                    vehicle.request.edge_id=self.edge_id
                    vehicle.request.location=self.location


                #dispatch the resource to the vehicle
                vehicle.request.resource=Request[vehicle.vehicleid]
                self.capability-= Request[vehicle.vehicleid]

   #this function handles the migration of the vehicles as the vehicles are moviing
    def updatemigration(self, offload, Bandwidth, table, vehicle, edgeserver):

        #maintain the migration of the vehicle
        for vehicleid in self.group:
            if vehicle[vehicleid].request.edge_id !=offload[vehicleid]:
                #initial edge
                initialedge=int(vehicle[vehicleid].request.edge_id)
                targetedge=int(offload[vehicleid])
                if table[initialedge][targetedge]-Bandwidth[vehicleid]>=0:
                    #on the way to migration to another edge server
                    if vehicle[vehicleid].request.state==6 and targetedge!=vehicle[vehicleid].request.offload:
                        #Now we reduce the baandwidth as the user is added
                        table[initialedge][targetedge]-=Bandwidth[vehicleid]
                        #Now start migration:
                        vehicle[vehicleid].request.sizemigration = vehicle[vehicleid].request.tasktype.sizemigration
                        vehicle[vehicleid].request.sizemigration-=Bandwidth[vehicleid]

                    #Now trying migration to step 1
                    elif vehicle[vehicleid].request.state!=6:
                        #if resource allocated then subtract bandwidth
                        table[initialedge][targetedge]-=Bandwidth[vehicleid]
                        # starting the migration of server
                        # Now start migration:
                        vehicle[vehicleid].request.sizemigration = vehicle[vehicleid].request.tasktype.sizemigration
                        vehicle[vehicleid].request.sizemigration -= Bandwidth[vehicleid]
                        #storing the result
                        vehicle[vehicleid].request.statepre=vehicle[vehicleid].request.state
                        #disconnection of the old server
                        vehicle[vehicleid].request.state=6
                    elif vehicle[vehicleid].request.state==6 and targetedge==vehicle[vehicleid].request.offload:
                        #state ==2
                        if vehicle[vehicleid].request.sizemigration >0:
                            table[initialedge][targetedge]-=Bandwidth[vehicleid]
                            vehicle[vehicleid].request.sizemigration-=Bandwidth[vehicleid]

                        else:
                            #number the connection to the user
                            connectionnumber=0
                            for targetuser in edgeserver[targetedge].group:
                                if vehicle[targetuser].request.state !=6:
                                    connectionnumber +=1

                            #changing the edge server
                            if edgeserver[targetedge].capability-vehicle[vehicleid].request.resource >=0 and connectionnumber +1 <= edgeserver[targetedge].limit:
                                #redigtering the new edge server
                                edgeserver[targetedge].capability -=vehicle[vehicleid].request.resource
                                edgeserver[targetedge].group.append(vehicleid)
                                self.group.remove(vehicleid)

                                #update request of the vehicles to the edge servers
                                vehicle[vehicleid].request.edge_id=vehicle[targetedge].edge_id
                                vehicle[vehicleid].request.location_edge=vehicle[targetedge].location
                                vehicle[vehicleid].request.state=vehicle[vehicleid].request.statepre
            #store offloading
            vehicle[vehicleid].request.offload=int(offload[vehicleid])

        return  table

    #Now releasing all the resources from the server
    def resourcerelease(self):
        self.capability=1e9*0.063

#########################################################################################

