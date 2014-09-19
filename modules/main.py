# Brenton Klassen
# Created 07/30/2014
# Updated 09/08/2014

import os
import csv
import subprocess
import shutil
import time
import db
import settings
import orderEditor
import tkinter
import tkinter.messagebox

# PARSING MODULES
import DSOL 
import BF
import LTM


class Snail:
    

    def __init__(self):

        self.version = '1.1.0'
        
        self.orderColumns = ["merchant",
            "merchantID",
            "completeOrderReference",
            "shortOrderReference",
            "fullName",
            "phoneNumber",
            "emailAddress",
            "address1",
            "address2",
            "address3",
            "town",
            "region",
            "postCode",
            "country",
            "packingSlip",
            "dateStamp"]

        self.itemColumns = ["merchantID",
            "shortOrderReference",
            "lineNumber",
            "itemTitle",
            "itemSKU",
            "itemQuantity",
            "itemUnitCost",
            "itemAttribKey",
            "itemAttribVal",
            "dateStamp"]

        self.packageColumns = ["merchantID",
            "shortOrderReference",
            "packageNumber",
            "returnCompany",
            "returnAdd1",
            "returnAdd2",
            "returnCity",
            "returnState",
            "returnZip",
            "carrier",
            "serviceClass",
            "length",
            "width",
            "height",
            "weight",
            "bulk",
            'note',
            "dateStamp"]

        self.shipmentColumns = ["merchantID",
            "shortOrderReference",
            "packageNumber",
            "carrier",
            "serviceClass",
            "postage",
            "trackingNumber",
            "billedWeight",
            "dateStamp"]
                   

        self.orders = list()
        self.items = list()
        self.packages = list()
        self.shipments = list()


    def writeOutTSV(self, path, columns, lines):

        if os.path.isfile(path):
            print("Oops, writeOutTSV function tried to overwrite an existing file")
            quit()
            
        with open(path, 'w', newline='') as outputfile:
            writer = csv.writer(outputfile, delimiter='\t', quoting=csv.QUOTE_NONE)
            writer.writerow(columns)
            for row in lines:
                writer.writerow(row)


    def exportQuery(self, query, filename):

        # query out the data
        subprocess.call('bcp "' + query + '" queryout ' + os.path.join('_work_files',filename) + ' -T -c', shell=True)
        
        with open(os.path.join('_work_files',filename)) as oldFile:

            lines = oldFile.readlines()
            
            if lines:

                # parse query to get col names
                colNames = query[:query.find('from')]
                colNames = [col.split('.')[-1].strip() for col in colNames.split(',')]
                colNames = '\t'.join(colNames)

                # create new file with col names
                newLines = [colNames + '\n']
                newLines.extend(lines)

                with open(filename, 'w') as newFile:
                    newFile.writelines(newLines)

        os.remove(os.path.join('_work_files',filename))


    def displayQuery(self, query):
        subprocess.call('sqlcmd -Q "' + query + '"', shell=True)


    def displayOrder(self, merchantId, shortOrderRef):

        orderQuery = "select fullName, dateStamp \
        from Snail.dbo.[Order] \
        where merchantID = " + merchantId + " and shortOrderReference = '" + shortOrderRef + "'"

        itemQuery = "select lineNumber, itemSKU, itemAttribKey, itemAttribVal \
        from Snail.dbo.Item \
        where merchantID = " + merchantId + " and shortOrderReference = '" + shortOrderRef + "'"

        print("\nOrder " + shortOrderRef + " from merchant " + merchantId + "\n")
        self.displayQuery(orderQuery)
        print("\nItems\n")
        self.displayQuery(itemQuery)

    def editOrder(self):
        merchant = input('What merchant? ')
        order = input('What order? ')
        if self.orderExists(merchant,order):
            orderEditor.editOrder(self,merchant,order)
        else: print('That order does not exist.')


    def deleteOrder(self,merchantId,shortOrderRef):

        db.cur.execute("delete from Snail.dbo.[Order] where merchantID=? and shortOrderReference=?",[merchantId,shortOrderRef])
        db.cur.execute("delete from Snail.dbo.Item where merchantID=? and shortOrderReference=?",[merchantId,shortOrderRef])
        db.cur.execute("delete from Snail.dbo.Package where merchantID=? and shortOrderReference=?",[merchantId,shortOrderRef])
        db.cur.execute("delete from Snail.dbo.Shipment where merchantID=? and shortOrderReference=?",[merchantId,shortOrderRef])
        db.cur.commit()
        print('Deleted order ' + shortOrderRef + ' from merchant ' + str(merchantId))

            
    def bulkInFile(self, file, table):

        # truncate table
        subprocess.call('sqlcmd -Q "truncate table Snail.dbo.' + table + '" -o _work_files\\log.txt', shell=True)

        if os.path.exists(os.path.join('_work_files',file)):
            print("\nImporting " + file + " into " + table + "...")
            subprocess.call('bcp Snail.dbo.' + table + ' in _work_files\\' + file + ' -F 2 -T -c', shell=True)


    def printPackingSlips(self, merchantid='', shortorderref=''):

        selectQuery = '''select distinct o.merchant,
        o.shortOrderReference,
        o.fullName,
        case
                when o.address3 is not null and o.address2 is not null
                        then o.address1+', '+o.address2+', '+o.address3
                when o.address2 is not null
                        then o.address1+', '+o.address2
                else o.address1
        end as [address],
        o.town+', '+o.region+'  '+o.postCode as townRegionPc,
        o.phonenumber,
        i1.itemQuantity as item1quantity,
        i1.itemSKU as item1sku,
        (
            Select i1a.itemAttribKey+': '+i1a.itemAttribVal+', ' AS [text()]
            From Snail.dbo.Item as i1a
                where i1.merchantID = i1a.merchantID and i1.shortOrderReference = i1a.shortOrderReference and i1.lineNumber = i1a.lineNumber
            For XML PATH ('')
        ) as item1attribs,
        i2.itemQuantity as item2quantity,
        i2.itemSKU as item2sku,
        (
            Select i2a.itemAttribKey+': '+i2a.itemAttribVal+', ' AS [text()]
            From Snail.dbo.Item as i2a
                where i2.merchantID = i2a.merchantID and i2.shortOrderReference = i2a.shortOrderReference and i2.lineNumber = i2a.lineNumber
            For XML PATH ('')
        ) as item2attribs,
        i3.itemQuantity as item3quantity,
        i3.itemSKU as item3sku,
        (
            Select i3a.itemAttribKey+': '+i3a.itemAttribVal+', ' AS [text()]
            From Snail.dbo.Item as i3a
                where i3.merchantID = i3a.merchantID and i3.shortOrderReference = i3a.shortOrderReference and i3.lineNumber = i3a.lineNumber
            For XML PATH ('')
        ) as item3attribs,
        i4.itemQuantity as item4quantity,
        i4.itemSKU as item4sku,
        (
            Select i4a.itemAttribKey+': '+i4a.itemAttribVal+', ' AS [text()]
            From Snail.dbo.Item as i4a
                where i4.merchantID = i4a.merchantID and i4.shortOrderReference = i4a.shortOrderReference and i4.lineNumber = i4a.lineNumber
            For XML PATH ('')
        ) as item4attribs,
        i5.itemQuantity as item5quantity,
        i5.itemSKU as item5sku,
        (
            Select i5a.itemAttribKey+': '+i5a.itemAttribVal+', ' AS [text()]
            From Snail.dbo.Item as i5a
                where i5.merchantID = i5a.merchantID and i5.shortOrderReference = i5a.shortOrderReference and i5.lineNumber = i5a.lineNumber
            For XML PATH ('')
        ) as item5attribs,
        case when i6.itemId is not null
                then 'More items...' end
                as more
        from Snail.dbo.[Order] as o
        left join Snail.dbo.Item as i1 on o.merchantID = i1.merchantID and o.shortOrderReference = i1.shortOrderReference and 1 = i1.lineNumber
        left join Snail.dbo.Item as i2 on o.merchantID = i2.merchantID and o.shortOrderReference = i2.shortOrderReference and 2 = i2.lineNumber
        left join Snail.dbo.Item as i3 on o.merchantID = i3.merchantID and o.shortOrderReference = i3.shortOrderReference and 3 = i3.lineNumber
        left join Snail.dbo.Item as i4 on o.merchantID = i4.merchantID and o.shortOrderReference = i4.shortOrderReference and 4 = i4.lineNumber
        left join Snail.dbo.Item as i5 on o.merchantID = i5.merchantID and o.shortOrderReference = i5.shortOrderReference and 5 = i5.lineNumber
        left join Snail.dbo.Item as i6 on o.merchantID = i6.merchantID and o.shortOrderReference = i6.shortOrderReference and 6 = i6.lineNumber'''

        if merchantid and shortorderref:
            whereOrder = "where o.merchantID = '"+str(merchantid)+"' and o.shortOrderReference = '"+shortorderref+"'"
            query = (selectQuery+' '+whereOrder).replace('\n',' ')

        else:
            whereUnshipped = '''where o.packingSlip = 1 and convert(date,o.dateStamp)=convert(date,getdate()) and o.orderId in
            (
                    /* select orders with unshipped packages */
                    select o.orderId
                    from Snail.dbo.[Order] as o
                    join Snail.dbo.Package as p
                            on o.merchantID = p.merchantID and o.shortOrderReference = p.shortOrderReference
                    left join Snail.dbo.Shipment as s
                            on p.merchantID = s.merchantID and p.shortOrderReference = s.shortOrderReference and p.packageNumber = s.packageNumber
                    where s.ShipmentId is null
            )'''
            query = (selectQuery+' '+whereUnshipped).replace('\n',' ')

        # write out packing slip data to file
        subprocess.call('bcp "' + query.replace('\n',' ') + '" queryout _work_files\\packing_slips.tsv -T -c', shell=True)

        # open print station
        print('Printing labels...')
        bartenderLabel = os.path.join(settings.get('basepath'),'packing_slips.btw')
        dataFile = os.path.join(settings.get('basepath'),'modules\_work_files\packing_slips.tsv')        
        subprocess.call('"C:\\Program Files (x86)\\Seagull\\BarTender Suite\\bartend.exe" /F="' + bartenderLabel + '" /D="' + dataFile + '"', shell=True)


    def importDSOL(self):
        for file in DSOL.getFiles():
            self.orders.extend(DSOL.getOrders(file, self.orderColumns))
            self.items.extend(DSOL.getItems(file, self.itemColumns))
            self.packages.extend(DSOL.getPackages(file, self.packageColumns))
            DSOL.archiveFile(file)


    def importBetafresh(self):
        for file in BF.getFiles():
            self.orders.extend(BF.getOrders(file, self.orderColumns))
            self.items.extend(BF.getItems(file, self.itemColumns))
            self.packages.extend(BF.getPackages(file, self.packageColumns))
            BF.archiveFile(file)


    def importLTM(self):
        for file in LTM.getFiles():
            self.orders.extend(LTM.getOrders(file, self.orderColumns))
            self.items.extend(LTM.getItems(file, self.itemColumns))
            self.packages.extend(LTM.getPackages(file, self.packageColumns))
            

    def updateDatabase(self):
        
        # write the parsed data out to files
        self.writeOutTSV("_work_files\\orders.tsv", self.orderColumns, self.orders)
        self.writeOutTSV("_work_files\\items.tsv", self.itemColumns, self.items)
        self.writeOutTSV("_work_files\\packages.tsv", self.packageColumns, self.packages)
        self.writeOutTSV("_work_files\\shipments.tsv", self.shipmentColumns, self.shipments)
    
        # truncate staging tables and bulk the files into the db
        self.bulkInFile('orders.tsv', 'OrderFile')
        self.bulkInFile('items.tsv', 'ItemFile')
        self.bulkInFile('packages.tsv', 'PackageFile')
        self.bulkInFile('shipments.tsv', 'ShipmentFile')

        # display duplicates
        print("\nDuplicate orders\n")
        duplicateOrderQuery = "select f.merchantID, f.shortOrderReference \
            from Snail.dbo.OrderFile as f \
            join Snail.dbo.[Order] as o \
            on f.merchantID = o.merchantID and f.shortOrderReference = o.shortOrderReference"
        self.displayQuery(duplicateOrderQuery)
        print("\nDuplicate packages\n")
        duplicatePackageQuery = "select f.merchantID, f.shortOrderReference, f.packageNumber \
            from Snail.dbo.PackageFile as f \
            join Snail.dbo.Package as p \
            on f.merchantID = p.merchantID and f.shortOrderReference = p.shortOrderReference and coalesce(f.packageNumber,1) = p.packageNumber"
        self.displayQuery(duplicatePackageQuery)
        print("\nDuplicate shipments\n")
        duplicateShipmentQuery = "select f.merchantID, f.shortOrderReference, f.packageNumber \
            from Snail.dbo.ShipmentFile as f \
            join Snail.dbo.Shipment as s \
            on f.merchantID = s.merchantID and f.shortOrderReference = s.shortOrderReference and coalesce(f.packageNumber,1) = s.packageNumber"
        self.displayQuery(duplicateShipmentQuery)

        response = input("\nStop and do something about the duplicates? [y/n] ")

        if response.upper() == "Y":
            
            # remove the files
            os.remove("_work_files\\orders.tsv")
            os.remove("_work_files\\items.tsv")
            os.remove("_work_files\\packages.tsv")
            os.remove("_work_files\\shipments.tsv")
            return

        # run sql saved proc to update db
        print("\nUpdating the db...")
        subprocess.call('sqlcmd -i _work_files\\loadData.sql -o _work_files\\log.txt', shell=True)

        # remove the files
        os.remove("_work_files\\orders.tsv")
        os.remove("_work_files\\items.tsv")
        os.remove("_work_files\\packages.tsv")
        os.remove("_work_files\\shipments.tsv")

        # empty the variables
        del self.orders[:]
        del self.items[:]
        del self.packages[:]
        del self.shipments[:]


    def displayUnshippedPackages(self):
        print("\nUnshipped Packages\n")
        unshippedPackagesQuery = '''select p.merchantID, p.shortOrderReference, p.packageNumber, p.dateStamp
        from Snail.dbo.Package as p
        join Snail.dbo.[Order] as o
                on p.merchantID = o.merchantID and p.shortOrderReference = o.shortOrderReference
        left join Snail.dbo.Shipment as s
                on p.merchantID = s.merchantID and p.shortOrderReference = s.shortOrderReference and p.packageNumber = s.packageNumber
        where s.ShipmentId is null'''
        self.displayQuery(unshippedPackagesQuery.replace('\n',''))


    def orderExists(self,merchantId,shortOrderRef):
        query = "select * from [order] where merchantid="+merchantId+" and shortOrderReference='"+shortOrderRef+"'"
        db.cur.execute(query)
        if len(db.cur.fetchall()) == 1: return True
        return False


    def exportTodaysPickList(self):
        
        pickQuery = '''select (count(*)*i.itemQuantity) as qty,i.itemSKU,i.itemattribs from
        (
        select distinct i.shortOrderReference, 
        i.lineNumber, 
        i.itemQuantity,
        i.itemTitle,
        i.itemSKU,
        (
            Select ia.itemAttribKey+': '+ia.itemAttribVal+', ' AS [text()]
            From Snail.dbo.Item as ia
                where i.merchantID = ia.merchantID and i.shortOrderReference = ia.shortOrderReference and i.lineNumber = ia.lineNumber
            For XML PATH ('')
        ) as itemattribs
        from Snail.dbo.Item as i
        join Snail.dbo.[Order] as o on i.merchantID = o.merchantID and i.shortOrderReference = o.shortOrderReference
        where o.orderId in
        (
            /* select orders with unshipped packages */
            select o.orderId
            from Snail.dbo.[Order] as o
            join Snail.dbo.Package as p
                    on o.merchantID = p.merchantID and o.shortOrderReference = p.shortOrderReference
            left join Snail.dbo.Shipment as s
                    on p.merchantID = s.merchantID and p.shortOrderReference = s.shortOrderReference and p.packageNumber = s.packageNumber
            where s.ShipmentId is null and convert(date,o.dateStamp) = convert(date,getdate())
        )
        ) as i
        group by i.itemTitle,i.itemSKU,i.itemattribs,i.itemQuantity
        order by i.itemSKU'''
        
        desktopfile = os.path.join(settings.get('basepath'),'..\pick_list.tsv')
        subprocess.call('bcp "' + pickQuery.replace('\n',' ') + '" queryout ' + desktopfile + ' -T -c', shell=True)


    def importOrders(self,orders,items,packages):
        print('Importing orders...')
        importedOrders = 0
        for order in orders:

            # check if this order is already in the db
            db.cur.execute('select * from [order] where merchantid=? and shortorderreference=?',[order[1],order[3]])
            if db.cur.fetchall():
                answer = tkinter.messagebox.askquestion(message='Order '+order[3]+' already exists.\nWould you like to replace it?')
                if answer=='yes':
                    # delete the existing order and let the insert happen
                    self.deleteOrder(order[1],order[3])
                else:
                    continue # skip the insert

            itemRows = [i for i in items if i[0]==order[1] and i[1]==order[3]]
            packageRows = [p for p in packages if p[0]==order[1] and p[1]==order[3]]

            # insert order
            insertQuery = '''insert into [Order]
            (merchant,merchantID,completeOrderReference,shortOrderReference,
            fullName,phoneNumber,emailAddress,address1,
            address2,address3,town,region,postCode,country,packingSlip,dateStamp)
            values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
            db.cur.execute(insertQuery,order)

            # insert item rows
            for item in itemRows:
                insertQuery = '''insert into Item
                (merchantID,shortOrderReference,lineNumber,itemTitle,itemSKU,
                itemQuantity,itemUnitCost,itemAttribKey,itemAttribVal,dateStamp)
                values (?,?,?,?,?,?,?,?,?,?)'''
                db.cur.execute(insertQuery,item)

            # insert package rows
            for package in packageRows:
                insertQuery = '''insert into Package
                (merchantID,shortOrderReference,packageNumber,returnCompany,returnAdd1,returnAdd2,returnCity,
                returnState,returnZip,carrier,serviceClass,[length],width,height,[weight],[bulk],note,dateStamp)
                values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
                db.cur.execute(insertQuery,package)

            db.cur.commit()
            importedOrders += 1

        tkinter.messagebox.showinfo(message="Imported "+str(importedOrders)+" orders!")
            
            
    def quitSnail(self):
        if self.orders or self.items or self.packages or self.shipments:
            response = input("\nThere is data in memory that will be lost if you exit.\nAre you sure you want to exit without sending it to the DB? [y/n] ")
            if response.upper() != "Y":
                return False

        return True
