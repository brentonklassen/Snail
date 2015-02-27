# Brenton Klassen
# Module for keeping track of incorrect orders
# 12/5/2014

import os
import csv
import db
import atexit
import settings

incorrectOrders = dict()
filePath = ''

if settings.isset('incorrectOrdersFile'):

	filePath = settings.get('incorrectOrdersFile')

	if os.path.isfile(filePath):

		with open(filePath) as f:
			
			for line in f:

				if line.strip():
					lineElements = line.split()
					merchantId = lineElements[0].strip()
					shortOrderRef = lineElements[1].strip()
					name = ' '.join(lineElements[2:])
					incorrectOrders[(merchantId,shortOrderRef)] = name

def exists(merchantId,shortOrderRef):

	return (merchantId,shortOrderRef) in incorrectOrders

def add(merchantId,shortOrderRef):

	db.cur.execute('select fullname from [order] where merchantid = ? and shortorderreference = ?',[merchantId,shortOrderRef])
	name = db.cur.fetchone()[0]

	incorrectOrders[(str(merchantId),shortOrderRef)] = name

def remove(merchantId,shortOrderRef):

	if (str(merchantId),shortOrderRef) in incorrectOrders:

		del incorrectOrders[(str(merchantId),shortOrderRef)]

def writeOut():

	if filePath:

		with open(filePath, 'w') as f:

			for key in incorrectOrders:

				f.write(key[0] + ' ' + key[1] + ' ' + incorrectOrders[key] + '\n')


atexit.register(writeOut)