import db
import tkinter

class ItemAttribEditor:

    def __init__(self,OrderEditor):

        self.OrderEditor = OrderEditor
        self.Snail = OrderEditor.Snail
        self.Main = self.Snail.Main
        self.merchantId = OrderEditor.merchantId
        self.shortOrderRef = OrderEditor.shortOrderRef


    def editItemAttribs(self,lineNum):

        self.lineNum = lineNum

        # create attrib editor window
        self.itemAttribEditor = tkinter.Toplevel(self.OrderEditor.master)
        nextRow = 0
        tkinter.Label(self.itemAttribEditor,text='Attributes for line '+str(lineNum)).grid(row=nextRow,column=0,columnspan=2,sticky='w',padx=5)
        nextRow += 1

        # display column headers
        tkinter.Label(self.itemAttribEditor,text='Key').grid(row=nextRow,column=0,sticky='w',padx=5)
        tkinter.Label(self.itemAttribEditor,text='Value').grid(row=nextRow,column=1,sticky='w',padx=5)

        # query db
        query = "select itemAttribKey,itemAttribVal from item where \
        merchantid=? and shortorderreference=? and linenumber=? and (itemattribkey is not null or itemattribkey!='')"
        db.cur.execute(query,[self.merchantId,self.shortOrderRef,lineNum])

        self.itemAttribWidgets = list()
        for row in db.cur.fetchall():
            self.itemAttribWidgets.append([
                tkinter.Label(self.itemAttribEditor,text=row[0]), # key
                tkinter.Entry(self.itemAttribEditor,textvariable=tkinter.StringVar(value=row[1]),width=20), # val
                tkinter.Button(self.itemAttribEditor,text='Remove attribute',command=lambda key=row[0]: self.removeItemAttrib(key))
            ])

        # display attrib widgets
        for row in self.itemAttribWidgets:
            nextCol = 0
            for widget in row:
                widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
                nextCol+=1
            nextRow += 1

        self.newItemAttribKey = tkinter.Entry(self.itemAttribEditor,textvariable=tkinter.StringVar(),width=10)
        self.newItemAttribKey.grid(row=nextRow,column=0,padx=5,sticky='w')
        self.newItemAttribVal = tkinter.Entry(self.itemAttribEditor,textvariable=tkinter.StringVar(),width=20)
        self.newItemAttribVal.grid(row=nextRow,column=1,padx=5,sticky='w')
        tkinter.Button(self.itemAttribEditor,text='Add attribute',command=lambda: self.addItemAttrib()).grid(row=nextRow,column=2,sticky='w',padx=5)
        nextRow += 1
        
        tkinter.Button(self.itemAttribEditor,text='Save attributes',command=lambda: self.saveItemAttribs()).grid(row=nextRow,column=0,sticky='w',padx=5)

        self.itemAttribEditor.focus()


    def saveItemAttribs(self):

        self.updateItemAttribs()
        self.itemAttribEditor.destroy()
        self.OrderEditor.save()
        self.OrderEditor.edit(self.merchantId,self.shortOrderRef)
    


    def updateItemAttribs(self):

        for row in self.itemAttribWidgets:
        
            key = row[0].cget('text')
            val = row[1].get()

            updateQuery = 'update item set itemAttribVal=? where merchantid=? and shortorderreference=? and linenumber=? and itemAttribKey=?'
            db.cur.execute(updateQuery,[val,self.merchantId,self.shortOrderRef,self.lineNum,key])
            db.cur.commit()

        self.deleteNullItemAttribs()


    def deleteNullItemAttribs(self):

        while True:

            # if only one row for this item, return
            db.cur.execute('select * from item where merchantid=? and shortorderreference=? and linenumber=?',[self.merchantId,self.shortOrderRef,self.lineNum])
            if len(db.cur.fetchall()) == 1: return

            # if there is more than one row with null attrib key, delete one
            selectQuery = "select * from item where merchantid=? and shortorderreference=? and linenumber=? and (itemattribkey is null or itemattribkey='')"
            db.cur.execute(selectQuery,[self.merchantId,self.shortOrderRef,self.lineNum])
            nullAttribKeys = len(db.cur.fetchall())

            if not nullAttribKeys: return

            else:
                deleteQuery = "delete from item where itemid = (select top(1) itemid from item \
                where merchantid=? and shortorderreference=? and linenumber=? and (itemattribkey is null or itemattribkey=''))"
                db.cur.execute(deleteQuery,[self.merchantId,self.shortOrderRef,self.lineNum])
                db.cur.commit()


    def addItemAttrib(self):

        newKey = self.newItemAttribKey.get()
        newVal = self.newItemAttribVal.get()

        selectQuery = 'select * from item where merchantid=? and shortorderreference=? and linenumber=? and itemattribkey=?'
        db.cur.execute(selectQuery,[self.merchantId,self.shortOrderRef,self.lineNum,newKey])
        if db.cur.fetchall():
            tkinter.messagebox.showinfo(message='That attribute key already exists.')
            self.itemAttribEditor.focus()
            
        else:

            self.updateItemAttribs()
            self.itemAttribEditor.destroy()
            
            insertQuery = 'insert into item (merchantid,shortorderreference,lineNumber,itemQuantity,itemTitle,itemSKU,itemUnitCost,itemAttribKey,itemAttribVal,datestamp) \
            select distinct merchantid,shortorderreference,lineNumber,itemQuantity,itemTitle,itemSKU,itemUnitCost,?,?,getdate() \
            from item where merchantid=? and shortorderreference=? and linenumber=?'
            db.cur.execute(insertQuery,[newKey,newVal,self.merchantId,self.shortOrderRef,self.lineNum])
            db.cur.commit()

            self.deleteNullItemAttribs()
            self.editItemAttribs(self.lineNum)
        

    def removeItemAttrib(self,key):

        self.updateItemAttribs()
        self.itemAttribEditor.destroy()
        
        updateQuery='update item set itemAttribKey=Null where merchantid=? and shortorderreference=? and linenumber=? and itemattribkey=?'
        db.cur.execute(updateQuery,[self.merchantId,self.shortOrderRef,self.lineNum,key])
        db.cur.commit()

        self.deleteNullItemAttribs()
        self.editItemAttribs(self.lineNum)
