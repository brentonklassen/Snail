import main
import ordereditor
import BulkManager
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
        self.displayOrderFilters()
        self.displayOrdersTree()
        self.displayBottomButtons()

        self.master.mainloop()


    def displayTopButtons(self):
        self.topButtonsFrame = tkinter.Frame(self.master)
        tkinter.Button(self.topButtonsFrame,text='Check DanceShoesOnline',command=self.checkDSOL).pack(side=tkinter.LEFT)
        tkinter.Button(self.topButtonsFrame,text='Check StackSocial',command=self.checkStackSocial).pack(side=tkinter.LEFT)
        tkinter.Button(self.topButtonsFrame,text='Check Lightake',command=self.checkLightake).pack(side=tkinter.LEFT)
        tkinter.Button(self.topButtonsFrame,text='Check Groupon',command=self.checkGroupon).pack(side=tkinter.LEFT)
        tkinter.Button(self.topButtonsFrame,text='Check Ncrowd',command=self.checkNcrowd).pack(side=tkinter.LEFT)
        tkinter.Button(self.topButtonsFrame,text='Check NMR',command=self.checkNMR).pack(side=tkinter.LEFT)
        self.topButtonsFrame.pack()


    def displayBottomButtons(self):
        self.bottomButtonsFrame = tkinter.Frame(self.master)
        tkinter.Button(self.bottomButtonsFrame,text='Export pick list',command=self.Main.exportPickList).pack(side=tkinter.LEFT)
        tkinter.Button(self.bottomButtonsFrame,text='Print packing slips',command = self.Main.printPackingSlips).pack(side=tkinter.LEFT)
        tkinter.Button(self.bottomButtonsFrame,text='Delete selected',command=self.deleteSelectedOrders).pack(side=tkinter.LEFT)
        tkinter.Button(self.bottomButtonsFrame,text='Manage bulk',command=self.manageBulk).pack(side=tkinter.LEFT)
        tkinter.Button(self.bottomButtonsFrame,text='Refresh',command=self.populateOrdersTree).pack(side=tkinter.LEFT)
        self.bottomButtonsFrame.pack()


    def checkDSOL(self):
        self.Main.importDSOL()
        self.Main.importDSOLAmazon()
        self.populateOrdersTree()


    def checkStackSocial(self):
        self.Main.importStackSocial()
        self.populateOrdersTree()


    def checkLightake(self):
        self.Main.importLightake()
        self.populateOrdersTree()


    def checkGroupon(self):
        self.Main.importGroupon()
        self.populateOrdersTree()


    def checkNcrowd(self):
        self.Main.importNcrowd()
        self.populateOrdersTree()


    def checkNMR(self):
        self.Main.importNMR()
        self.populateOrdersTree()


    def displayOrderFilters(self):

        self.filtersFrame = tkinter.Frame(self.master)

        tkinter.Label(self.filtersFrame, text='Merchant Id:').pack(side=tkinter.LEFT)
        self.merchantIdFilterVal = tkinter.StringVar()
        self.merchantIdFilterWidget = tkinter.Entry(self.filtersFrame,textvariable=self.merchantIdFilterVal,width=5)
        self.merchantIdFilterWidget.pack(side=tkinter.LEFT)

        tkinter.Label(self.filtersFrame, text='Order ref:').pack(side=tkinter.LEFT)
        self.orderRefFilterVal = tkinter.StringVar()
        self.orderRefFilterWidget = tkinter.Entry(self.filtersFrame,textvariable=self.orderRefFilterVal)
        self.orderRefFilterWidget.pack(side=tkinter.LEFT)

        tkinter.Label(self.filtersFrame, text='Name:').pack(side=tkinter.LEFT)
        self.nameFilterVal = tkinter.StringVar()
        self.nameFilterWidget = tkinter.Entry(self.filtersFrame,textvariable=self.nameFilterVal)
        self.nameFilterWidget.pack(side=tkinter.LEFT)

        tkinter.Label(self.filtersFrame, text='Include shipped:').pack(side=tkinter.LEFT)
        self.shippedFilterVal = tkinter.IntVar()
        self.shippedFilterWidget = tkinter.Checkbutton(self.filtersFrame, variable=self.shippedFilterVal)
        self.shippedFilterWidget.pack(side=tkinter.LEFT)


        tkinter.Button(self.filtersFrame,text='Filter', command=self.filterOrders).pack(side=tkinter.LEFT)
        tkinter.Button(self.filtersFrame,text='Clear', command=self.clearFilters).pack(side=tkinter.LEFT)

        self.filtersFrame.pack()


    def filterOrders(self):

        merchantId = self.merchantIdFilterWidget.get()
        shortOrderRef = self.orderRefFilterWidget.get()
        name = self.nameFilterWidget.get()
        searchShipped = self.shippedFilterVal.get()

        # reset where clause to nothing
        self.filters = ''

        # create a set of filters
        filterSet = set()

        if not searchShipped:
            filterSet.add(' s.ShipmentId is null ')

        if merchantId.strip():
            try:
                int(merchantId)
            except ValueError:
                print('Merchant Id must be an int')
            else:
                filterSet.add(' o.merchantId = ' + merchantId.strip() + ' ')

        if shortOrderRef.strip():
            filterSet.add(" o.shortOrderReference like '%" + shortOrderRef.strip() + "%' ")

        if name.strip():
            filterSet.add(" o.fullName like '%" + name.strip() + "%' ")

        # build new where clause
        if filterSet:
            self.filters = ' where ' + ' and '.join(filterSet)

        print(self.filters)

        self.populateOrdersTree()


    def clearFilters(self):

        self.merchantIdFilterVal.set('')
        self.orderRefFilterVal.set('')
        self.nameFilterVal.set('')
        self.shippedFilterVal.set(0)
        
        self.filters = ' where s.ShipmentId is null ' # default filter
        self.populateOrdersTree()


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

        self.filters = ' where s.ShipmentId is null ' # default filter
        self.ordersTree['show'] = 'headings'
        self.ordersTree['columns'] = ('companycode','merchantid', 'shortorderref', 'fullname', 'items', 'datestamp')
        self.ordersTree.heading('companycode', text="Company")
        self.ordersTree.column('companycode', width=75)
        self.ordersTree.heading('merchantid', text='Merchant')
        self.ordersTree.column('merchantid', width=75)
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
        ''' + self.filters + '''
        ) as o 
        group by o.company,o.merchantID,o.shortOrderReference,o.fullName,o.dateStamp
        order by o.datestamp desc'''
        db.cur.execute(query)
        orderRows = db.cur.fetchall()

        # insert these orders into tree
        for row in orderRows:
            self.ordersTree.insert('', 'end', values=(row))

        # update the status frame
        self.statusLabel.set(str(len(orderRows))+' records')


    def editSelectedOrder(self):
        treeSelection = self.ordersTree.selection()[0]
        merchantId = self.ordersTree.item(treeSelection,'values')[1]
        shortOrderRef = self.ordersTree.item(treeSelection,'values')[2]
        ordereditor.OrderEditor(self).edit(merchantId,shortOrderRef)


    def manageBulk(self):
        BulkManager.BulkManager(self)


    def deleteSelectedOrders(self):
        for order in self.ordersTree.selection():
            merchantId = self.ordersTree.item(order,'values')[1]
            shortOrderRef = self.ordersTree.item(order,'values')[2]
            self.Main.deleteOrder(merchantId,shortOrderRef)
        self.populateOrdersTree()
        
        
# RUN
Snail()
