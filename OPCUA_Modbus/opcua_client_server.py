import os
import random
import sys
import time
import uuid
from datetime import datetime
from threading import Thread

from opcua import Client, Server, ua, uamethod
from opcua.common.type_dictionary_buider import (DataTypeDictionaryBuilder,
                                                 get_ua_class)

from OurProductDataType_Lib import OurProduct


@uamethod
def doSomethingwithModule(parent, new_product) : # OPC Ua method defined in your server to be consumed by client.
    print("dosomethingwithModule method in my server called with parameters: ")
    print("*********************************************")
    print(new_product)
    ###### Now we got the data from one of our clients who called this method with the parameter new_product. 
    
    ## By Calling this function DoSoemthingwithModbus with sending data received as parmater we can ...
    #.. call a function to do something in machine using Modbus communciation. 
    DoSomethingwithModbus(new_product)
  
    return "It works..."


class OPCUA_Client():
    
    #Create a new opcua client
    def __init__(self, endpoint,moduleName):
        self.client = Client(endpoint)
        self.moduleName= moduleName
    
    def __enter__(self):#Connect to Server

        self.client.connect()
        print("Client Connected....")
        self.mynamespace_idx = self.client.get_namespace_index("http://example.com/OurProduct/")
        self.root = self.client.get_root_node()
        self.obj = self.root.get_child(["0:Objects", "{0}:{1}".format(self.mynamespace_idx,self.moduleName)])
        self.client.load_type_definitions()  # scan server for custom structures and import them
        return self
       
    def SendData(self,data,methodName): #Method to send the received object from another server to next server where you are now connected as client
        res = self.obj.call_method("{0}:{1}".format(self.mynamespace_idx,methodName), data)
        print("Method answer is: ", res)
        return "ok done"    
    
    def __exit__(self, exc_type, exc_val, exc_tb):#Exit the server
        print("Disconnecting....")
        self.client.disconnect()

class OPCUA_Server(OurProduct):

    def __init__(self, endpoint, name):
        #Configuration
        print("Init", name, "...")
        self.name = name
        self.server = Server ()
        self.my_namespace_name = 'http://example.com/OurProduct/'
        self.my_namespace_idx = self.server.register_namespace(self.my_namespace_name)
        self.server.set_endpoint(endpoint)
        self.server.set_server_name(name)
       
        #Add new object - MyModule
        self.objects = self.server.get_objects_node()
        self.mymodule = self.objects.add_object(self.my_namespace_idx, "MyModule") #Mandotry please change the module name here to reflect your servers module.

        #Specify input argument(s)
        self.create_our_product_type()
        inarg_ourproduct = ua.Argument()
        inarg_ourproduct.Name = "OurProduct"
        inarg_ourproduct.DataType = self.ourproduct_data.data_type
        inarg_ourproduct.ValueRank = -1 
        inarg_ourproduct.ArrayDimensions = []
        inarg_ourproduct.Description = ua.LocalizedText("A new Product")

        #Specify output argument 
        outarg_answer = ua.Argument()
        outarg_answer.Name = "Answer"
        outarg_answer.DataType = ua.NodeId(ua.ObjectIds.String)
        outarg_answer.ValueRank = -1 
        outarg_answer.ArrayDimensions = []
        outarg_answer.Description = ua.LocalizedText("Here you can specify an answer")
        
        #Add new method
        mymethod = self.mymodule.add_method(self.my_namespace_idx, "doSomethingwithModule", doSomethingwithModule, [inarg_ourproduct], [outarg_answer])

    def __enter__(self) :
        #Start server
        print("Setup of Server", self.name, "....")
        self.server.start()
        return self
    
    def __exit__(self, exc, exc_val, exc_tb) :
        #Close server
        print("Closing Server", self.name, "....")
        self.server.stop()

def StartOPCUAServer(): #Method to start OPC UA Server
    
    server_name = "OPCUA Server"
    endpoint_address = "opc.tcp://0.0.0.0:40840" ##End point of the server you wish to create.

    with OPCUA_Server(endpoint_address, server_name) as testserver :
        try:
            while True :
                time.sleep(1)
        
        except KeyboardInterrupt :
            print("Goodbye")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise    


def SendDataUsingOPCAUAClient(data): #Method to call OPC UA Client and pass the data to send to next sever. 

    #Endpoint url of server to connect
    endpoint_address = "opc.tcp://192.168.0.182:40840"
    with OPCUA_Client(endpoint_address,"MyModule") as testclient: #With this now you can pass to any client by just passing module name, no need to chnage client class ccode.
        try: 
            
            testclient.SendData(data,"doSomethingwithModule") # Send Data method defiend in client class above at line 54. This method is used to just push data to defined function where you are connecting.
            #The method also take method name with it making it generic function to use it with different methods defined in connected server..
                
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

def DoSomethingwithModbus(data): ## Keep this function generic and can call when there ia an activity to be done by Machine using Modbus.

    try:
        print("Data Recived in Modbus Fucntion  ->>" )
        print(data)
        
        ### Write your ******!!!!!!!! Modbus !!!!!!!******** code to interact with machine here
      
        ### After that manipulate this data object(recived in paramter) and send it to next fucntion SendDataUsingOPCAUAClient as parameter. 
        for i in range(len(data.PathStack)):
            if data.PathStack[i].NameOfStation == "Input": ## This is the code for setting the step in PathStack wrt to your module to True.
                 data.PathStack[i].IsDoneSuccessful=True

        SendDataUsingOPCAUAClient(data) ## Calling the fucntion to connect client and send data
    except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
   


if __name__ == '__main__': #Main run of your program

    
     StartOPCUAServer() #Start your OPC server by calling this method
