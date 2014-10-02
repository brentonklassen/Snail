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
        tkinter.Label(self.master,text='Return company').grid(row=nextRow,column=0,sticky='w',padx=5)

        self.master.focus()
