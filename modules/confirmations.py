# Brenton Klassen
# Script to export confirmations to merchants
# Created 10/14/2014

import db
import os
import time
import csv
import settings

class Confirmations:

	def __init__(self):

		self.bfconfirmationsdir = ''
		if settings.isset('bfconfirmationsdir'):
			self.bfconfirmationsdir = settings.get('bfconfirmationsdir')

	def exportBetafreshConfirmations(self):

		selectQuery = '''select o.completeOrderReference,s.trackingNumber,s.dateStamp
		from Snail.dbo.[Order] as o 
		join Snail.dbo.Shipment as s 
			on s.merchantID = o.merchantID and s.shortOrderReference = o.shortOrderReference 
		where o.merchantid = 38 and datediff(day,s.dateStamp,getdate())=0'''

		db.cur.execute(selectQuery)

		with open(os.path.join(self.bfconfirmationsdir,time.strftime('%Y-%m-%d')+'.csv'),'w') as f:

			writer = csv.writer(f)
			for row in db.cur.fetchall():
				writer.write(row)


# RUN
C = Confirmations()
C.exportBetafreshConfirmations()
