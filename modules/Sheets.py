# Brenton Klassen
# 10/07/2014
# Sheets parser

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
        if settings.isset('sheetserrordir'):
            with open(os.path.join(settings.get('sheetserrordir'),'errorlog.txt'), 'a') as f:
                for error in errors:
                    f.write(error + '\n')

        # delete the errors
        del errors[:]


def email(body):

    if settings.isset('mailSheetsto'):

        to = settings.get('mailSheetsto')
        subject = 'SkuTouch could not validate orders from Sheets'
        print('Sending email to ' + to)
        mail.sendmail(to,subject,body)


def getNextFile():

    # source dir
    sourceDir = settings.get('sheetsdrop')
    
    for file in os.listdir(sourceDir):
        filename, ext = os.path.splitext(file)
        if ext == ".csv":
            return os.path.join(sourceDir,file)
            
    return ''


def archiveFile(path):

    # archive dir
    archivedir = settings.get('sheetsarchive')
    
    # move file to archive folder
    if not os.path.isfile(os.path.join(archivedir, os.path.basename(path))):
        shutil.move(path, os.path.join(archivedir, os.path.basename(path)))
    else: # or delete it if it's already there
        os.remove(path)


def getOrders(path, columns):

    print("Getting orders from " + path)

    with open(path) as file:
        reader = csv.reader(file) # create a CSV reader object
        parsedRows = list() # create a list to hold the new rows
        next(reader) # skip header row

        for row in reader:
            
            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            if len(row) < 2 or row[17] == '' or not row[51]:
                continue # skip if < 2 cols or no item name or no order number

            print('Parsing '+row[0])

            newRow['merchant'] = 'Sheets'
            newRow["completeOrderReference"] = validate.clean(row[51])
            newRow["shortOrderReference"] = validate.clean(row[51])
            newRow["merchantID"] = 30
            newRow["fullName"] = validate.clean(row[34])
            newRow["phoneNumber"] = validate.phone(row[43])
            newRow["address1"] = validate.clean(row[36])
            newRow['address2'] = validate.clean(row[37])
            newRow["town"] = validate.clean(row[39])
            newRow['packingSlip'] = 1
            
            newRow["country"] = validate.country(validate.clean(row[42]))
            if not newRow['country']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate country: ' + row[42] + '\n'
                errors.append(msg)
                continue
            
            newRow["region"] = validate.region(validate.clean(row[41]), newRow['country'])
            if not newRow['region']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate region: ' + row[41] + '\n'
                errors.append(msg)
                continue
                
            newRow["postCode"] = validate.postCode(validate.clean(row[40]), newRow['country'])
            if not newRow['postCode']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate post code: ' + row[40] + '\n'
                errors.append(msg)
                continue
            
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops BF order parser added a column")
                quit()


        print("\nImported " + str(len(parsedRows)) + " orders from Sheets file '" + os.path.basename(path) + "'")
        return parsedRows

