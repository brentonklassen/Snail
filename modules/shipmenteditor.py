import db
import tkinter
import tkinter.messagebox

class ShipmentEditor:

    def __init__(self,OrderEditor):

        self.OrderEditor = OrderEditor
        self.Snail = OrderEditor.Snail
        self.Main = self.Snail.Main
        self.merchantId = OrderEditor.merchantId
        self.shortOrderRef = OrderEditor.shortOrderRef


    def addShipment(self,packageNum):

        db.cur.execute("delete from shipment where carrier is null and trackingNumber is null")
        db.cur.execute("insert into shipment (merchantid,shortorderreference,packagenumber,datestamp) values (?,?,?,getdate())",[self.merchantId,self.shortOrderRef,packageNum])
        db.cur.commit()

        self.editShipment(packageNum)


    def editShipment(self,packageNum):

        self.packageNum = packageNum

        # create shipment editor window
        self.master = tkinter.Toplevel(self.OrderEditor.master)
        nextRow = 0
        tkinter.Label(self.master,text='SHIPMENT '+str(packageNum)+' (weight is in ounces)').grid(row=nextRow,column=0,columnspan=5,sticky='w',padx=5)
        nextRow += 1

        # display column headers
        tkinter.Label(self.master,text='Carrier').grid(row=nextRow,column=0,sticky='w',padx=5)
        tkinter.Label(self.master,text='Service').grid(row=nextRow,column=1,sticky='w',padx=5)
        tkinter.Label(self.master,text='Postage').grid(row=nextRow,column=2,sticky='w',padx=5)
        tkinter.Label(self.master,text='Tracking number').grid(row=nextRow,column=3,sticky='w',padx=5)
        tkinter.Label(self.master,text='Weight').grid(row=nextRow,column=4,sticky='w',padx=5)
        tkinter.Label(self.master,text='Date stamp').grid(row=nextRow,column=5,sticky='w',padx=5)
        nextRow += 1

        # query db
        query = "select carrier,serviceClass,postage,trackingNumber,billedWeight,dateStamp \
        from shipment where merchantID=? and shortOrderReference=? and packageNumber=?"
        db.cur.execute(query,[self.merchantId,self.shortOrderRef,packageNum])
        rows = db.cur.fetchall()
        if len(rows) != 1:
            print('Huston, we have a problem')
            quit()
        shipment = rows[0]

        self.shipmentWidgets = [
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=shipment[0]),width=5), # carrier
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=shipment[1]),width=5), # service class
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=shipment[2]),width=5), # postage
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=shipment[3]),width=20), # tracking number
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=shipment[4]),width=5), # weight
            tkinter.Label(self.master,text=shipment[5]) # date stamp
        ]
        
        # display shipment widgets
        nextCol = 0
        for widget in self.shipmentWidgets:
            widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
            nextCol+=1
        nextRow += 1

        tkinter.Button(self.master,text='Save shipment',command=lambda: self.saveShipment()).grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
        tkinter.Button(self.master,text='Delete shipment',command=lambda: self.deleteShipment()).grid(row=nextRow,column=4,columnspan=2,sticky='e',padx=5)

        self.master.focus()

        
    def saveShipment(self):

        carrier = self.shipmentWidgets[0].get()
        serviceClass = self.shipmentWidgets[1].get()
        postage = self.shipmentWidgets[2].get()
        trackingNumber = self.shipmentWidgets[3].get()
        weight = self.shipmentWidgets[4].get()

        # make sure a carrier and tracking number were entered
        if not carrier or not trackingNumber:
            tkinter.messagebox.showinfo(message='You must enter both carrier and tracking number.')
            self.master.focus()

        else:
            
            # check to make sure this shipment does not already exist
            query = "select * from shipment where carrier=? and trackingnumber=? and (merchantid!=? or shortorderreference!=? or packagenumber!=?)"
            db.cur.execute(query,[carrier,trackingNumber,self.merchantId,self.shortOrderRef,self.packageNum])
            if db.cur.fetchall():
                tkinter.messagebox.showinfo(message='That shipment already exists')
                self.master.focus()

            else:
                # do the update
                self.master.destroy()
                self.OrderEditor.save()
                
                updateQuery = "update shipment set carrier=?, trackingnumber=?, serviceclass=?, postage=?, billedweight=? \
                where merchantid=? and shortorderreference=? and packagenumber=?"
                db.cur.execute(updateQuery,[carrier,trackingNumber,serviceClass,postage,weight,self.merchantId,self.shortOrderRef,self.packageNum])
                db.cur.commit()

                self.Snail.populateOrdersTree()
                self.OrderEditor.edit(self.merchantId,self.shortOrderRef)


    def deleteShipment(self):

        self.master.destroy()
        self.OrderEditor.save()

        # record the deletion
        insertQuery = "insert into Snail.dbo.Deletion (merchantID,shortOrderReference,carrier,trackingNumber,dateStamp)  \
        select ?,?,carrier,trackingNumber,getdate() from Shipment where merchantID=? and shortOrderReference=?"
        db.cur.execute(insertQuery,[self.merchantId,self.shortOrderRef,self.merchantId,self.shortOrderRef])

        db.cur.execute("delete from shipment where merchantId=? and shortorderreference=? and packagenumber=?",[self.merchantId,self.shortOrderRef,self.packageNum])
        db.cur.commit()

        self.Snail.populateOrdersTree()
        self.OrderEditor.edit(self.merchantId,self.shortOrderRef)
