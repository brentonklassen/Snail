import db
import tkinter
import tkinter.messagebox


def editOrder(Snail,merchantId,shortOrderRef):
    root = tkinter.Tk()
    root.title(str(merchantId) + ' : ' + str(shortOrderRef))
    root.orderWidgets = list()
    root.itemWidgets = list()
    root.packageWidgets = list()
    root.shipmentWidgets = list()
    root.Snail = Snail
    
    displayOrderDetails(root,merchantId,shortOrderRef)
    displayItems(root,merchantId,shortOrderRef)
    displayPackages(root,merchantId,shortOrderRef)

    # display buttons
    buttonsFrame = tkinter.Frame(root)
    tkinter.Button(buttonsFrame,text='Save order',command=lambda: saveOrder(root,merchantId,shortOrderRef)).pack(side=tkinter.LEFT)
    tkinter.Button(buttonsFrame,text='Delete order',command=lambda: deleteOrder(root,merchantId,shortOrderRef)).pack(side=tkinter.LEFT)
    tkinter.Button(buttonsFrame,text='Print packing slip',command=lambda: Snail.printPackingSlips(merchantId,shortOrderRef)).pack(side=tkinter.LEFT)
    buttonsFrame.pack(pady=10)
    
    root.mainloop()
    

def displayOrderDetails(root,merchantId,shortOrderRef):

    # create order details frame
    orderDetailsFrame = tkinter.Frame(root)
    nextRow = 0
    tkinter.Label(orderDetailsFrame,text='ORDER DETAILS').grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
    nextRow+=1

    # display column headers
    tkinter.Label(orderDetailsFrame,text='Merchant').grid(row=nextRow,column=0,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Order').grid(row=nextRow,column=1,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Name').grid(row=nextRow,column=2,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Address 1').grid(row=nextRow,column=3,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Address 2').grid(row=nextRow,column=4,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Town').grid(row=nextRow,column=5,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Region').grid(row=nextRow,column=6,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Post Code').grid(row=nextRow,column=7,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Country').grid(row=nextRow,column=8,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Packing Slip').grid(row=nextRow,column=9,sticky='w',padx=5)
    tkinter.Label(orderDetailsFrame,text='Date').grid(row=nextRow,column=10,sticky='w',padx=5)
    nextRow+=1

    # query db
    db.cur.execute("select merchant, shortOrderReference, fullName, address1, address2, town, region, postCode, country, packingSlip, dateStamp \
    from [order] where merchantid=? and shortOrderReference=?",[merchantId,shortOrderRef])
    rows = db.cur.fetchall()
    if len(rows) != 1:
        input('Something is messed up...')
        quit(1)
        
    row = rows[0] # grab first (and only) row

    # create list of widgets
    root.orderWidgets = [
        tkinter.Label(orderDetailsFrame,text=row[0]), # merchant
        tkinter.Label(orderDetailsFrame,text=row[1]), # order number
        tkinter.Entry(orderDetailsFrame,textvariable=tkinter.StringVar(value=row[2]),width=30), # full name
        tkinter.Entry(orderDetailsFrame,textvariable=tkinter.StringVar(value=row[3]),width=40), # address 1
        tkinter.Entry(orderDetailsFrame,textvariable=tkinter.StringVar(value=row[4]),width=10), # address 2
        tkinter.Entry(orderDetailsFrame,textvariable=tkinter.StringVar(value=row[5]),width=20), # town
        tkinter.Entry(orderDetailsFrame,textvariable=tkinter.StringVar(value=row[6]),width=6), # region
        tkinter.Entry(orderDetailsFrame,textvariable=tkinter.StringVar(value=row[7]),width=10), # post code
        tkinter.Entry(orderDetailsFrame,textvariable=tkinter.StringVar(value=row[8]),width=7), # country
        tkinter.OptionMenu(orderDetailsFrame,tkinter.StringVar(value=('Yes' if row[9] else 'No')),'Yes','No'), # packing slip
        tkinter.Label(orderDetailsFrame,text=row[10]), # date
    ]

    # display orderWidgets
    nextCol=0
    for widget in root.orderWidgets:
        widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
        nextCol+=1

    orderDetailsFrame.pack(anchor='w',pady=10)


def displayItems(root,merchantId,shortOrderRef):

    # create items frame
    itemsFrame = tkinter.Frame(root)
    nextRow = 0
    tkinter.Label(itemsFrame,text='ITEMS').grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
    nextRow+=1

    # display column headers
    tkinter.Label(itemsFrame,text='Line').grid(row=nextRow,column=0,sticky='w',padx=5)
    tkinter.Label(itemsFrame,text='Qty').grid(row=nextRow,column=1,sticky='w',padx=5)
    tkinter.Label(itemsFrame,text='Item').grid(row=nextRow,column=2,sticky='w',padx=5)
    tkinter.Label(itemsFrame,text='Sku').grid(row=nextRow,column=3,sticky='w',padx=5)
    tkinter.Label(itemsFrame,text='Cost').grid(row=nextRow,column=4,sticky='w',padx=5)
    tkinter.Label(itemsFrame,text='Attributes').grid(row=nextRow,column=5,sticky='w',padx=5)
    tkinter.Label(itemsFrame,text='Date stamp').grid(row=nextRow,column=6,sticky='w',padx=5)
    nextRow += 1

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
    
    db.cur.execute(query,[merchantId,shortOrderRef])
    rows = db.cur.fetchall()

    for row in rows:

        # create list of widgets
        root.itemWidgets.append([
            tkinter.Label(itemsFrame,text=row[0]), # line number
            tkinter.Entry(itemsFrame,textvariable=tkinter.StringVar(value=row[1]),width=5), # quantity
            tkinter.Entry(itemsFrame,textvariable=tkinter.StringVar(value=row[2]),width=40), # item title
            tkinter.Entry(itemsFrame,textvariable=tkinter.StringVar(value=row[3]),width=20), # sku
            tkinter.Entry(itemsFrame,textvariable=tkinter.StringVar(value=row[4]),width=20), # unit cost
            tkinter.Label(itemsFrame,text=row[5]), # item attributes
            tkinter.Label(itemsFrame,text=row[6]), # date stamp
            tkinter.Button(itemsFrame,text='Remove item',command=lambda lineNum=row[0]: deleteItem(root,merchantId,shortOrderRef,lineNum))
        ])

    # display itemWidgets
    for row in root.itemWidgets:
        nextCol=0
        for widget in row:
            widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
            nextCol+=1
        nextRow += 1

    tkinter.Button(itemsFrame,text='Add item',command=lambda: addItem(root,merchantId,shortOrderRef)).grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
            

    itemsFrame.pack(anchor='w',pady=10)


def displayPackages(root, merchantId, shortOrderRef):

    # create packages frame
    packagesFrame = tkinter.Frame(root)
    nextRow = 0
    tkinter.Label(packagesFrame,text='PACKAGES (dimensions are in inches and pounds)').grid(row=nextRow,column=0,columnspan=5,sticky='w',padx=5)
    nextRow += 1

    # display column headers
    tkinter.Label(packagesFrame,text='Package').grid(row=nextRow,column=0,sticky='w',padx=5)
    tkinter.Label(packagesFrame,text='Carrier').grid(row=nextRow,column=1,sticky='w',padx=5)
    tkinter.Label(packagesFrame,text='Service').grid(row=nextRow,column=2,sticky='w',padx=5)
    tkinter.Label(packagesFrame,text='Length').grid(row=nextRow,column=3,sticky='w',padx=5)
    tkinter.Label(packagesFrame,text='Width').grid(row=nextRow,column=4,sticky='w',padx=5)
    tkinter.Label(packagesFrame,text='Height').grid(row=nextRow,column=5,sticky='w',padx=5)
    tkinter.Label(packagesFrame,text='Weight').grid(row=nextRow,column=6,sticky='w',padx=5)
    tkinter.Label(packagesFrame,text='Bulk').grid(row=nextRow,column=7,sticky='w',padx=5)
    tkinter.Label(packagesFrame,text='Note').grid(row=nextRow,column=8,sticky='w',padx=5)
    tkinter.Label(packagesFrame,text='Date stamp').grid(row=nextRow,column=9,sticky='w',padx=5)
    nextRow += 1

    # query db
    query = "select packageNumber,carrier,serviceClass,[length],width,height,[weight],[bulk],note,dateStamp \
    from Package where merchantID=? and shortOrderReference=?"
    db.cur.execute(query,[merchantId,shortOrderRef])
    rows = db.cur.fetchall()

    for row in rows:

        # check for shipment
        db.cur.execute("select * from Shipment where merchantID=? and shortOrderReference=? and packageNumber=?",[merchantId,shortOrderRef,row[0]])
        shipment = db.cur.fetchall()

        # create list of package widgets
        root.packageWidgets.append([
            tkinter.Label(packagesFrame,text=row[0]), # package number
            tkinter.Entry(packagesFrame,textvariable=tkinter.StringVar(value=row[1]),width=5), # carrier
            tkinter.Entry(packagesFrame,textvariable=tkinter.StringVar(value=row[2]),width=5), # service class
            tkinter.Entry(packagesFrame,textvariable=tkinter.StringVar(value=row[3]),width=5), # length
            tkinter.Entry(packagesFrame,textvariable=tkinter.StringVar(value=row[4]),width=5), # width
            tkinter.Entry(packagesFrame,textvariable=tkinter.StringVar(value=row[5]),width=5), # height
            tkinter.Entry(packagesFrame,textvariable=tkinter.StringVar(value=row[6]),width=5), # weight
            tkinter.OptionMenu(packagesFrame,tkinter.StringVar(value=('Yes' if row[7] else 'No')),'Yes','No'), # bulk
            tkinter.Entry(packagesFrame,textvariable=tkinter.StringVar(value=row[8]),width=15), # note
            tkinter.Label(packagesFrame,text=row[9]), # date stamp
            tkinter.Button(packagesFrame,text=('Edit shipment' if shipment else 'Add shipment'),command=lambda packageNum=row[0], shipment = shipment: editShipment(root,merchantId,shortOrderRef,packageNum) if shipment else addShipment(root,merchantId,shortOrderRef,packageNum)),
            tkinter.Button(packagesFrame,text='Remove package',command=lambda packageNum=row[0]: deletePackage(root,merchantId,shortOrderRef,packageNum))
        ])

    # display package widgets
    for row in root.packageWidgets:
        nextCol = 0
        for widget in row:
            widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
            nextCol+=1
        nextRow += 1

    tkinter.Button(packagesFrame,text='Add package',command=lambda: addPackage(root,merchantId,shortOrderRef)).grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)

    packagesFrame.pack(anchor='w',pady=10)


def saveOrder(root,merchantId,shortOrderRef):
    
    updateOrderDetails(root,merchantId,shortOrderRef)
    updateItem(root,merchantId,shortOrderRef)
    updatePackage(root,merchantId,shortOrderRef)
    root.destroy()


def updateOrderDetails(root,merchantId,shortOrderRef):

    name = root.orderWidgets[2].get()
    address1 = root.orderWidgets[3].get()
    address2 = root.orderWidgets[4].get()
    town = root.orderWidgets[5].get()
    region = root.orderWidgets[6].get()
    postCode = root.orderWidgets[7].get()
    country = root.orderWidgets[8].get()
    packingSlip = str(1 if root.orderWidgets[9].cget('text') == 'Yes' else 0)

    updateQuery = "update [order] set  fullName=?, address1=?, address2=?, town=?, region=?, postCode=?, country=?, packingSlip=? \
    where merchantid=? and shortOrderReference=?"
    db.cur.execute(updateQuery,[name,address1,address2,town,region,postCode,country,packingSlip,merchantId,shortOrderRef])
    db.cur.commit()


def updateItem(root,merchantId,shortOrderRef):

    for row in root.itemWidgets:
        lineNum = row[0].cget('text')
        quantity = row[1].get()
        itemTitle = row[2].get()
        sku = row[3].get()
        unitCost = row[4].get()

        updateQuery = "update item set itemquantity=?, itemtitle=?, itemsku=?, itemunitcost=? where merchantid=? and shortorderreference=? and linenumber=?"
        db.cur.execute(updateQuery,[quantity,itemTitle,sku,unitCost,merchantId,shortOrderRef,lineNum])
        db.cur.commit()


def updatePackage(root,merchantId,shortOrderRef):

    for row in root.packageWidgets:
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
        db.cur.execute(updateQuery,[carrier,serviceClass,length,width,height,weight,bulk,note,merchantId,shortOrderRef,packageNum])
        db.cur.commit()
    

def deleteOrder(root,merchantId,shortOrderRef):

    root.Snail.deleteOrder(merchantId,shortOrderRef)
    root.destroy()


def deleteItem(root, merchantId, shortOrderRef, lineNum):

    saveOrder(root,merchantId,shortOrderRef)

    db.cur.execute("delete from Item where merchantid=? and shortorderreference=? and linenumber=?",[merchantId,shortOrderRef,lineNum])
    db.cur.commit()

    lineExists = True
    while lineExists:
        lineNum += 1
        db.cur.execute("select * from item where merchantid=? and shortorderreference=? and linenumber=?",[merchantId,shortOrderRef,lineNum])
        if db.cur.fetchall():
            db.cur.execute("update item set linenumber=? where merchantid=? and shortorderreference=? and linenumber=?",[lineNum-1,merchantId,shortOrderRef,lineNum])
            db.cur.commit()
        else:
            lineExists = False
            
    editOrder(root.Snail,merchantId,shortOrderRef)


def deletePackage(root,merchantId,shortOrderRef,packageNum):

    saveOrder(root,merchantId,shortOrderRef)

    db.cur.execute("delete from shipment where merchantid=? and shortorderreference=? and packagenumber=?",[merchantId,shortOrderRef,packageNum])
    db.cur.execute("delete from package where merchantid=? and shortorderreference=? and packagenumber=?",[merchantId,shortOrderRef,packageNum])
    db.cur.commit()

    packageExists = True
    while packageExists:
        packageNum += 1
        db.cur.execute("select * from package where merchantid=? and shortorderreference=? and packagenumber=?",[merchantId,shortOrderRef,packageNum])
        if db.cur.fetchall():
            db.cur.execute("update package set packagenumber=? where merchantid=? and shortorderreference=? and packagenumber=?",[packageNum-1,merchantId,shortOrderRef,packageNum])
            db.cur.commit()
        else:
            packageExists = False

    editOrder(root.Snail,merchantId,shortOrderRef)


def addItem(root,merchantId,shortOrderRef):

    saveOrder(root,merchantId,shortOrderRef)

    lineNum = 0
    lineExists = True
    while lineExists:
        lineNum += 1
        db.cur.execute("select * from item where merchantid=? and shortorderreference=? and linenumber=?",[merchantId,shortOrderRef,lineNum])
        if not db.cur.fetchall():
            lineExists = False

    db.cur.execute("insert into item (merchantid,shortorderreference,linenumber,datestamp) values (?,?,?,getdate())",[merchantId,shortOrderRef,lineNum])
    db.cur.commit()
    
    editOrder(root.Snail,merchantId,shortOrderRef)

def addPackage(root,merchantId,shortOrderRef):

    saveOrder(root,merchantId,shortOrderRef)

    packageNum = 0
    packageExists = True
    while packageExists:
        packageNum += 1
        db.cur.execute("select * from package where merchantid=? and shortorderreference=? and packagenumber=?",[merchantId,shortOrderRef,packageNum])
        if not db.cur.fetchall():
            packageExists = False

    db.cur.execute("insert into package (merchantid,shortorderreference,packagenumber,datestamp) values (?,?,?,getdate())",[merchantId,shortOrderRef,packageNum])
    db.cur.commit()

    editOrder(root.Snail,merchantId,shortOrderRef)


def addShipment(root,merchantId,shortOrderRef,packageNum):

    db.cur.execute("insert into shipment (merchantid,shortorderreference,packagenumber,datestamp) values (?,?,?,getdate())",[merchantId,shortOrderRef,packageNum])
    db.cur.commit()

    editShipment(root,merchantId,shortOrderRef,packageNum)


def editShipment(root,merchantId,shortOrderRef,packageNum):

    # create shipment editor window
    root.shipmentEditor = tkinter.Toplevel(master=root)
    nextRow = 0
    tkinter.Label(root.shipmentEditor,text='SHIPMENT '+str(packageNum)+' (weight is in ounces)').grid(row=nextRow,column=0,columnspan=5,sticky='w',padx=5)
    nextRow += 1

    # display column headers
    tkinter.Label(root.shipmentEditor,text='Carrier').grid(row=nextRow,column=0,sticky='w',padx=5)
    tkinter.Label(root.shipmentEditor,text='Service').grid(row=nextRow,column=1,sticky='w',padx=5)
    tkinter.Label(root.shipmentEditor,text='Postage').grid(row=nextRow,column=2,sticky='w',padx=5)
    tkinter.Label(root.shipmentEditor,text='Tracking number').grid(row=nextRow,column=3,sticky='w',padx=5)
    tkinter.Label(root.shipmentEditor,text='Weight').grid(row=nextRow,column=4,sticky='w',padx=5)
    tkinter.Label(root.shipmentEditor,text='Date stamp').grid(row=nextRow,column=5,sticky='w',padx=5)
    nextRow += 1

    # query db
    query = "select carrier,serviceClass,postage,trackingNumber,billedWeight,dateStamp \
    from shipment where merchantID=? and shortOrderReference=? and packageNumber=?"
    db.cur.execute(query,[merchantId,shortOrderRef,packageNum])
    rows = db.cur.fetchall()
    if len(rows) != 1:
        print('Huston, we have a problem')
        quit()
    shipment = rows[0]

    root.shipmentEditor.shipmentWidgets = [
        tkinter.Entry(root.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[0]),width=5), # carrier
        tkinter.Entry(root.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[1]),width=5), # service class
        tkinter.Entry(root.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[2]),width=5), # postage
        tkinter.Entry(root.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[3]),width=20), # tracking number
        tkinter.Entry(root.shipmentEditor,textvariable=tkinter.StringVar(value=shipment[4]),width=5), # weight
        tkinter.Label(root.shipmentEditor,text=shipment[5]) # date stamp
    ]
    
    # display shipment widgets
    nextCol = 0
    for widget in root.shipmentEditor.shipmentWidgets:
        widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
        nextCol+=1
    nextRow += 1

    tkinter.Button(root.shipmentEditor,text='Save shipment',command=lambda: saveShipment(root,merchantId,shortOrderRef,packageNum)).grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
    tkinter.Button(root.shipmentEditor,text='Delete shipment',command=lambda: deleteShipment(root,merchantId,shortOrderRef,packageNum)).grid(row=nextRow,column=4,columnspan=2,sticky='e',padx=5)

    
def saveShipment(root,merchantId,shortOrderRef,packageNum):

    carrier = root.shipmentEditor.shipmentWidgets[0].get()
    serviceClass = root.shipmentEditor.shipmentWidgets[1].get()
    postage = root.shipmentEditor.shipmentWidgets[2].get()
    trackingNumber = root.shipmentEditor.shipmentWidgets[3].get()
    weight = root.shipmentEditor.shipmentWidgets[4].get()

    if not carrier or not trackingNumber:
        tkinter.messagebox.showinfo(message='You must enter both carrier and tracking number.')
        root.shipmentEditor.focus()

    else:
        
        # check to make sure this shipment does not already exist
        query = "select * from shipment where carrier=? and trackingnumber=? and (merchantid!=? or shortorderreference!=? or packagenumber!=?)"
        db.cur.execute(query,[carrier,trackingNumber,merchantId,shortOrderRef,packageNum])
        if db.cur.fetchall():
            tkinter.messagebox.showinfo(message='That shipment already exists')
            root.shipmentEditor.focus()

        else:
            updateQuery = "update shipment set carrier=?, trackingnumber=?, serviceclass=?, postage=?, billedweight=? \
            where merchantid=? and shortorderreference=? and packagenumber=?"
            db.cur.execute(updateQuery,[carrier,trackingNumber,serviceClass,postage,weight,merchantId,shortOrderRef,packageNum])
            db.cur.commit()

            root.shipmentEditor.destroy()
            saveOrder(root,merchantId,shortOrderRef)
            editOrder(root.Snail,merchantId,shortOrderRef)


def deleteShipment(root,merchantId,shortOrderRef,packageNum):

    db.cur.execute("delete from shipment where merchantId=? and shortorderreference=? and packagenumber=?",[merchantId,shortOrderRef,packageNum])
    db.cur.commit()

    root.shipmentEditor.destroy()
    saveOrder(root,merchantId,shortOrderRef)
    editOrder(root.Snail,merchantId,shortOrderRef)
