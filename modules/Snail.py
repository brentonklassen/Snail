import main
import ordereditor
import db
import DSOL
import BF
import LTM
import os
import tkinter
import tkinter.messagebox
from tkinter import ttk

class Snail:

    def __init__(self):
        
        self.master = tkinter.Tk()
        self.Main = main.Main()
        self.master.title('Snail v' + self.Main.version)
        self.OrderEditor = ordereditor.OrderEditor(self)

        # display buttons
        self.buttonsFrame = tkinter.Frame(self.master)
        tkinter.Button(self.buttonsFrame,text='Check DanceShoesOnline',command=lambda: self.Main.checkDSOL()).pack(side=tkinter.LEFT)
        tkinter.Button(self.buttonsFrame,text='Check BetaFresh',command=lambda: self.Main.checkBF()).pack(side=tkinter.LEFT)
        tkinter.Button(self.buttonsFrame,text='Check Lighttake',command=lambda: self.Main.checkLTM()).pack(side=tkinter.LEFT)
        self.buttonsFrame.pack()

        # display order lookup
        self.displayOrderLookup()

        # display unshipped orders in tree
        self.displayOrdersTree()

        # run
        self.master.mainloop()


    def displayOrderLookup(self):

        self.lookupFrame = tkinter.Frame(self.master)
        tkinter.Label(self.lookupFrame, text='Merchant Id:').pack(side=tkinter.LEFT)
        self.merchantIdWidget = tkinter.Entry(self.lookupFrame,textvariable=tkinter.StringVar(),width=5)
        self.merchantIdWidget.pack(side=tkinter.LEFT)
        tkinter.Label(self.lookupFrame, text='Short order reference:').pack(side=tkinter.LEFT)
        self.shortOrderRefWidget = tkinter.Entry(self.lookupFrame,textvariable=tkinter.StringVar())
        self.shortOrderRefWidget.pack(side=tkinter.LEFT)
        tkinter.Button(self.lookupFrame,text='Look up order', command=self.lookupOrder).pack(side=tkinter.LEFT)
        self.lookupFrame.pack()


    def lookupOrder(self):

        merchantId = self.merchantIdWidget.get()
        shortOrderRef = self.shortOrderRefWidget.get()
        if self.Main.orderExists(merchantId,shortOrderRef):
            self.OrderEditor.edit(merchantId,shortOrderRef)
        else:
            print('You are a moron')
        


    def displayOrdersTree(self):

        self.ordersFrame = tkinter.Frame(self.master)
        self.ordersTree = ttk.Treeview(self.ordersFrame)

        self.statusFrame = tkinter.Frame(self.master)
        self.statusLabel = tkinter.StringVar()
        tkinter.Label(self.statusFrame, textvariable=self.statusLabel).pack()
        
        self.configureOrdersTree()
        self.populateOrdersTree()
        
        self.ordersTree.pack()
        self.ordersFrame.pack()
        self.statusFrame.pack() 
        
        
    def configureOrdersTree(self):

        self.ordersTree['columns'] = ('merchantid', 'shortorderref', 'fullname', 'datestamp')
        self.ordersTree.heading('merchantid', text='Merchant Id')
        self.ordersTree.heading('shortorderref', text='Order')
        self.ordersTree.heading('fullname', text='Name')
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
        query = '''select distinct o.merchant, o.merchantid, o.shortOrderReference, o.fullname, o.dateStamp
        from Snail.dbo.[Order] as o
        left join Snail.dbo.Package as p
                on o.merchantID = p.merchantID and o.shortOrderReference = p.shortOrderReference
        left join Snail.dbo.Shipment as s
                on p.merchantID = s.merchantID and p.shortOrderReference = s.shortOrderReference and p.packageNumber = s.packageNumber
        where s.ShipmentId is null
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
        order = self.ordersTree.item(treeSelection)['values']
        merchantid = order[0]
        shortorderref = order[1]
        self.OrderEditor.edit(merchantid,shortorderref)
        
        
# RUN
Snail()
