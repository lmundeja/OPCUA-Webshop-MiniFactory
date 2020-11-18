import asyncio
import os
import time
import uuid
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from opcua import Client, ua
from opcua.common.type_dictionary_buider import (DataTypeDictionaryBuilder,
                                                 get_ua_class)


class OPCUA_Client():
    
    #Create a new opcua client
    def __init__(self, endpoint):
        self.client = Client(endpoint)
      
    #Connect to Server
    def __enter__(self):

        self.client.connect()
        print("Connected....")
        self.mynamespace_idx = self.client.get_namespace_index("http://example.com/OurProduct/")
        self.root = self.client.get_root_node()
        self.obj = self.root.get_child(["0:Objects", "{}:Input_WEBshop".format(self.mynamespace_idx)])
        self.client.load_type_definitions()  # scan server for custom structures and import them
        return self

    def GetAvaiality(self):
        
        res = self.obj.call_method("{}:mag_info".format(self.mynamespace_idx)) 
        return  res

    def SendOrder(self,DeliveryAddress,PlannedDeliveryTime,Silver,Red,Black,OrderID):
        
        data = get_ua_class('OurProduct')()        

        orderTime= datetime.now()   

        def CallOrderFunction(lengthofOrder, stack, partClassID):
            
            pathItemArray= []
            for i in range (len(stack)):
                pathItem= get_ua_class('PathItem')()
                pathItem.NameOfStation=stack[i]
                pathItem.PlannedStepNumber=i+1
                pathItem.IsDoneSuccessful=False
                pathItemArray.append(pathItem)

            for order in range(lengthofOrder):
                data.DeliveryAddress = DeliveryAddress
                data.OrderID = OrderID
                data.OrderTime  = orderTime
                data.PartClassID =uuid.UUID(partClassID)
                data.PartID = uuid.uuid4()
                data.PathStack= pathItemArray
                data.PlannedDeliveryTime = PlannedDeliveryTime
                self.obj.call_method("{}:get_part".format(self.mynamespace_idx), data)
                #print("Method answer is: ", res)

        #print((PlannedDeliveryTime-datetime.now()))
        difference =  PlannedDeliveryTime-datetime.now()
        duration_in_s = difference.total_seconds()
        minutes = divmod(duration_in_s, 60)[0] 

        redPathStack = ["Input","Machining_1","Machining_2","Output"]
        silverPathStack= ["Input","Machining_2","Output"]
        blackPathStack =["Input","Machining_1","Output"]
        
        print(minutes)
        
        if(minutes>=5):
            redPathStack.insert(len(redPathStack)-1,"Warehouse")
            silverPathStack.insert(len(silverPathStack)-1,"Warehouse")
            blackPathStack.insert(len(blackPathStack)-1,"Warehouse")
            
        if(Red>0):
            CallOrderFunction(Red,redPathStack,'d0a135f2-ac3a-485e-baff-b17f8ca32039')
        if(Silver>0):
            CallOrderFunction(Silver,silverPathStack,'1c2045df-a8aa-4899-bd7d-ed6dcedbc4ee')
        if(Black>0):
            CallOrderFunction(Black,blackPathStack,'e3d3e558-a086-48f3-8774-c103fe23fe6d')
    
    #Exit the server
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Disconnecting....")
        self.client.disconnect()
    

app = Flask(__name__)
endpoint_address = "opc.tcp://192.168.200.195:48844"
@app.route("/")
def index():
    #Create a new opcua client
    with OPCUA_Client(endpoint_address) as testclient:
        quantity=testclient.GetAvaiality()
        quantity =list(quantity)
        SilverQuantity=quantity[0]
        RedQuantity= quantity[2]
        BlackQuantity= quantity[4]
    return render_template("Webshop.html", SilverQuantity=SilverQuantity, RedQuantity=RedQuantity, BlackQuantity=BlackQuantity)

@app.route("/OrderPlaced", methods=["POST"])
def OrderPlaced():
    # name= request.form.get("SendOrder")
    silverQuantity= request.form.get("silverQuantity")
    redQuantity= request.form.get("redQuantity")
    blackQuantity= request.form.get("blackQuantity")
    deliveryRegion= request.form.get("Delivery_Region")
    timeofOrder= request.form.get("TimeofOrder")
    orderTime= datetime.strptime(timeofOrder,'%Y-%m-%dT%H:%M')
    orderId=uuid.uuid4()
    if silverQuantity is None:
        silverQuantity=0

    if redQuantity is None:
        redQuantity=0

    if blackQuantity is None:
        blackQuantity=0


    with OPCUA_Client(endpoint_address) as testclient:
        testclient.SendOrder(deliveryRegion,orderTime,int(silverQuantity),int(redQuantity),int(blackQuantity),orderId)
    name=orderId
    return render_template("NewWebshop.html", name=name)

@app.route("/ContinueShopping", methods=["POST"])
def ContinueShopping():
     return redirect (url_for('index'))

