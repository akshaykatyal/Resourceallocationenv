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
Location="Rio"
Num_Users=10
Num_Edge=10
Limit=4
Max_No_Steps=3000
Num=92
#Resource Bound
bound_r=1e9*0.063
#Bandwidth Bound
bound_b=1e9

# This class tells the policy the agent shoukd follow and which plicy has a priority for following, the policiy is selected by the vehicle

class policy():
    #this function generates policy that agent follows
    def prioritygenerate(self,vehicle,edge_server, priority):
        for vehicles in vehicle:
            # get a list of the offloading priority
            dist = np.zeros(Num_Edge)
            # now getting edge server there in the list of servers in the loop
            for edge in edge_server:
                dist[edge.edge_id] = np.sqrt(np.sum(np.square(vehicles.loc[0]-edge.loc)))
            dist_sort = np.sort(dist)
            #getting index value for the number of edge servers
            for i in range(Num_Edge):
                priority[vehicles.vehicleid][i] = np.argwhere(dist == dist_sort[i])[0]
        return priority

   #this function gives the offload that edge server contains resources to the vehicle
    def edgeserverindicate(self,offload,vehicle,priority):
        serverlimit = np.ones((Num_Edge)) * Limit
        for vehicles in vehicle:
            for i in range(Num_Edge):
                if serverlimit[int(priority[vehicles.vehicleid][i])] - 1 >= 0:
                    serverlimit[int(priority[vehicles.vehicleid][i])] -= 1
                    offload [vehicles.vehicleid] = priority[vehicles.vehicleid][i]
                    break
        return offload

  #this function will update the resouces after the connection established to edge server
    def resource_update(self, resource, edgeserver,vehicle):
        for server in edgeserver:
            # count the number of the connection user
            connectionnumber = 0
            for vehicleid in server.group:
                if vehicle[vehicleid].request.state != 5 and vehicle[vehicleid].request.state != 6:
                    connectionnumber += 1
            # Now dispatch the resource to the connected user
            for vehicleid in server.group:
                # take resource from vehicles in state 5 and 6
                if vehicle[vehicleid].request.state == 5 or  vehicle[vehicleid].request.state == 6:
                    resource[vehicleid] = 0
                #granting the resource access to vehicles
                else:
                    resource[vehicleid] = server.capability/(connectionnumber+2)  # reserve the resource to those want to migration
        return resource
#as the new vehicle gets connected the bandwidth is decreased for edge server
    def updatebandwith(self, offload, table, bandwidth, vehicle,edgeserver):
        for vehicles in vehicle :
            share_number = 1
            initialedge = int(vehicles.request.edge_id)
            targetedge = int(offload[vehicles.request.vehicleid])
            # if the resource is there so no need to migrate
            if initialedge == targetedge:
                bandwidth[vehicles.request.vehicleid] = 0
            # provide bandwidth to migrate
            else:
                # share bandwidth with user from migration edge
                for id in edgeserver[targetedge].group:
                    if offload[id] == initialedge:
                        share_number += 1
                # now the bandwidth is shared with the user from the original edge to migration edge
                for vehid in edgeserver[initialedge].group:
                    if vehid != vehicles.request.vehicleid and offload[vehid] == targetedge:
                        share_number += 1
                # now allocate the bandwidth
                bandwidth[vehicles.request.vehicleid] = table[min(initialedge,targetedge)][max(initialedge,targetedge)] / (share_number+2)

        return bandwidth
########################################################################################################################################