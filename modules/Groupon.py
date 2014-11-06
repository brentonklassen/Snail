# Brenton Klassen
# 11/04/2014
# Groupon parser

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
        if settings.isset('grouponerrordir'):
            with open(os.path.join(settings.get('grouponerrordir'),'errorlog.txt'), 'a') as f:
                for error in errors:
                    f.write(error + '\n')

        # delete the errors
        del errors[:]


def email(body):
    if settings.isset('mailgrouponto'):
        to = settings.get('mailgrouponto')
        subject = 'SkuTouch could not validate orders from Groupon'
        print('Sending email to ' + to)
        mail.sendmail(to, subject, body)


def getNextFile():

    # source dir
    sourceDir = settings.get('groupondrop')

    # Groupon has several merhcants each with
    # their own drop folders. Go through these.
    companies = [os.path.join(sourceDir,subdir) for subdir in os.listdir(sourceDir) if os.path.isdir(os.path.join(sourceDir,subdir))]

    for company in companies:
        for file in os.listdir(company):
            filename, ext = os.path.splitext(file)
            if ext == '.csv':
                return os.path.join(company,file)

    return ''


def archiveFile(path):

    # archive dir
    archiveDir = settings.get('grouponarchive')

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


            if len(row) < 2 or not row[0]:
                continue # skip if < 2 cols no order number

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            newRow['company'] = os.path.split(os.path.dirname(path))[1]
            newRow['merchantID'] = 36
            newRow['completeOrderReference'] = validate.clean(row[0])
            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow['fullName'] = validate.clean(row[6])
            newRow['phoneNumber'] = validate.phone(row[40])
            newRow['address1'] = validate.clean(row[7])
            newRow['address2'] = validate.clean(row[8])
            newRow['town'] = validate.clean(row[9])
            newRow['packingSlip'] = 1
            
            newRow['country'] = validate.country(validate.clean(row[12]))
            if not newRow['country']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate country: ' + row[12]
                errors.append(msg)
                continue

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
                print("Oops, Groupon order parser added a column")
                quit()

    print("\nImported " + str(len(parsedRows)) + " orders from Groupon file '" + os.path.basename(path) + "'")
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

            newRow['merchantID'] = 36
            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow['lineNumber'] = 1
            newRow['itemTitle'] = validate.clean(row[23])
            newRow['itemSKU'] = validate.clean(row[3])
            newRow['itemQuantity'] = 1
            

            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, Lighttake item parser added a column")
                quit()

            prevRow = row

    print("Imported " + str(len(parsedRows)) + " item rows from Lighttake file '" + os.path.basename(path) + "'")
    return parsedRows


def getPackages(path, columns):

    parsedRows = list()

    with open(path) as file:
        reader = csv.reader(file)
        next(reader) # skip header

        # read the whole file into memory
        for row in reader:

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            newRow['merchantID'] = 36
            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow["bulk"] = 0
            newRow["carrier"] = 26
            newRow['weight'] = validate.clean(row[34])

            # save the package row in completedLines
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, DSOL shipping allocator added a column")
                quit()

    print("Created " + str(len(parsedRows)) + " packages from '" + os.path.basename(path) + "'")
    return parsedRows
