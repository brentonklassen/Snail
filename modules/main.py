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
import tkinter
import tkinter.messagebox

# PARSING MODULES
import DSOL
import StackSocial
import LightTake
import Groupon
import Ncrowd


class Main:
    
    def __init__(self):
        
        self.orderColumns = ["company",
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
            "packingSlip"]

        self.itemColumns = ["merchantID",
            "shortOrderReference",
            "lineNumber",
            "itemTitle",
            "itemSKU",
            "itemQuantity",
            "itemUnitCost",
            "itemAttribKey",
            "itemAttribVal"]

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
            'note']


    def deleteOrder(self,merchantId,shortOrderRef):

        # record the deletion
        insertQuery = "insert into Snail.dbo.Deletion (merchantID,shortOrderReference,carrier,trackingNumber,dateStamp)  \
        select ?,?,carrier,trackingNumber,getdate() from Shipment where merchantID=? and shortOrderReference=?"
        db.cur.execute(insertQuery,[merchantId,shortOrderRef,merchantId,shortOrderRef])

        db.cur.execute("delete from Snail.dbo.[Order] where merchantID=? and shortOrderReference=?",[merchantId,shortOrderRef])
        db.cur.execute("delete from Snail.dbo.Item where merchantID=? and shortOrderReference=?",[merchantId,shortOrderRef])
        db.cur.execute("delete from Snail.dbo.Package where merchantID=? and shortOrderReference=?",[merchantId,shortOrderRef])
        db.cur.execute("delete from Snail.dbo.Shipment where merchantID=? and shortOrderReference=?",[merchantId,shortOrderRef])
        db.cur.commit()
        
        print('Deleted order ' + str(shortOrderRef) + ' from merchant ' + str(merchantId))


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
            whereUnshipped = '''where o.packingSlip = 1 and datediff(day,o.dateStamp,getdate())=0 and o.orderId in
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
        subprocess.call('bcp "' + query.replace('\n',' ') + '" queryout _temp\\packing_slips.tsv -T -c', shell=True)

        # open print station
        print('Printing labels...')
        bartenderLabel = os.path.join(settings.get('basepath'),'packing_slips.btw')
        dataFile = os.path.join(settings.get('basepath'),'modules\_temp\packing_slips.tsv')        
        subprocess.call('"C:\\Program Files (x86)\\Seagull\\BarTender Suite\\bartend.exe" /F="' + bartenderLabel + '" /D="' + dataFile + '"', shell=True)


    def importDSOL(self):
        
        file = DSOL.getNextFile()
        if not file:
            tkinter.messagebox.showinfo(message='There are no new DSOL files')
            return

        orders = DSOL.getOrders(file,self.orderColumns)
        items = DSOL.getItems(file,self.itemColumns)
        packages = DSOL.getPackages(file,self.packageColumns)
        DSOL.outputErrors()
        DSOL.archiveFile(file)
        self.importOrders(os.path.basename(file),orders,items,packages)


    def importStackSocial(self):
        
        file = StackSocial.getNextFile()
        if not file:
            tkinter.messagebox.showinfo(message='There are no new StackSocial files')
            return
        
        orders = StackSocial.getOrders(file,self.orderColumns)
        items = StackSocial.getItems(file,self.itemColumns)
        packages = StackSocial.getPackages(file,self.packageColumns)
        StackSocial.outputErrors()
        StackSocial.archiveFile(file)
        self.importOrders(os.path.basename(file),orders,items,packages)


    def importLightTake(self):
        
        file = LightTake.getNextFile()
        if not file:
            tkinter.messagebox.showinfo(message='There are no new LightTake files')
            return
        
        orders = LightTake.getOrders(file,self.orderColumns)
        items = LightTake.getItems(file,self.itemColumns)
        packages = LightTake.getPackages(file,self.packageColumns)
        LightTake.outputErrors()
        LightTake.archiveFile(file)
        self.importOrders(os.path.basename(file),orders,items,packages)


    def importGroupon(self):
        
        file = Groupon.getNextFile()
        if not file:
            tkinter.messagebox.showinfo(message='There are no new Groupon files')
            return
        
        orders = Groupon.getOrders(file,self.orderColumns)
        items = Groupon.getItems(file,self.itemColumns)
        packages = Groupon.getPackages(file,self.packageColumns)
        Groupon.outputErrors()
        Groupon.archiveFile(file)
        self.importOrders(os.path.basename(file),orders,items,packages)


    def importNcrowd(self):
        
        file = Ncrowd.getNextFile()
        if not file:
            tkinter.messagebox.showinfo(message='There are no new Ncrowd files')
            return
        
        orders = Ncrowd.getOrders(file,self.orderColumns)
        items = Ncrowd.getItems(file,self.itemColumns)
        packages = Ncrowd.getPackages(file,self.packageColumns)
        Ncrowd.outputErrors()
        Ncrowd.archiveFile(file)
        self.importOrders(os.path.basename(file),orders,items,packages)


    def orderExists(self,merchantId,shortOrderRef):
        db.cur.execute("select * from [order] where merchantid=? and shortOrderReference=?",[merchantId,shortOrderRef])
        if len(db.cur.fetchall()) == 1: return True
        return False


    def exportPickList(self):
        
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
            where s.ShipmentId is null and datediff(day,o.dateStamp,getdate())=0
        )
        ) as i
        group by i.itemTitle,i.itemSKU,i.itemattribs,i.itemQuantity
        order by i.itemSKU'''
        
        desktopfile = os.path.join(settings.get('basepath'),'..\pick_list.tsv')
        subprocess.call('bcp "' + pickQuery.replace('\n',' ') + '" queryout ' + desktopfile + ' -T -c', shell=True)


    def importOrders(self,filename,orders,items,packages):
        
        print('Importing orders...')
        
        importedOrders = 0
        skippedOrders = 0
        replace = False
        replaceAll = False
        skipAll = False
        asked = False
        
        for order in orders:

            # check if this order is already in the db
            db.cur.execute('select * from [order] where merchantid=? and shortorderreference=?',[order[1],order[3]])
            if db.cur.fetchall():

                if not (replaceAll or skipAll):
                    replace = tkinter.messagebox.askyesno(message='Order '+order[3]+' already exists.\nWould you like to replace it?')

                if replace or replaceAll:

                    if not replaceAll and not asked:
                        replaceAll = tkinter.messagebox.askyesno(message='Replace the rest of the duplicates as well?')
                        asked = True

                    # delete the existing order and let the insert happen
                    self.deleteOrder(order[1],order[3])

                if not replace or skipAll:

                    if not skipAll and not asked:
                        skipAll = tkinter.messagebox.askyesno(message='Skip the rest of the duplicates as well?')
                        asked = True

                    print('Skipped order ' + order[3] + ' from the file')
                    skippedOrders += 1
                    continue # skip the insert


            itemRows = [i for i in items if i[0]==order[1] and i[1]==order[3]]
            packageRows = [p for p in packages if p[0]==order[1] and p[1]==order[3]]

            # insert order
            insertQuery = '''insert into [Order]
            (company,merchantID,completeOrderReference,shortOrderReference,
            fullName,phoneNumber,emailAddress,address1,
            address2,address3,town,region,postCode,country,packingSlip,dateStamp)
            values (?, /* company */
            ?, /* merchantID */
            ?, /* completeOrderReference */
            ?, /* shortOrderReference */
            left(upper(?),40), /* fullName */
            left(?,16), /* phoneNumber */
            left(upper(?),40), /* emailAddress */
            left(upper(?),100), /* address1 */
            left(upper(?),40), /* address2 */
            left(upper(?),40), /* address3 */
            left(upper(?),40), /* town */
            ?, /* region */
            ?, /* postCode */
            ?, /* country */
            ?, /* packingSlip */
            getdate()) /* dateStamp */'''
            db.cur.execute(insertQuery,order)

            # insert item rows
            for item in itemRows:
                insertQuery = '''insert into Item
                (merchantID,shortOrderReference,lineNumber,itemTitle,itemSKU,
                itemQuantity,itemUnitCost,itemAttribKey,itemAttribVal,dateStamp)
                values (?, /* merchantID */
                ?, /* shortOrderReference */
                ?, /* lineNumber */
                left(?,300), /* itemTitle */
                left(?,20), /* itemSKU */
                ?, /* itemQuantity */
                ?, /* itemUnitCost */
                left(?,15), /* itemAttribKey */
                left(?,20), /* itemAttribVal */
                getdate()) /* dateStamp */'''
                db.cur.execute(insertQuery,item)

            # insert package rows
            for package in packageRows:
                insertQuery = '''insert into Package
                (merchantID,shortOrderReference,packageNumber,returnCompany,returnAdd1,returnAdd2,returnCity,
                returnState,returnZip,carrier,serviceClass,[length],width,height,[weight],[bulk],note,dateStamp)
                values (?, /* merchantID */
                ?, /* shortOrderReference */
                coalesce(?,1), /* packageNumber */
                left(?,50), /* returnCompany */
                left(?,100), /* returnAdd1 */
                left(?,50), /* returnAdd2 */
                left(?,50), /* returnCity */
                left(?,5), /* returnState */
                left(?,15), /* returnZip */
                ?, /* carrier */
                ?, /* serviceClass */
                ?, /* length */
                ?, /* width */
                ?, /* height */
                ?, /* weight */
                ?, /* bulk */
                left(?,500), /* note */
                getdate()) /* dateStamp */'''
                db.cur.execute(insertQuery,package)

            db.cur.commit()
            importedOrders += 1

        msg = "Imported "+str(importedOrders)+" orders from '"+filename+"'"
        if skippedOrders: msg += "\nSkipped "+str(skippedOrders)+" duplicate orders"
        tkinter.messagebox.showinfo(message=msg)

