# Brenton Klassen
# Script to export confirmations to merchants
# Created 10/14/2014

import db
import os
import datetime
import csv
import settings
import pickle

class Confirmations:

	def __init__(self):

		self.bfconfirmationsdir = ''
		if settings.isset('bfconfirmationsdir'):
			self.bfconfirmationsdir = settings.get('bfconfirmationsdir')

		self.confirmationsPickle = dict()
		self.confirmationsPicklePath = os.path.join(settings.get('basepath'),'confirmations.pickle')
		if os.path.isfile(self.confirmationsPicklePath):
			with open(self.confirmationsPicklePath, 'rb') as f:
				self.confirmationsPickle = pickle.load(f)

		if 'lastbfconfirmation' not in self.confirmationsPickle:
			# assume the last confirmation was yesterday
			self.confirmationsPickle['lastbfconfirmation'] = datetime.date.today() - datetime.timedelta(days=1)
	    

	def exportBetafreshConfirmations(self):

		today = datetime.date.today()

		daysMissed = (today - self.confirmationsPickle['lastbfconfirmation']).days
		while daysMissed > 0:

			# add 1 day to date of last confirmation
			self.confirmationsPickle['lastbfconfirmation'] += datetime.timedelta(days=1)
			
			# re-calculate days missed
			daysMissed = (today - self.confirmationsPickle['lastbfconfirmation']).days

			selectQuery = '''select o.completeOrderReference,s.trackingNumber,s.dateStamp
			from Snail.dbo.[Order] as o 
			join Snail.dbo.Shipment as s 
				on s.merchantID = o.merchantID and s.shortOrderReference = o.shortOrderReference 
			where o.merchantid = 38 and datediff(day,s.dateStamp,getdate())='''+str(daysMissed)
			db.cur.execute(selectQuery)

			confirmationFileName = str(self.confirmationsPickle['lastbfconfirmation'])+'.csv'

			print("exporting confirmations from "+str(daysMissed)+" days ago to '"+confirmationFileName+"'")

			with open(os.path.join(self.bfconfirmationsdir,confirmationFileName),'w', newline='') as f:

				writer = csv.writer(f)
				for row in db.cur.fetchall():
					writer.writerow(row)

		# dump the new date into the pickle
		with open(self.confirmationsPicklePath, 'wb') as f:
			pickle.dump(self.confirmationsPickle, f)


# RUN
C = Confirmations()
C.exportBetafreshConfirmations()
