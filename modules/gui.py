from main import Snail
from ordereditor import OrderEditor
import db
import DSOL
import BF
import LTM
import os
import tkinter
import tkinter.messagebox
from tkinter import ttk

class SnailGui:

    def __init__(self):
        
        self.master = tkinter.Tk()
        self.Snail = Snail()
        self.master.title('Snail v' + self.Snail.version)
        self.orderEditor = OrderEditor(self)

        # display buttons
        self.buttonsFrame = tkinter.Frame(self.master)
        tkinter.Button(self.buttonsFrame,text='Check DanceShoesOnline',command=lambda: self.Snail.checkDSOL()).pack(side=tkinter.LEFT)
        tkinter.Button(self.buttonsFrame,text='Check BetaFresh',command=lambda: self.Snail.checkBF()).pack(side=tkinter.LEFT)
        tkinter.Button(self.buttonsFrame,text='Check Lighttake',command=lambda: self.Snail.checkLTM()).pack(side=tkinter.LEFT)
        self.buttonsFrame.pack()

        # display unshipped orders in tree
        self.ordersFrame = tkinter.Frame(self.master)
        self.ordersTree = ttk.Treeview(self.ordersFrame)
        self.configureOrdersTree()
        self.populateOrdersTree()
        self.ordersTree.pack()
        self.ordersFrame.pack()

        self.master.mainloop()
        
        
    def configureOrdersTree(self):

        self.ordersTree['columns'] = ('merchantid', 'shortorderref', 'datestamp')
        self.ordersTree.heading('merchantid', text='Merchant Id')
        self.ordersTree.heading('shortorderref', text='Order')
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
        query = '''select distinct o.merchant, o.merchantid, o.shortOrderReference, o.dateStamp
        from Snail.dbo.[Order] as o
        left join Snail.dbo.Package as p
                on o.merchantID = p.merchantID and o.shortOrderReference = p.shortOrderReference
        left join Snail.dbo.Shipment as s
                on p.merchantID = s.merchantID and p.shortOrderReference = s.shortOrderReference and p.packageNumber = s.packageNumber
        where s.ShipmentId is null
        order by o.dateStamp desc'''
        db.cur.execute(query)

        # insert these orders into tree
        for row in db.cur.fetchall():
            self.ordersTree.insert('', 'end', text=row[0], values=(row[1:]))


    def editSelectedOrder(self):
        treeSelection = self.ordersTree.selection()[0]
        order = self.ordersTree.item(treeSelection)['values']
        merchantid = order[0]
        shortorderref = order[1]
        self.orderEditor.edit(merchantid,shortorderref)
        
        
# RUN
SnailGui()
