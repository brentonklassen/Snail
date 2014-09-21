import db
import tkinter
import tkinter.messagebox

class OrderEditor:

    def __init__(self,Snail):

        self.Snail = Snail
        self.Main = Snail.Main


    def edit(self,merchantId,shortOrderRef):

        self.merchantId = merchantId
        self.shortOrderRef = shortOrderRef
        self.master = tkinter.Toplevel(self.Snail.master)
        self.master.title('Order '+self.shortOrderRef+' from merchant '+str(self.merchantId))
        self.displayOrderDetails()
        self.displayItems()
        self.displayPackages()

        # display buttons
        self.buttonsFrame = tkinter.Frame(self.master)
        tkinter.Button(self.buttonsFrame,text='Save order',command=lambda: self.save()).pack(side=tkinter.LEFT)
        tkinter.Button(self.buttonsFrame,text='Delete order',command=lambda: self.deleteOrder()).pack(side=tkinter.LEFT)
        tkinter.Button(self.buttonsFrame,text='Print packing slip',command=lambda: self.Main.printPackingSlips(self.merchantId,self.shortOrderRef)).pack(side=tkinter.LEFT)
        self.buttonsFrame.pack(pady=10)
        self.master.focus()
        

    def displayOrderDetails(self):

        # create order details frame
        self.orderDetailsFrame = tkinter.Frame(self.master)
        nextRow = 0
        tkinter.Label(self.orderDetailsFrame,text='ORDER DETAILS').grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
        nextRow+=1

        # display column headers
        tkinter.Label(self.orderDetailsFrame,text='Merchant').grid(row=nextRow,column=0,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Order').grid(row=nextRow,column=1,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Name').grid(row=nextRow,column=2,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Address 1').grid(row=nextRow,column=3,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Address 2').grid(row=nextRow,column=4,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Town').grid(row=nextRow,column=5,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Region').grid(row=nextRow,column=6,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Post Code').grid(row=nextRow,column=7,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Country').grid(row=nextRow,column=8,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Packing Slip').grid(row=nextRow,column=9,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Date').grid(row=nextRow,column=10,sticky='w',padx=5)
        nextRow+=1

        # query db
        db.cur.execute("select merchant, shortOrderReference, fullName, address1, address2, town, region, postCode, country, packingSlip, dateStamp \
        from [order] where merchantid=? and shortOrderReference=?",[self.merchantId,self.shortOrderRef])
        rows = db.cur.fetchall()
        if len(rows) != 1:
            print(rows)
            input('The order editor did not recieve one order line when trying to edit '+str(self.merchantId)+':'+self.shortOrderRef)
            quit(1)
            
        row = rows[0] # grab first (and only) row

        # create list of widgets
        self.orderWidgets = [
            tkinter.Label(self.orderDetailsFrame,text=row[0]), # merchant
            tkinter.Label(self.orderDetailsFrame,text=row[1]), # order number
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[2]),width=30), # full name
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[3]),width=40), # address 1
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[4]),width=10), # address 2
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[5]),width=20), # town
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[6]),width=6), # region
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[7]),width=10), # post code
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[8]),width=7), # country
            tkinter.OptionMenu(self.orderDetailsFrame,tkinter.StringVar(value=('Yes' if row[9] else 'No')),'Yes','No'), # packing slip
            tkinter.Label(self.orderDetailsFrame,text=row[10]), # date
        ]

        # display orderWidgets
        nextCol=0
        for widget in self.orderWidgets:
            widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
            nextCol+=1

        self.orderDetailsFrame.pack(anchor='w',pady=10)


    def displayItems(self):

        # create items frame
        self.itemsFrame = tkinter.Frame(self.master)
        nextRow = 0
        tkinter.Label(self.itemsFrame,text='ITEMS').grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
        nextRow+=1

        # query db
        query = '''select distinct i.lineNumber, 
        i.itemQuantity, 
        i.itemTitle, 
        i.itemSKU, 
        i.itemUnitCost, 
        (
            Select ia.itemAttribKey+': '+ia.itemAttribVal+', ' AS [text()]
            From Snail.dbo.Item as ia
                where i.merchantID = ia.merchantID and i.shortOrderReference = ia.shortOrderReference and i.lineNumber = ia.lineNumber
            For XML PATH ('')
        ) as itemattribs,
        i.dateStamp 
        from Item as i where merchantID=? and shortOrderReference=?'''
        
        db.cur.execute(query,[self.merchantId,self.shortOrderRef])
        rows = db.cur.fetchall()

        # display column headers
        if rows:
            tkinter.Label(self.itemsFrame,text='Line').grid(row=nextRow,column=0,sticky='w',padx=5)
            tkinter.Label(self.itemsFrame,text='Qty').grid(row=nextRow,column=1,sticky='w',padx=5)
            tkinter.Label(self.itemsFrame,text='Item').grid(row=nextRow,column=2,sticky='w',padx=5)
            tkinter.Label(self.itemsFrame,text='Sku').grid(row=nextRow,column=3,sticky='w',padx=5)
            tkinter.Label(self.itemsFrame,text='Cost').grid(row=nextRow,column=4,sticky='w',padx=5)
            tkinter.Label(self.itemsFrame,text='Attributes').grid(row=nextRow,column=5,sticky='w',padx=5)
            tkinter.Label(self.itemsFrame,text='Date stamp').grid(row=nextRow,column=6,sticky='w',padx=5)
            nextRow += 1
        
        self.itemWidgets = list()
        for row in rows:

            # create list of widgets
            self.itemWidgets.append([
                tkinter.Label(self.itemsFrame,text=row[0]), # line number
                tkinter.Entry(self.itemsFrame,textvariable=tkinter.StringVar(value=row[1]),width=5), # quantity
                tkinter.Entry(self.itemsFrame,textvariable=tkinter.StringVar(value=row[2]),width=40), # item title
                tkinter.Entry(self.itemsFrame,textvariable=tkinter.StringVar(value=row[3]),width=20), # sku
                tkinter.Entry(self.itemsFrame,textvariable=tkinter.StringVar(value=row[4]),width=20), # unit cost
                tkinter.Label(self.itemsFrame,text=row[5]), # item attributes
                tkinter.Label(self.itemsFrame,text=row[6]), # date stamp
                tkinter.Button(self.itemsFrame,text='Remove item',command=lambda lineNum=row[0]: self.deleteItem(lineNum))
            ])

        # display itemWidgets
        for row in self.itemWidgets:
            nextCol=0
            for widget in row:
                widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
                nextCol+=1
            nextRow += 1

        tkinter.Button(self.itemsFrame,text='Add item',command=lambda: self.addItem()).grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
                

        self.itemsFrame.pack(anchor='w',pady=10)


    def displayPackages(self):

        # create packages frame
        self.packagesFrame = tkinter.Frame(self.master)
        nextRow = 0
        tkinter.Label(self.packagesFrame,text='PACKAGES (dimensions are in inches and pounds)').grid(row=nextRow,column=0,columnspan=5,sticky='w',padx=5)
        nextRow += 1

        # query db
        query = "select packageNumber,carrier,serviceClass,[length],width,height,[weight],[bulk],note,dateStamp \
        from Package where merchantID=? and shortOrderReference=?"
        db.cur.execute(query,[self.merchantId,self.shortOrderRef])
        rows = db.cur.fetchall()

        if rows:
            # display column headers
            tkinter.Label(self.packagesFrame,text='Package').grid(row=nextRow,column=0,sticky='w',padx=5)
            tkinter.Label(self.packagesFrame,text='Carrier').grid(row=nextRow,column=1,sticky='w',padx=5)
            tkinter.Label(self.packagesFrame,text='Service').grid(row=nextRow,column=2,sticky='w',padx=5)
            tkinter.Label(self.packagesFrame,text='Length').grid(row=nextRow,column=3,sticky='w',padx=5)
            tkinter.Label(self.packagesFrame,text='Width').grid(row=nextRow,column=4,sticky='w',padx=5)
            tkinter.Label(self.packagesFrame,text='Height').grid(row=nextRow,column=5,sticky='w',padx=5)
            tkinter.Label(self.packagesFrame,text='Weight').grid(row=nextRow,column=6,sticky='w',padx=5)
            tkinter.Label(self.packagesFrame,text='Bulk').grid(row=nextRow,column=7,sticky='w',padx=5)
            tkinter.Label(self.packagesFrame,text='Note').grid(row=nextRow,column=8,sticky='w',padx=5)
            tkinter.Label(self.packagesFrame,text='Date stamp').grid(row=nextRow,column=9,sticky='w',padx=5)
            nextRow += 1

        self.packageWidgets = list()
        for row in rows:

            # check for shipment
            db.cur.execute("select * from Shipment where merchantID=? and shortOrderReference=? and packageNumber=?",[self.merchantId,self.shortOrderRef,row[0]])
            shipment = db.cur.fetchall()

            # create list of package widgets
            self.packageWidgets.append([
                tkinter.Label(self.packagesFrame,text=row[0]), # package number
                tkinter.Entry(self.packagesFrame,textvariable=tkinter.StringVar(value=row[1]),width=5), # carrier
                tkinter.Entry(self.packagesFrame,textvariable=tkinter.StringVar(value=row[2]),width=5), # service class
                tkinter.Entry(self.packagesFrame,textvariable=tkinter.StringVar(value=row[3]),width=5), # length
                tkinter.Entry(self.packagesFrame,textvariable=tkinter.StringVar(value=row[4]),width=5), # width
                tkinter.Entry(self.packagesFrame,textvariable=tkinter.StringVar(value=row[5]),width=5), # height
                tkinter.Entry(self.packagesFrame,textvariable=tkinter.StringVar(value=row[6]),width=5), # weight
                tkinter.OptionMenu(self.packagesFrame,tkinter.StringVar(value=('Yes' if row[7] else 'No')),'Yes','No'), # bulk
                tkinter.Entry(self.packagesFrame,textvariable=tkinter.StringVar(value=row[8]),width=15), # note
                tkinter.Label(self.packagesFrame,text=row[9]), # date stamp
                tkinter.Button(self.packagesFrame,text=('Edit shipment' if shipment else 'Add shipment'), \
                               command=lambda packageNum=row[0], shipment = shipment: self.editShipment(packageNum) if shipment else self.addShipment(packageNum)),
                tkinter.Button(self.packagesFrame,text='Remove package',command=lambda packageNum=row[0]: self.deletePackage(packageNum))
            ])

        # display package widgets
        for row in self.packageWidgets:
            nextCol = 0
            for widget in row:
                widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
                nextCol+=1
            nextRow += 1

        tkinter.Button(self.packagesFrame,text='Add package',command=lambda: self.addPackage()).grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)

        self.packagesFrame.pack(anchor='w',pady=10)


    def save(self):
        
        self.updateOrderDetails()
        self.updateItems()
        self.updatePackages()
        self.master.destroy()


    def updateOrderDetails(self):

        name = self.orderWidgets[2].get()
        address1 = self.orderWidgets[3].get()
        address2 = self.orderWidgets[4].get()
        town = self.orderWidgets[5].get()
        region = self.orderWidgets[6].get()
        postCode = self.orderWidgets[7].get()
        country = self.orderWidgets[8].get()
        packingSlip = str(1 if self.orderWidgets[9].cget('text') == 'Yes' else 0)

        updateQuery = "update [order] set  fullName=?, address1=?, address2=?, town=?, region=?, postCode=?, country=?, packingSlip=? \
        where merchantid=? and shortOrderReference=?"
        db.cur.execute(updateQuery,[name,address1,address2,town,region,postCode,country,packingSlip,self.merchantId,self.shortOrderRef])
        db.cur.commit()


    def updateItems(self):

        for row in self.itemWidgets:
            lineNum = row[0].cget('text')
            quantity = row[1].get()
            itemTitle = row[2].get()
            sku = row[3].get()
            unitCost = row[4].get()

            updateQuery = "update item set itemquantity=?, itemtitle=?, itemsku=?, itemunitcost=? where merchantid=? and shortorderreference=? and linenumber=?"
            db.cur.execute(updateQuery,[quantity,itemTitle,sku,unitCost,self.merchantId,self.shortOrderRef,lineNum])
            db.cur.commit()


    def updatePackages(self):

        for row in self.packageWidgets:
            packageNum = row[0].cget('text')
            carrier = row[1].get()
            serviceClass = row[2].get()
            length = row[3].get()
            width = row[4].get()
            height = row[5].get()
            weight = row[6].get()
            bulk = 1 if row[7].cget('text') == 'Yes' else 0
            note = row[8].get()

            updateQuery = "update package set carrier=?, serviceClass=?, [length]=?, width=?, height=?, [weight]=?, [bulk]=?, note=? \
            where merchantid=? and shortorderreference=? and packagenumber=?"
            db.cur.execute(updateQuery,[carrier,serviceClass,length,width,height,weight,bulk,note,self.merchantId,self.shortOrderRef,packageNum])
            db.cur.commit()
        

    def deleteOrder(self):

        self.Main.deleteOrder(self.merchantId,self.shortOrderRef)
        self.master.destroy()
        self.Snail.populateOrdersTree()


    def deleteItem(self,lineNum):

        self.save()

        db.cur.execute("delete from Item where merchantid=? and shortorderreference=? and linenumber=?",[self.merchantId,self.shortOrderRef,lineNum])
        db.cur.commit()

        lineExists = True
        while lineExists:
            lineNum += 1
            db.cur.execute("select * from item where merchantid=? and shortorderreference=? and linenumber=?",[self.merchantId,self.shortOrderRef,lineNum])
            if db.cur.fetchall():
                db.cur.execute("update item set linenumber=? where merchantid=? and shortorderreference=? and linenumber=?",[lineNum-1,self.merchantId,self.shortOrderRef,lineNum])
                db.cur.commit()
            else:
                lineExists = False
                
        self.edit(self.merchantId,self.shortOrderRef)


    def deletePackage(self,packageNum):

        self.save()

        db.cur.execute("delete from shipment where merchantid=? and shortorderreference=? and packagenumber=?",[self.merchantId,self.shortOrderRef,packageNum])
        db.cur.execute("delete from package where merchantid=? and shortorderreference=? and packagenumber=?",[self.merchantId,self.shortOrderRef,packageNum])
        db.cur.commit()

        packageExists = True
        while packageExists:
            packageNum += 1
            db.cur.execute("select * from package where merchantid=? and shortorderreference=? and packagenumber=?",[self.merchantId,self.shortOrderRef,packageNum])
            if db.cur.fetchall():
                db.cur.execute("update package set packagenumber=? where merchantid=? and shortorderreference=? and packagenumber=?",[packageNum-1,self.merchantId,self.shortOrderRef,packageNum])
                db.cur.commit()
            else:
                packageExists = False

        self.edit(self.merchantId,self.shortOrderRef)


    def addItem(self):

        self.save()

        lineNum = 0
        lineExists = True
        while lineExists:
            lineNum += 1
            db.cur.execute("select * from item where merchantid=? and shortorderreference=? and linenumber=?",[self.merchantId,self.shortOrderRef,lineNum])
            if not db.cur.fetchall():
                lineExists = False

        db.cur.execute("insert into item (merchantid,shortorderreference,linenumber,datestamp) values (?,?,?,getdate())",[self.merchantId,self.shortOrderRef,lineNum])
        db.cur.commit()
        
        self.edit(self.merchantId,self.shortOrderRef)

    def addPackage(self):

        self.save()

        packageNum = 0
        packageExists = True
        while packageExists:
            packageNum += 1
            db.cur.execute("select * from package where merchantid=? and shortorderreference=? and packagenumber=?",[self.merchantId,self.shortOrderRef,packageNum])
            if not db.cur.fetchall():
                packageExists = False

        db.cur.execute("insert into package (merchantid,shortorderreference,packagenumber,datestamp) values (?,?,?,getdate())",[self.merchantId,self.shortOrderRef,packageNum])
        db.cur.commit()

        self.edit(self.merchantId,self.shortOrderRef)


    def addShipment(self,packageNum):

        db.cur.execute("delete from shipment where carrier is null and trackingNumber is null")
        db.cur.execute("insert into shipment (merchantid,shortorderreference,packagenumber,datestamp) values (?,?,?,getdate())",[self.merchantId,self.shortOrderRef,packageNum])
        db.cur.commit()

        self.editShipment(packageNum)


    def editShipment(self,packageNum):

        # create shipment editor window
        self.shipmentEditor = tkinter.Toplevel(self.master)
        nextRow = 0
        tkinter.Label(self.shipmentEditor,text='SHIPMENT '+str(packageNum)+' (weight is in ounces)').grid(row=nextRow,column=0,columnspan=5,sticky='w',padx=5)
        nextRow += 1

        # display column headers
        tkinter.Label(self.shipmentEditor,text='Carrier').grid(row=nextRow,column=0,sticky='w',padx=5)
        tkinter.Label(self.shipmentEditor,text='Service').grid(row=nextRow,column=1,sticky='w',padx=5)
        tkinter.Label(self.shipmentEditor,text='Postage').grid(row=nextRow,column=2,sticky='w',padx=5)
        tkinter.Label(self.shipmentEditor,text='Tracking number').grid(row=nextRow,column=3,sticky='w',padx=5)
        tkinter.Label(self.shipmentEditor,text='Weight').grid(row=nextRow,column=4,sticky='w',padx=5)
        tkinter.Label(self.shipmentEditor,text='Date stamp').grid(row=nextRow,column=5,sticky='w',padx=5)
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
            tkinter.Entry(self.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[0]),width=5), # carrier
            tkinter.Entry(self.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[1]),width=5), # service class
            tkinter.Entry(self.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[2]),width=5), # postage
            tkinter.Entry(self.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[3]),width=20), # tracking number
            tkinter.Entry(self.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[4]),width=5), # weight
            tkinter.Label(self.shipmentEditor,text=shipment[5]) # date stamp
        ]
        
        # display shipment widgets
        nextCol = 0
        for widget in self.shipmentWidgets:
            widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
            nextCol+=1
        nextRow += 1

        tkinter.Button(self.shipmentEditor,text='Save shipment',command=lambda: self.saveShipment(packageNum)).grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
        tkinter.Button(self.shipmentEditor,text='Delete shipment',command=lambda: self.deleteShipment(packageNum)).grid(row=nextRow,column=4,columnspan=2,sticky='e',padx=5)

        self.shipmentEditor.focus()

        
    def saveShipment(self,packageNum):

        carrier = self.shipmentWidgets[0].get()
        serviceClass = self.shipmentWidgets[1].get()
        postage = self.shipmentWidgets[2].get()
        trackingNumber = self.shipmentWidgets[3].get()
        weight = self.shipmentWidgets[4].get()

        # make sure a carrier and tracking number were entered
        if not carrier or not trackingNumber:
            tkinter.messagebox.showinfo(message='You must enter both carrier and tracking number.')
            self.shipmentEditor.focus()

        else:
            
            # check to make sure this shipment does not already exist
            query = "select * from shipment where carrier=? and trackingnumber=? and (merchantid!=? or shortorderreference!=? or packagenumber!=?)"
            db.cur.execute(query,[carrier,trackingNumber,self.merchantId,self.shortOrderRef,packageNum])
            if db.cur.fetchall():
                tkinter.messagebox.showinfo(message='That shipment already exists')
                self.shipmentEditor.focus()

            else:
                # do the update
                self.shipmentEditor.destroy()
                self.save()
                
                updateQuery = "update shipment set carrier=?, trackingnumber=?, serviceclass=?, postage=?, billedweight=? \
                where merchantid=? and shortorderreference=? and packagenumber=?"
                db.cur.execute(updateQuery,[carrier,trackingNumber,serviceClass,postage,weight,self.merchantId,self.shortOrderRef,packageNum])
                db.cur.commit()

                self.Snail.populateOrdersTree()
                self.edit(self.merchantId,self.shortOrderRef)


    def deleteShipment(self,packageNum):

        self.shipmentEditor.destroy()
        self.save()

        db.cur.execute("delete from shipment where merchantId=? and shortorderreference=? and packagenumber=?",[self.merchantId,self.shortOrderRef,packageNum])
        db.cur.commit()

        self.Snail.populateOrdersTree()
        self.edit(self.merchantId,self.shortOrderRef)
