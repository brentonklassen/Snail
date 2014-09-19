from main import Snail
import db
import DSOL
import BF
import LTM
import orderEditor
import os
import tkinter
import tkinter.messagebox
from tkinter import ttk


def configureOrdersTree(ordersTree):

    ordersTree['columns'] = ('merchantid', 'shortorderref', 'datestamp')
    ordersTree.heading('merchantid', text='Merchant Id')
    ordersTree.heading('shortorderref', text='Order')
    ordersTree.heading('datestamp', text='Date')
    ysb = ttk.Scrollbar(ordersFrame, command=ordersTree.yview)
    ordersTree.configure(yscroll=ysb.set)
    ysb.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    ordersTree.bind('<Double-1>', lambda event: editSelectedOrder(event,ordersTree))


def populateOrdersTree(ordersTree):

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

    for row in db.cur.fetchall():
        ordersTree.insert('', 'end', text=row[0], values=(row[1:]))


def editSelectedOrder(event,tree):
    treeSelection = tree.selection()[0]
    order = tree.item(treeSelection)['values']
    merchantid = order[0]
    shortorderref = order[1]
    orderEditor.editOrder(root,merchantid,shortorderref)


# create root window
root = tkinter.Tk()
root.Snail = Snail() # bind Snail instance to root
root.title('Snail v' + root.Snail.version)

# display buttons
buttonsFrame = tkinter.Frame(root)
tkinter.Button(buttonsFrame,text='Check DanceShoesOnline',command=lambda: root.Snail.checkDSOL()).pack(side=tkinter.LEFT)
tkinter.Button(buttonsFrame,text='Check BetaFresh',command=lambda: root.Snail.checkBF()).pack(side=tkinter.LEFT)
tkinter.Button(buttonsFrame,text='Check Lighttake',command=lambda: root.Snail.checkLTM()).pack(side=tkinter.LEFT)
buttonsFrame.pack()

# display unshipped orders in tree
ordersFrame = tkinter.Frame(root)
ordersTree = ttk.Treeview(ordersFrame)
configureOrdersTree(ordersTree)
populateOrdersTree(ordersTree)
ordersTree.pack()
ordersFrame.pack()

# run program
root.mainloop()
