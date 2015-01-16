import db
import tkinter
from tkinter import ttk

class BulkManager:

	def __init__(self,Snail):

		self.master = tkinter.Toplevel(Snail.master)
		self.master.title('Bulk Manager')
		self.treeFrame = tkinter.Frame(self.master)
		self.bulkTree = ttk.Treeview(self.treeFrame)
		self.configureBulkTree()
		self.populateBulkTree()
		self.bulkTree.pack(expand=tkinter.Y,fill=tkinter.Y)
		self.treeFrame.pack(expand=tkinter.Y,fill=tkinter.Y)
		self.buttonsFrame = tkinter.Frame(self.master)
		tkinter.Button(self.buttonsFrame,text='Refresh',command=self.populateBulkTree).pack(side=tkinter.LEFT)
		self.buttonsFrame.pack()
		self.master.focus()


	def configureBulkTree(self):

		self.bulkTree['show'] = 'headings'
		self.bulkTree['columns'] = ('company','address1', 'address2', 'city', 'state', 'zip','packages','print')
		self.bulkTree.heading('company', text="Company")
		self.bulkTree.column('company', width=100)
		self.bulkTree.heading('address1', text='Address 1')
		self.bulkTree.column('address1', width=300)
		self.bulkTree.heading('address2', text='Address 2')
		self.bulkTree.column('address2', width=150)
		self.bulkTree.heading('city', text='City')
		self.bulkTree.column('city', width=100)
		self.bulkTree.heading('state', text='State')
		self.bulkTree.column('state', width=50)
		self.bulkTree.heading('zip', text='Zip')
		self.bulkTree.column('zip', width=50)
		self.bulkTree.heading('packages', text='#')
		self.bulkTree.column('packages', width=50)
		self.bulkTree.heading('print', text='Print')
		self.bulkTree.column('print', width=50)

		ysb = ttk.Scrollbar(self.master, command=self.bulkTree.yview)
		self.bulkTree.configure(yscroll=ysb.set)
		ysb.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		self.bulkTree.bind('<Double-1>', lambda event: self.togglePrinting())


	def populateBulkTree(self):

		for child in self.bulkTree.get_children():
		    self.bulkTree.delete(child)
		    
		# get unshipped orders from db
		query = '''select returnCompany,returnAdd1,returnAdd2,returnCity,returnState,returnZip,count(*),[bulk]
		from Snail.dbo.package as p
		left join Snail.dbo.Shipment as s on p.merchantID = s.merchantID and p.shortOrderReference = s.shortOrderReference
		where [bulk] != 0 and s.shipmentid is null
		group by returnCompany,returnAdd1,returnAdd2,returnCity,returnState,returnZip,[bulk]'''
		db.cur.execute(query)
		orderRows = db.cur.fetchall()

		# insert these orders into tree
		for row in orderRows:

			vals = list(row)
			vals[-1] = 'Yes' if row[-1] == 1 else 'No'
			self.bulkTree.insert('', 'end', values=(vals))


	def togglePrinting(self):

		treeSelection = self.bulkTree.selection()[0]
		treeValues = self.bulkTree.item(treeSelection,'values')
		values = [val if val != 'None' else '' for val in treeValues[:6]]

		newBulkVal = '2' if treeValues[-1] == 'Yes' else '1'
		
		query = '''update Snail.dbo.package set [bulk]=''' + newBulkVal + ''' 
		where coalesce(returnCompany,'')=? and coalesce(returnAdd1,'')=? and coalesce(returnAdd2,'')=? 
		and coalesce(returnCity,'')=? and coalesce(returnState,'')=? and coalesce(returnZip,'')=?'''
		db.cur.execute(query,values)
		db.cur.commit()

		self.populateBulkTree()
