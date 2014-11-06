# Brenton Klassen
# 11/05/2014
# ncrowd parser

import os
import csv
import shutil
import collections
import validate
import settings
import productWeights
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
        if settings.isset('ncrowderrordir'):
            with open(os.path.join(settings.get('ncrowderrordir'),'errorlog.txt'), 'a') as f:
                for error in errors:
                    f.write(error + '\n')

        # delete the errors
        del errors[:]


def email(body):
    if settings.isset('mailncrowdto'):
        to = settings.get('mailncrowdto')
        subject = 'SkuTouch could not validate orders from ncrowd'
        print('Sending email to ' + to)
        mail.sendmail(to, subject, body)


def getNextFile():

    # source dir
    sourceDir = settings.get('ncrowddrop')

    for file in os.listdir(sourceDir):
        filename, ext = os.path.splitext(file)
        if ext == '.csv':
            return os.path.join(sourceDir,file)

    return ''


def archiveFile(path):

    # archive dir
    archiveDir = settings.get('ncrowdarchive')

    # move file to archive folder
    if not os.path.isfile(os.path.join(archiveDir, os.path.basename(path))):
        shutil.move(path, os.path.join(archiveDir, os.path.basename(path)))

    # or delete it if it's already there
    else:
        os.remove(path)


def getOrders(path, columns):
    with open(path) as file:
        prevRow = list()
        parsedRows = list()
        reader = csv.reader(file)
        next(reader) # skip header row

        for row in reader:

            if len(row) < 2 or (prevRow and row[0] == prevRow[0]):
                continue # skip if < 2 cols or same order as prev row

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            newRow['merchant'] = 'ncrowd'
            newRow['merchantID'] = 0
            newRow['completeOrderReference'] = validate.clean(row[0])
            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow['fullName'] = validate.clean(row[3]) + ' ' + validate.clean(row[4])
            newRow['phoneNumber'] = validate.phone(row[12])
            newRow['address1'] = validate.clean(row[7])
            newRow['address2'] = validate.clean(row[8])
            newRow['town'] = validate.clean(row[9])
            newRow['packingSlip'] = 1
            newRow['country'] = 'US'

            newRow['region'] = validate.region(validate.clean(row[10]), newRow['country'])
            if not newRow['region']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate region: ' + row[10]
                errors.append(msg)
                continue

            newRow['postCode'] = validate.postCode(validate.clean(row[11]), newRow['country'])
            if not newRow['postCode']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate post code: ' + row[11]
                errors.append(msg)
                continue

            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, LTM order parser added a column")
                quit()

            prevRow = row

    print("\nImported " + str(len(parsedRows)) + " orders from ncrowd file '" + os.path.basename(path) + "'")
    return parsedRows


def getItems(path, columns):
    with open(path) as file:
        reader = csv.reader(file)
        parsedRows = list()
        prevRow = list()
        next(reader) # skip first row

        for row in reader:

            if len(row) < 2:
                continue # skip if < 2 columns

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            newRow['merchantID'] = 0
            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow['lineNumber'] = 1
            newRow['itemSKU'] = validate.clean(row[15])
            newRow['itemQuantity'] = 1
            

            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, ncrowd item parser added a column")
                quit()

            prevRow = row

    print("Imported " + str(len(parsedRows)) + " item rows from ncrowd file '" + os.path.basename(path) + "'")
    return parsedRows


def getPackages(path, columns):

    lines = list() # this list will hold the whole file
    parsedRows = list()

    with open(path) as file:
        reader = csv.reader(file)
        next(reader) # skip header

        # read the whole file into memory
        for row in reader:

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            # FIGURE OUT WHAT TO DO WITH THIS ORDER

            newRow['merchantID'] = 0
            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow["bulk"] = 0

            # save the package row in completedLines
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, DSOL shipping allocator added a column")
                quit()

        
    print("Created " + str(len(parsedRows)) + " packages from '" + os.path.basename(path) + "'")
    return parsedRows
