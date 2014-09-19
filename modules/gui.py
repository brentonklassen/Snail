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


def populateOrdersTree(tree):

    # get unshipped orders from db
    query = '''/* select orders with unshipped packages */
    select distinct top(10) o.merchant, o.merchantid, o.shortOrderReference, o.dateStamp
    from Snail.dbo.[Order] as o
    left join Snail.dbo.Package as p
            on o.merchantID = p.merchantID and o.shortOrderReference = p.shortOrderReference
    left join Snail.dbo.Shipment as s
            on p.merchantID = s.merchantID and p.shortOrderReference = s.shortOrderReference and p.packageNumber = s.packageNumber
    where s.ShipmentId is null'''
    db.cur.execute(query)

    for row in db.cur.fetchall():
        tree['columns'] = ('merchantid', 'shortorderref', 'datestamp')
        tree.heading('merchantid', text='Merchant Id')
        tree.heading('shortorderref', text='Order')
        tree.heading('datestamp', text='Date')
        tree.insert('', 'end', text=row[0], values=(row[1:]))

    tree.bind('<Double-1>', lambda event: editSelectedOrder(event,tree))


def editSelectedOrder(event,tree):
    treeSelection = tree.selection()[0]
    order = tree.item(treeSelection)['values']
    merchantid = order[0]
    shortorderref = order[1]
    orderEditor.editOrder(S,merchantid,shortorderref)
        

# create instance of Snail
S = Snail()

# create root window
root = tkinter.Tk()
root.title('Snail v' + S.version)

# display buttons
buttonsFrame = tkinter.Frame(root)
tkinter.Button(buttonsFrame,text='Check DanceShoesOnline',command=lambda: S.checkDSOL()).pack(side=tkinter.LEFT)
tkinter.Button(buttonsFrame,text='Check BetaFresh',command=lambda: S.checkBF()).pack(side=tkinter.LEFT)
tkinter.Button(buttonsFrame,text='Check Lighttake',command=lambda: S.checkLTM()).pack(side=tkinter.LEFT)
buttonsFrame.pack()

# display unshipped orders
ordersFrame = tkinter.Frame(root)
ordersTree = ttk.Treeview(ordersFrame)
populateOrdersTree(ordersTree)
ordersTree.pack()
ordersFrame.pack()

root.mainloop()
