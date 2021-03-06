# Brenton Klassen
# 07/30/2014
# Updated 9/17/14 with new column mapping that included return address and ; seperated format
# Betafresh parser

import os
import csv
import collections
import shutil
import validate
import settings
import mail
import tkinter.messagebox


# global list var for errors
errors = list()


def outputErrors():

    if errors:

        # show the errors in a message box
        tkinter.messagebox.showinfo(message='\n'.join(errors))

        # email the errors
        email('\n'.join(errors))

        # write the errors to a file
        if settings.isset('stacksocialerrordir'):
            with open(os.path.join(settings.get('stacksocialerrordir'),'errorlog.txt'), 'a') as f:
                for error in errors:
                    f.write(error + '\n')

        # delete the errors
        del errors[:]


def email(body):
    if settings.isset('mailstacksocialto'):
        to = settings.get('mailstacksocialto')
        subject = 'SkuTouch could not validate orders from StackSocial'
        print('Sending email to ' + to)
        mail.sendmail(to,subject,body)


def getNextFile():

    # source dir
    sourceDir = settings.get('stacksocialdrop')
    BetafreshDir = os.path.join(sourceDir,'Betafresh') # Stack Social only sells Betafresh
    
    for file in os.listdir(BetafreshDir):
        filename, ext = os.path.splitext(file)
        if ext == ".csv":
            return os.path.join(BetafreshDir,file)
            
    return ''


def archiveFile(path):

    # archive dir
    archivedir = settings.get('stacksocialarchive')
    
    # move file to archive folder
    if not os.path.isfile(os.path.join(archivedir, os.path.basename(path))):
        shutil.move(path, os.path.join(archivedir, os.path.basename(path)))
    else: # or delete it if it's already there
        os.remove(path)


def getOrders(path, columns):
    with open(path) as file:
        reader = csv.reader(file) # create a CSV reader object
        parsedRows = list() # create a list to hold the new rows

        for row in reader:
            
            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            if len(row) < 2 or row[13] == '':
                continue # skip if < 2 cols or no sku

            newRow['companyCode'] = 113
            newRow["completeOrderReference"] = validate.clean(row[0])
            newRow["shortOrderReference"] = validate.clean(row[0])
            newRow["originFile"] = os.path.basename(path)
            newRow["merchantID"] = 38
            newRow["fullName"] = validate.clean(row[11] + " " + row[12])
            newRow["phoneNumber"] = "".join([char for char in row[18] if str.isdigit(char)])
            newRow["address1"] = validate.clean(row[13])
            newRow['address2'] = validate.clean(row[14])
            newRow["town"] = validate.clean(row[15])
            newRow['packingSlip'] = 0
            
            newRow["country"] = validate.country(validate.clean(row[18]))
            if not newRow['country']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate country: ' + row[18] + '\n'
                errors.append(msg)
                continue
            
            newRow["region"] = validate.region(validate.clean(row[16]), newRow['country'])
            if not newRow['region']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate region: ' + row[16] + '\n'
                errors.append(msg)
                continue
                
            newRow["postCode"] = validate.postCode(validate.clean(row[17]), newRow['country'])
            if not newRow['postCode']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate post code: ' + row[17] + '\n'
                errors.append(msg)
                continue
            
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops StackSocial order parser added a column")
                quit()


        print("\nImported " + str(len(parsedRows)) + " orders from StackSocial file '" + os.path.basename(path) + "'")
        return parsedRows


def getItems(path, columns):
    with open(path) as file:
        reader = csv.reader(file)
        parsedRows = list()

        for row in reader:

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            if len(row) < 2 or row[13] == '':
                continue # skip if < 2 cols or no sku

            newRow["shortOrderReference"] = validate.clean(row[0])
            newRow["merchantID"] = 38

            newRow["lineNumber"] = 0
            skuCol = 20
            while skuCol < len(row) and row[skuCol]:
                newRow["lineNumber"] += 1
                newRow["itemSKU"] = row[skuCol]
                newRow["itemQuantity"] = row[skuCol+1]

                if len(columns) == len(newRow):
                    parsedRows.append(list(newRow.values()))
                else:
                    print("Oops StackSocial item parser added a column")
                    quit()
                
                skuCol += 2

        print("Imported " + str(len(parsedRows)) + " item lines from StackSocial file '" + os.path.basename(path) + "'")
        return(parsedRows)


def getPackages(path, columns):
    with open(path) as file:
        reader = csv.reader(file)
        parsedRows = list()

        for row in reader:

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            if len(row) < 2 or row[20] == '':
                continue # skip if < 2 cols or no sku

            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow['merchantID'] = 38
            newRow['returnCompany'] = validate.clean(row[4])
            newRow['returnAdd1'] = validate.clean(row[5])
            newRow['returnAdd2'] = validate.clean(row[6])
            newRow['returnCity'] = validate.clean(row[7])
            newRow['returnState'] = validate.clean(row[8])
            newRow['returnZip'] = validate.clean(row[9])
            newRow['bulk'] = 1
            newRow['packageNumber'] = 1
            newRow['carrier'] = 26
            newRow['serviceClass'] = 12

            itemNotes = list()
            skuCol = 20
            while skuCol < len(row) and row[skuCol]:
                itemNotes.append(row[skuCol+1]+'-'+row[skuCol]) # add sku and quantity to note
                skuCol += 2
            newRow['note'] = ','.join(itemNotes)

            
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops StackSocial package parser added a column")
                quit()

        print("Imported " + str(len(parsedRows)) + " packages from StackSocial file '" + os.path.basename(path) + "'")
        return parsedRows

