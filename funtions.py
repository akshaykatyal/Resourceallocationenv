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
Location = "Rio"
Num_Users = 10
Num_Edge = 10
Limit = 4
Max_No_Steps = 3000
Num = 92
# Resource Bound
bound_r = 1e9 * 0.063
# Bandwidth Bound
bound_b = 1e9


#############################################
######################Functions######################
# this is the function for transfer rate of the the vehicle send the signal
def rate_transfer(vehicle_loc, edge_loc):
    # Bandwidth, Power, distance, height,
    Bandwidth = 2e6
    Power = 0.25
    distance = np.sqrt(np.sum(np.square(vehicle_loc - edge_loc))) + 0.01
    h = 4.11 * math.pow(3e8 / (4 * math.pi * 915e6 * distance), 2)
    N = 1e10
    return Bandwidth * math.log2(1 + Power * h / N)


# Function to give bandwith table for edge servers, to selct bandwith
def Table_for_bandwidth(edge_server_num):
    Table_for_bandwidth = np.zeros((edge_server_num, edge_server_num))
    for x in range(0, edge_server_num):
        for y in range(x + 1, edge_server_num):
            Table_for_bandwidth[x][y] = 1e9
    return Table_for_bandwidth


# function to flaaten the two table to one table
def table_flatten(table_two):
    table = table_two.flatten()
    return table


# states for the policy in the vehicular approach this gives available resources, bandwidth migration, off laod, location of vehicle
def states_generate(table_two, Vehicle, Edgeserver, x_min, y_min):
    # initalizing the state table
    table = table_flatten(table_two)
    State = np.zeros((len(Edgeserver) + table.size + len(Vehicle) + len(Vehicle) * 2))
    # transformation and cout initilize
    count = 0
    # Number of resources for each edge server
    for server in Edgeserver:
        State[count] = server.capability / (bound_r * 10)
        count += 1
    # Bandwidth of the each connection
    for x in range(len(table)):
        State[count] = table[x] / (bound_b * 10)
        count += 1
    # Passing the server to each vehicle
    for vehicle in Vehicle:
        State[count] = vehicle.req.edge_id / 100
        count += 1
    # location of the vehicle
    for vehicle in Vehicle:
        State[count] = (vehicle.loc[0][0] + abs(x_min)) / 1e5
        State[count + 1] = (vehicle.loc[0][1] + abs(y_min)) / 1e5
        count += 2
    return State


# Function for the actions performed at that state by the vehcle agents, this return resource, bandwith migration action, offload
# this function assigns the resource to the vehicle.
def actions_generate(Resource, bandwidth, load):
    # the resource is given as
    veh = np.zeros(Num_Users + Num_Users + Num_Edge * Num_Users)
    veh[:Num_Users] = Resource / bound_r

    # the bandwidth is given as:
    veh[Num_Users:Num_Users + Num_Users] = bandwidth / bound_b

    # the load is given as:
    base = Num_Users + Num_Users
    for id in range(Num_Users):
        veh[base + int(load[id])] = 1
        base += Num_Edge

    return veh


# function to get minimum location:
def minimum_location():
    cal = np.zeros((1, 2))
    path = r'C:\Users\Aditya Katyal\PycharmProjects\ResourceallocationEdgecomputing\data1'
    for filename in os.listdir(path):
        with open(os.path.join(path, filename),  encoding='ascii') as f:
          f1 = f.readlines()
            #for je in f.readlines():
             #   tm = je[:-1].split(',')

        # get the num
        line_num = 0
        for line in f1:
            line_num += 1
        # getting data from txt files
        data = np.zeros((line_num, 2))
        index = 0
        for line in f1:
            data[index][0] = line.split(",")[1]  # x coordinate
            data[index][1] = line.split(",")[2]  # y coordinate
            index += 1
        # data into cal defined above
        cal = np.vstack((cal, data))
    return min(cal[:, 0]), min(cal[:, 1])



# Now to get the proper location of the edge servers

def getedgelocation(edge_server_num):
    # initilize the variable to get the edge server lecoation
    location = np.zeros((edge_server_num, 2))
    # mean of the data
    num = math.floor(Num / edge_server_num)
    edge_id = 0
    for server in range(0, num * edge_server_num, num):
        path = r'C:\Users\Aditya Katyal\PycharmProjects\ResourceallocationEdgecomputing\data1'
        for filename in os.listdir(path):
            with open(os.path.join(path, filename)) as f:
                f1 = f.readlines()
            #get line num and initial data
            line_num=0
            for line in f1:
                line_num +=1
            data=np.zeros((line_num,2))
            index=0
            for line in f1:
                data[index][0]=line.split()[1] #x coordinate
                data[index][1]=line.split()[2]# y coordinate
                index+=1
            #now data is collected
            if filename % num==0:
                cal=data
            else:
                cal=np.vstack((cal,data))
        location[edge_id]=np.mean(cal,axis=0)
        edge_id+=1
    return location
#the above function gets location of the edge servers.
############################################################################
