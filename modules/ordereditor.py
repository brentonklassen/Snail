import db
import tkinter
import tkinter.messagebox
import shipmenteditor
import itemattribeditor
import returnaddeditor

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
        tkinter.Label(self.orderDetailsFrame,text='Name').grid(row=nextRow,column=0,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Address 1').grid(row=nextRow,column=1,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Address 2').grid(row=nextRow,column=2,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Town').grid(row=nextRow,column=3,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Region').grid(row=nextRow,column=4,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Post Code').grid(row=nextRow,column=5,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Country').grid(row=nextRow,column=6,sticky='w',padx=5)
        tkinter.Label(self.orderDetailsFrame,text='Packing Slip').grid(row=nextRow,column=7,sticky='w',padx=5)
        nextRow+=1

        # query db
        db.cur.execute("select fullName, address1, address2, town, region, postCode, country, packingSlip \
        from [order] where merchantid=? and shortOrderReference=?",[self.merchantId,self.shortOrderRef])
        rows = db.cur.fetchall()
        if len(rows) != 1:
            print(rows)
            input('The order editor did not recieve one order line when trying to edit '+str(self.merchantId)+':'+self.shortOrderRef)
            quit(1)
            
        row = rows[0] # grab first (and only) row

        # create list of widgets
        self.orderWidgets = [
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[0]),width=30), # full name
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[1]),width=40), # address 1
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[2]),width=10), # address 2
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[3]),width=20), # town
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[4]),width=6), # region
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[5]),width=10), # post code
            tkinter.Entry(self.orderDetailsFrame,textvariable=tkinter.StringVar(value=row[6]),width=7), # country
            tkinter.OptionMenu(self.orderDetailsFrame,tkinter.StringVar(value=('Yes' if row[7] else 'No')),'Yes','No'), # packing slip
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
            From Item as ia
                where i.merchantID = ia.merchantID and i.shortOrderReference = ia.shortOrderReference and i.lineNumber = ia.lineNumber
            For XML PATH ('')
        ) as itemattribs
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
                tkinter.Button(self.itemsFrame,text='Edit attributes',command=lambda lineNum=row[0]: itemattribeditor.ItemAttribEditor(self).editItemAttribs(lineNum)),
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
        query = "select packageNumber,carrier,serviceClass,[length],width,height,[weight],[bulk],note \
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
                tkinter.Button(self.packagesFrame,text='Edit return address',command=lambda packageNum=row[0]: returnaddeditor.ReturnAddEditor(self).editReturnAdd(packageNum)),
                tkinter.Button(self.packagesFrame,text=('Edit shipment' if shipment else 'Add shipment'), \
                               command=lambda packageNum=row[0], shipment = shipment: shipmenteditor.ShipmentEditor(self).editShipment(packageNum) if shipment \
                               else shipmenteditor.ShipmentEditor(self).addShipment(packageNum)),
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
        self.Snail.populateOrdersTree()


    def updateOrderDetails(self):

        name = self.orderWidgets[0].get()
        address1 = self.orderWidgets[1].get()
        address2 = self.orderWidgets[2].get()
        town = self.orderWidgets[3].get()
        region = self.orderWidgets[4].get()
        postCode = self.orderWidgets[5].get()
        country = self.orderWidgets[6].get()
        packingSlip = str(1 if self.orderWidgets[7].cget('text') == 'Yes' else 0)

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
                updateQuery = "update item set linenumber=? where merchantid=? and shortorderreference=? and linenumber=?"
                db.cur.execute(updateQuery,[lineNum-1,self.merchantId,self.shortOrderRef,lineNum])
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
                updateQuery = "update package set packagenumber=? where merchantid=? and shortorderreference=? and packagenumber=?"
                db.cur.execute(updateQuery,[packageNum-1,self.merchantId,self.shortOrderRef,packageNum])
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

        insertQuery = '''insert into package (merchantid,shortorderreference,packagenumber,
        returnCompany,returnAdd1,returnAdd2,returnCity,returnState,returnZip,datestamp) 
        values 
        (?,?,?,
        (select returnCompany from Package where packageId=(select top 1 packageId from Package where merchantID=? order by dateStamp desc)),
        (select returnAdd1 from Package where packageId=(select top 1 packageId from Package where merchantID=? order by dateStamp desc)),
        (select returnAdd2 from Package where packageId=(select top 1 packageId from Package where merchantID=? order by dateStamp desc)),
        (select returnCity from Package where packageId=(select top 1 packageId from Package where merchantID=? order by dateStamp desc)),
        (select returnState from Package where packageId=(select top 1 packageId from Package where merchantID=? order by dateStamp desc)),
        (select returnZip from Package where packageId=(select top 1 packageId from Package where merchantID=? order by dateStamp desc)),
        getdate())'''
        db.cur.execute(insertQuery,[self.merchantId,self.shortOrderRef,packageNum,
                                    self.merchantId,self.merchantId,self.merchantId,self.merchantId,self.merchantId,self.merchantId])
        db.cur.commit()

        self.edit(self.merchantId,self.shortOrderRef)
