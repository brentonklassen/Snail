import main
import ordereditor
import db
import os
import tkinter
import tkinter.messagebox
from tkinter import ttk

class Snail:

    def __init__(self):
        
        self.master = tkinter.Tk()
        self.Main = main.Main()
        self.master.title('Snail')
        
        self.displayTopButtons()
        self.displayOrderLookup()
        self.displayOrdersTree()
        self.displayBottomButtons()

        self.master.mainloop()


    def displayTopButtons(self):
        self.topButtonsFrame = tkinter.Frame(self.master)
        tkinter.Button(self.topButtonsFrame,text='Check DanceShoesOnline',command=self.checkDSOL).pack(side=tkinter.LEFT)
        tkinter.Button(self.topButtonsFrame,text='Check StackSocial',command=self.checkStackSocial).pack(side=tkinter.LEFT)
        tkinter.Button(self.topButtonsFrame,text='Check Lighttake',command=self.checkLightTake).pack(side=tkinter.LEFT)
        tkinter.Button(self.topButtonsFrame,text='Check Groupon',command=self.checkGroupon).pack(side=tkinter.LEFT)
        tkinter.Button(self.topButtonsFrame,text='Check Ncrowd',command=self.checkNcrowd).pack(side=tkinter.LEFT)
        self.topButtonsFrame.pack()


    def displayBottomButtons(self):
        self.bottomButtonsFrame = tkinter.Frame(self.master)
        tkinter.Button(self.bottomButtonsFrame,text='Export pick list',command=self.Main.exportPickList).pack(side=tkinter.LEFT)
        tkinter.Button(self.bottomButtonsFrame,text='Print packing slips',command = self.Main.printPackingSlips).pack(side=tkinter.LEFT)
        tkinter.Button(self.bottomButtonsFrame,text='Delete selected',command=self.deleteSelectedOrders).pack(side=tkinter.LEFT)
        tkinter.Button(self.bottomButtonsFrame,text='Refresh',command=self.populateOrdersTree).pack(side=tkinter.LEFT)
        self.bottomButtonsFrame.pack()


    def checkDSOL(self):
        self.Main.importDSOL()
        self.populateOrdersTree()


    def checkStackSocial(self):
        self.Main.importStackSocial()
        self.populateOrdersTree()


    def checkLightTake(self):
        self.Main.importLightTake()
        self.populateOrdersTree()


    def checkGroupon(self):
        self.Main.importGroupon()
        self.populateOrdersTree()


    def checkNcrowd(self):
        self.Main.importNcrowd()
        self.populateOrdersTree()


    def displayOrderLookup(self):

        self.lookupFrame = tkinter.Frame(self.master)
        tkinter.Label(self.lookupFrame, text='Merchant Id:').pack(side=tkinter.LEFT)
        self.merchantIdWidget = tkinter.Entry(self.lookupFrame,textvariable=tkinter.StringVar(),width=5)
        self.merchantIdWidget.pack(side=tkinter.LEFT)
        tkinter.Label(self.lookupFrame, text='Short order ref:').pack(side=tkinter.LEFT)
        self.shortOrderRefWidget = tkinter.Entry(self.lookupFrame,textvariable=tkinter.StringVar())
        self.shortOrderRefWidget.pack(side=tkinter.LEFT)
        tkinter.Button(self.lookupFrame,text='Look up order', command=self.lookupOrder).pack(side=tkinter.LEFT)
        self.lookupFrame.pack()


    def lookupOrder(self):

        merchantId = self.merchantIdWidget.get()
        shortOrderRef = self.shortOrderRefWidget.get()
        if self.Main.orderExists(merchantId,shortOrderRef):
            ordereditor.OrderEditor(self).edit(merchantId,shortOrderRef)
        else:
            tkinter.messagebox.showinfo(message='That order does not exist')
        


    def displayOrdersTree(self):

        self.ordersFrame = tkinter.Frame(self.master)
        self.ordersTree = ttk.Treeview(self.ordersFrame)

        self.statusFrame = tkinter.Frame(self.master)
        self.statusLabel = tkinter.StringVar()
        tkinter.Label(self.statusFrame, textvariable=self.statusLabel).pack()
        
        self.configureOrdersTree()
        self.populateOrdersTree()
        
        self.ordersTree.pack(expand=tkinter.Y,fill=tkinter.Y)
        self.ordersFrame.pack(expand=tkinter.Y,fill=tkinter.Y)
        self.statusFrame.pack()
        
        
    def configureOrdersTree(self):

        self.ordersTree['columns'] = ('merchantid', 'shortorderref', 'fullname', 'items', 'datestamp')
        self.ordersTree.heading('#0', text='Company')
        self.ordersTree.heading('merchantid', text='Merchant Id')
        self.ordersTree.column('merchantid', width=100)
        self.ordersTree.heading('shortorderref', text='Short Order Ref')
        self.ordersTree.column('shortorderref', width=150)
        self.ordersTree.heading('fullname', text='Full Name')
        self.ordersTree.column('fullname', width=300)
        self.ordersTree.heading('items', text='Items')
        self.ordersTree.column('items', width=50)
        self.ordersTree.heading('datestamp', text='Date')
        ysb = ttk.Scrollbar(self.ordersFrame, command=self.ordersTree.yview)
        self.ordersTree.configure(yscroll=ysb.set)
        ysb.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.ordersTree.bind('<Double-1>', lambda event: self.editSelectedOrder())


    def populateOrdersTree(self):

        # empty tree
        for child in self.ordersTree.get_children():
            self.ordersTree.delete(child)
            
        # get unshipped orders from db
        query = '''select o.company, o.merchantid, o.shortOrderReference, o.fullname, sum(o.itemQuantity) as items, o.dateStamp from (
        select distinct o.company, o.merchantid, o.shortOrderReference, o.fullname, i.linenumber, i.itemQuantity, o.dateStamp
        from Snail.dbo.[Order] as o
        join Item as i on o.merchantID = i.merchantID and o.shortOrderReference = i.shortOrderReference
        left join Snail.dbo.Package as p
            on o.merchantID = p.merchantID and o.shortOrderReference = p.shortOrderReference
        left join Snail.dbo.Shipment as s
            on p.merchantID = s.merchantID and p.shortOrderReference = s.shortOrderReference and p.packageNumber = s.packageNumber
        where s.ShipmentId is null
        ) as o 
        group by o.company,o.merchantID,o.shortOrderReference,o.fullName,o.dateStamp
        order by o.datestamp desc'''
        db.cur.execute(query)
        orderRows = db.cur.fetchall()

        # insert these orders into tree
        for row in orderRows:
            self.ordersTree.insert('', 'end', text=row[0], values=(row[1:]))

        # update the status frame
        self.statusLabel.set(str(len(orderRows))+' unshipped orders')


    def editSelectedOrder(self):
        treeSelection = self.ordersTree.selection()[0]
        merchantId = self.ordersTree.item(treeSelection,'values')[0]
        shortOrderRef = self.ordersTree.item(treeSelection,'values')[1]
        ordereditor.OrderEditor(self).edit(merchantId,shortOrderRef)


    def deleteSelectedOrders(self):
        for order in self.ordersTree.selection():
            merchantId = self.ordersTree.item(order,'values')[0]
            shortOrderRef = self.ordersTree.item(order,'values')[1]
            self.Main.deleteOrder(merchantId,shortOrderRef)
        self.populateOrdersTree()
        
        
# RUN
Snail()
