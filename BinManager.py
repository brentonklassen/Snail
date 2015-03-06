import db
import tkinter
from tkinter import ttk

class BinManager:

	def __init__(self,Snail):

		self.master = tkinter.Toplevel(Snail.master)
		self.master.title('Bin Manager')

		self.formFrame = tkinter.Frame(self.master)
		self.configureForm()
		self.formFrame.pack()

		self.treeFrame = tkinter.Frame(self.master)
		self.binTree = ttk.Treeview(self.treeFrame)
		self.configurebinTree()
		self.populatebinTree()
		self.binTree.pack(expand=tkinter.Y,fill=tkinter.Y)
		self.treeFrame.pack(expand=tkinter.Y,fill=tkinter.Y)

		self.buttonsFrame = tkinter.Frame(self.master)
		tkinter.Button(self.buttonsFrame,text='Refresh',command=self.populatebinTree).pack(side=tkinter.LEFT)
		tkinter.Button(self.buttonsFrame,text='Delete selected',command=self.deleteSelected).pack(side=tkinter.LEFT)
		self.buttonsFrame.pack()
		self.master.focus()


	def configureForm(self):

		tkinter.Label(self.formFrame, text='Merchant:').pack(side=tkinter.LEFT)
		self.merchantIdFormVal = tkinter.StringVar()
		tkinter.Entry(self.formFrame,textvariable=self.merchantIdFormVal,width=5).pack(side=tkinter.LEFT)

		tkinter.Label(self.formFrame, text='Item SKU:').pack(side=tkinter.LEFT)
		self.itemSkuFormVal = tkinter.StringVar()
		tkinter.Entry(self.formFrame,textvariable=self.itemSkuFormVal,width=20).pack(side=tkinter.LEFT)

		tkinter.Label(self.formFrame, text='Location:').pack(side=tkinter.LEFT)
		self.locationFormVal = tkinter.StringVar()
		tkinter.Entry(self.formFrame,textvariable=self.locationFormVal,width=30).pack(side=tkinter.LEFT)

		tkinter.Button(self.formFrame,text='Add',command=self.addNew).pack(side=tkinter.LEFT)


	def configurebinTree(self):

		self.binTree['show'] = 'headings'
		self.binTree['columns'] = ('merchantID','itemsku', 'location')
		self.binTree.heading('merchantID', text="Merchant", command=lambda:self.populatebinTree("order by merchantID"))
		self.binTree.column('merchantID', width=75)
		self.binTree.heading('itemsku', text='Item Sku', command=lambda:self.populatebinTree("order by itemsku"))
		self.binTree.column('itemsku', width=150)
		self.binTree.heading('location', text='Location', command=lambda:self.populatebinTree("order by location"))
		self.binTree.column('location', width=300)

		ysb = ttk.Scrollbar(self.master, command=self.binTree.yview)
		self.binTree.configure(yscroll=ysb.set)
		ysb.pack(side=tkinter.RIGHT, fill=tkinter.Y)


	def populatebinTree(self, sort="order by location"):

		for child in self.binTree.get_children():
		    self.binTree.delete(child)
		    
		# get unshipped orders from db
		query = "select merchantID, itemsku, location	from Snail.dbo.bin "+sort
		db.cur.execute(query)
		orderRows = db.cur.fetchall()

		# insert these orders into tree
		for row in orderRows:
			self.binTree.insert('', 'end', values=(row))

	def addNew(self):

		merchantID = self.merchantIdFormVal.get()
		itemsku = self.itemSkuFormVal.get()
		location = self.locationFormVal.get()

		if not merchantID or not itemsku or not location: return

		query = "insert into Snail.dbo.bin (merchantID,itemsku,location) values (?,?,?)"
		db.cur.execute(query,[merchantID,itemsku,location])
		db.cur.commit()

		self.populatebinTree()

		self.merchantIdFormVal.set('')
		self.itemSkuFormVal.set('')
		self.locationFormVal.set('')

	def deleteSelected(self):

		for entry in self.binTree.selection():
			merchantId = self.binTree.item(entry,'values')[0]
			itemsku = self.binTree.item(entry,'values')[1]

			db.cur.execute("delete from Snail.dbo.bin where merchantID=? and itemsku=?",[merchantId,itemsku])
			db.cur.commit()

		self.populatebinTree()

