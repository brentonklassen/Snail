# Brenton Klassen
# 5/30/2015
# Standard parser

import os
import csv
import shutil
import collections
import validate
import settings
import productWeights
import tkinter.messagebox
import db


class Standard:

    def __init__(self):

        self.errors = set()

    def outputErrors(self):

        if self.errors:

            # show the errors in a message box
            tkinter.messagebox.showinfo(message='\n'.join(self.errors))

            # email the errors
            self.email('\n'.join(self.errors))

            # write the errors to a file
            if settings.isset('standarderrordir'):
                with open(os.path.join(settings.get('standarderrordir'),'errorlog.txt'), 'a') as f:
                    for error in self.errors:
                        f.write(error + '\n')


    def getMarketParam(self, key, required=True, job="Orders"):

        query = "select "+key+" from Snail.dbo.Market where companyCode=? and market=?"
        db.cur.execute(query,[self.companyCode, self.marketId])
        data = db.cur.fetchone()

        if not data or not data[0]:
            
            if required:
                self.errors.add(job+' from '+self.market+' were skipped because '+key+' could not be retrieved.')
            return None

        return data[0]


    def email(self, body):
        if settings.isset('mailstandardto'):
            to = settings.get('mailstandardto')
            subject = 'SkuTouch could not validate orders from '+self.market
            print('Sending email to ' + to)
            mail.sendmail(to, subject, body)


    def getNextFile(self):

        # source dir
        sourceDir = settings.get('standarddrop')

        for file in os.listdir(sourceDir):
            filename, ext = os.path.splitext(file)
            if ext == '.csv':
                self.file = os.path.join(sourceDir,file)
                return True
        return False


    def archiveFile(self):

        # archive dir
        archiveDir = settings.get('standardarchive')

        # move file to archive folder
        if not os.path.isfile(os.path.join(archiveDir, os.path.basename(self.file))):
            shutil.move(self.file, os.path.join(archiveDir, os.path.basename(self.file)))

        # or delete it if it's already there
        else:
            os.remove(self.file)


    def getOrders(self, columns):

        with open(self.file) as file:
            prevRow = list()
            parsedRows = list()
            reader = csv.reader(file)
            next(reader) # skip header row

            for row in reader:

                if len(row) < 2 or (prevRow and row[0] == prevRow[0]):
                    continue # skip if < 2 cols or same order as prev row

                # create a new ordered dictionary to hold the row info
                newRow = collections.OrderedDict.fromkeys(columns)

                # set company and market
                self.companyCode = row[2]
                self.marketId = row[0][:2]
                self.market = row[0][3:]


                newRow['marketId'] = self.market # save market id for confirmations
                newRow['companyCode'] = self.companyCode
                newRow['merchantID'] = self.getMarketParam('merchantID')
                if not newRow['merchantID']: continue
                newRow['completeOrderReference'] = validate.clean(row[1])
                newRow['shortOrderReference'] = validate.shortenPossibleAmazon(row[1])
                newRow['fullName'] = validate.clean(row[3])
                newRow["originFile"] = os.path.basename(self.file)
                newRow['phoneNumber'] = validate.phone(row[4])
                newRow['address1'] = validate.clean(row[5])
                newRow['address2'] = validate.clean(row[6])
                newRow['town'] = validate.clean(row[7])
                newRow['packingSlip'] = 1
                
                newRow['country'] = validate.country(validate.clean(row[10]))
                if not newRow['country']:
                    msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(self.file) + "' was skipped.\n"
                    msg += 'Could not validate country: ' + row[10]
                    self.errors.add(msg)
                    continue

                newRow['region'] = validate.region(validate.clean(row[8]), newRow['country'])
                if not newRow['region']:
                    msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(self.file) + "' was skipped.\n"
                    msg += 'Could not validate region: ' + row[8]
                    self.errors.add(msg)
                    continue

                newRow['postCode'] = validate.postCode(validate.clean(row[9]), newRow['country'])
                if not newRow['postCode']:
                    msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(self.file) + "' was skipped.\n"
                    msg += 'Could not validate post code: ' + row[9]
                    self.errors.add(msg)
                    continue

                if len(columns) == len(newRow):
                    parsedRows.append(list(newRow.values()))
                else:
                    print("Oops, standard order parser added a column")
                    quit()

                prevRow = row

        print("\nImported " + str(len(parsedRows)) + " orders from "+self.market+" file '" + os.path.basename(self.file) + "'")
        return parsedRows


    def getItems(self, columns):

        with open(self.file) as file:
            reader = csv.reader(file)
            parsedRows = list()
            prevRow = list()
            next(reader) # skip first row

            for row in reader:

                if len(row) < 2:
                    continue # skip if < 2 columns

                # create a new ordered dictionary to hold the row info
                newRow = collections.OrderedDict.fromkeys(columns)

                if prevRow and row[0] == prevRow[0]:
                    lineNumber += 1
                else:
                    lineNumber = 1

                newRow['merchantID'] = self.getMarketParam('merchantID')
                if not newRow['merchantID']: continue
                newRow['shortOrderReference'] = validate.shortenPossibleAmazon(row[1])
                newRow['lineNumber'] = lineNumber
                newRow['itemTitle'] = validate.clean(row[12])
                newRow['itemSKU'] = validate.clean(row[11].split('-')[-1]) # grab after the last -
                newRow['itemAttribKey'] = 'Full SKU'
                newRow['itemAttribVal'] = validate.clean(row[11]) # save entire sku
                newRow['itemQuantity'] = validate.clean(row[13])

                if len(columns) == len(newRow):
                    parsedRows.append(list(newRow.values()))
                else:
                    print("Oops, standard item parser added a column")
                    quit()

                prevRow = row

        print("Imported " + str(len(parsedRows)) + " item rows from "+self.market+" file '" + os.path.basename(self.file) + "'")
        return parsedRows


    def getPackages(self, columns):

        lines = list() # this list will hold the whole file
        parsedRows = list()

        with open(self.file) as file:
            reader = csv.reader(file)
            next(reader) # skip header

            # read the whole file into memory
            for row in reader:
                if len(row) > 1:
                    lines.append(row)

        orderStart = 0
        orderEnd = 0
        while orderEnd < len(lines):

            orderEnd += 1
            # while the current line has the same order number as the starting line
            while orderEnd < len(lines) and lines[orderEnd][0] == lines[orderStart][0]:
                orderEnd += 1

            # grab the slice of the file that contains the next order
            currentOrder = lines[orderStart:orderEnd]

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            # FIGURE OUT WHAT TO DO WITH THIS ORDER

            newRow['merchantID'] = self.getMarketParam('merchantID', job="Packages")
            if not newRow['merchantID']: 
                orderStart = orderEnd
                continue

            newRow['shortOrderReference'] = validate.shortenPossibleAmazon(currentOrder[0][1])

            newRow['returnCompany'] = self.getMarketParam('returnCompany', job="Packages")
            if not newRow['returnCompany']: 
                orderStart = orderEnd
                continue

            newRow['returnCompany2'] = self.getMarketParam('returnCompany2', required=False)

            newRow['returnAdd1'] = self.getMarketParam('returnAdd1', job="Packages")
            if not newRow['returnAdd1']:
                orderStart = orderEnd
                continue

            newRow['returnAdd2'] = self.getMarketParam('returnAdd2', required=False)

            newRow['returnCity'] = self.getMarketParam('returnCity', job="Packages")
            if not newRow['returnCity']:
                orderStart = orderEnd
                continue

            newRow['returnState'] = self.getMarketParam('returnState', job="Packages")
            if not newRow['returnState']:
                orderStart = orderEnd
                continue

            newRow['returnZip'] = self.getMarketParam('returnZip', job="Packages")
            if not newRow['returnZip']:
                orderStart = orderEnd
                continue

            itemCount = sum(int(row[13]) if row[13] else 0 for row in currentOrder)

            if itemCount == 1:
                line = currentOrder[0]
                sku = validate.clean(line[11].split('-')[-1])
                qty = line[13]

                newRow["carrier"] = 26
                newRow['serviceClass'] = 12
                newRow['weight'] = float(15/16);
                newRow['note'] = qty + '-' + sku
                newRow["bulk"] = 1

            else:
                # create a default package
                newRow["carrier"] = 26
                newRow['serviceClass'] = 12
                newRow["bulk"] = 0

            # save the package row in completedLines
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, "+self.market+" shipping allocator added a column")
                quit()

            orderStart = orderEnd # move on to the next order
            
        print("Created " + str(len(parsedRows)) + " packages from '" + os.path.basename(self.file) + "'")

        return parsedRows
