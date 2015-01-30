import db
import tkinter

class ReturnAddEditor:

    def __init__(self,OrderEditor):

        self.OrderEditor = OrderEditor
        self.Snail = OrderEditor.Snail
        self.Main = self.Snail.Main
        self.merchantId = OrderEditor.merchantId
        self.shortOrderRef = OrderEditor.shortOrderRef


    def editReturnAdd(self,packageNum):

        self.packageNum = packageNum

        # create package editor window
        self.master = tkinter.Toplevel(self.OrderEditor.master)
        nextRow = 0
        tkinter.Label(self.master,text='RETURN ADDRESS FOR PACKAGE '+str(self.packageNum)).grid(row=nextRow,column=0,columnspan=5,sticky='w',padx=5)
        nextRow += 1

        # display column headers
        tkinter.Label(self.master,text='Company 1').grid(row=nextRow,column=0,sticky='w',padx=5)
        tkinter.Label(self.master,text='Company 2').grid(row=nextRow,column=1,sticky='w',padx=5)
        tkinter.Label(self.master,text='Address 1').grid(row=nextRow,column=2,sticky='w',padx=5)
        tkinter.Label(self.master,text='Address 2').grid(row=nextRow,column=3,sticky='w',padx=5)
        tkinter.Label(self.master,text='City').grid(row=nextRow,column=4,sticky='w',padx=5)
        tkinter.Label(self.master,text='State').grid(row=nextRow,column=5,sticky='w',padx=5)
        tkinter.Label(self.master,text='Zip').grid(row=nextRow,column=6,sticky='w',padx=5)
        nextRow += 1

        # query db
        query = "select returncompany,returncompany2,returnadd1,returnadd2,returncity,returnstate,returnzip from package where merchantid=? and shortorderreference=? and packagenumber=?"
        db.cur.execute(query,[self.merchantId,self.shortOrderRef,self.packageNum])
        rows = db.cur.fetchall()
        if len(rows) != 1:
            print('KC, we have a problem')
            quit()
        returnAddress = rows[0]

        self.returnAddWidgets = [
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=returnAddress[0]),width=25), # company 1
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=returnAddress[1]),width=25), # company 2
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=returnAddress[2]),width=25), # address 1
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=returnAddress[3]),width=20), # address 2
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=returnAddress[4]),width=20), # city
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=returnAddress[5]),width=10), # state
            tkinter.Entry(self.master,textvariable=tkinter.StringVar(value=returnAddress[6]),width=10) # zip
            ]

        # display return address widgets
        nextCol = 0
        for widget in self.returnAddWidgets:
            widget.grid(row=nextRow,column=nextCol,sticky='w',padx=5)
            nextCol+=1
        nextRow += 1

        tkinter.Button(self.master,text='Save return address',command=lambda: self.save()).grid(row=nextRow,column=0,columnspan=3,sticky='w',padx=5)
        
        self.master.focus()


    def save(self):

        company1 = self.returnAddWidgets[0].get()
        company2 = self.returnAddWidgets[1].get()
        address1 = self.returnAddWidgets[2].get()
        address2 = self.returnAddWidgets[3].get()
        city = self.returnAddWidgets[4].get()
        state = self.returnAddWidgets[5].get()
        zipcode = self.returnAddWidgets[6].get()

        self.master.destroy()

        updateQuery = "update package set returncompany=?, returncompany2=?, returnadd1=?, returnadd2=?, returncity=?, returnstate=?, returnzip=? \
            where merchantid=? and shortorderreference=? and packagenumber=?"
        db.cur.execute(updateQuery, [company1,company2,address1,address2,city,state,zipcode,self.merchantId,self.shortOrderRef,self.packageNum])
        db.cur.commit()
