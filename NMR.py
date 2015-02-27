# Brenton Klassen
# 01/01/2015
# NMR parser

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
        if settings.isset('nmrerrordir'):
            with open(os.path.join(settings.get('nmrerrordir'),'errorlog.txt'), 'a') as f:
                for error in errors:
                    f.write(error + '\n')

        # delete the errors
        del errors[:]


def email(body):
    if settings.isset('mailnmrto'):
        to = settings.get('mailnmrto')
        subject = 'SkuTouch could not validate orders from NMR'
        print('Sending email to ' + to)
        mail.sendmail(to, subject, body)


def getNextFile():

    # source dir
    sourceDir = settings.get('nmrdrop')

    for file in os.listdir(sourceDir):
        filename, ext = os.path.splitext(file)
        if ext == '.csv':
            return os.path.join(sourceDir,file)

    return ''


def archiveFile(path):

    # archive dir
    archiveDir = settings.get('nmrarchive')

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

            newRow['companyCode'] = 112 # marvellous
            newRow['merchantID'] = 40

            newRow['completeOrderReference'] = validate.clean(row[1])
            newRow['shortOrderReference'] = validate.clean(row[1])
            newRow['fullName'] = validate.clean(row[6]) + ' ' + validate.clean(row[7])
            newRow['phoneNumber'] = validate.phone(row[23])
            newRow['address1'] = validate.clean(row[8])
            newRow['address2'] = validate.clean(row[9])
            newRow['town'] = validate.clean(row[10])
            newRow['packingSlip'] = 1
            
            newRow['country'] = validate.country(validate.clean(row[13]))
            if not newRow['country']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate country: ' + row[13]
                errors.append(msg)
                continue

            newRow['region'] = validate.region(validate.clean(row[11]), newRow['country'])
            if not newRow['region']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate region: ' + row[11]
                errors.append(msg)
                continue

            newRow['postCode'] = validate.postCode(validate.clean(row[12]), newRow['country'])
            if not newRow['postCode']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate post code: ' + row[12]
                errors.append(msg)
                continue

            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, NMR order parser added a column")
                quit()

            prevRow = row

    print("\nImported " + str(len(parsedRows)) + " orders from NMR file '" + os.path.basename(path) + "'")
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

            if prevRow and row[0] == prevRow[0]:
                lineNumber += 1
            else:
                lineNumber = 1

            newRow['merchantID'] = 40
            newRow['shortOrderReference'] = validate.clean(row[1])
            newRow['lineNumber'] = lineNumber
            newRow['itemTitle'] = validate.clean(row[20])
            newRow['itemSKU'] = validate.clean(row[15]) # grab after the last -
            newRow['itemQuantity'] = validate.clean(row[19])
            

            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, NMR item parser added a column")
                quit()

            prevRow = row

    print("Imported " + str(len(parsedRows)) + " item rows from NMR file '" + os.path.basename(path) + "'")
    return parsedRows


def getPackages(path, columns):

    lines = list() # this list will hold the whole file
    parsedRows = list()

    with open(path) as file:
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
        while orderEnd < len(lines) and lines[orderEnd][1] == lines[orderStart][1]:
            orderEnd += 1

        # grab the slice of the file that contains the next order
        currentOrder = lines[orderStart:orderEnd]

        # create a new ordered dictionary to hold the row info
        newRow = collections.OrderedDict.fromkeys(columns)

        # FIGURE OUT WHAT TO DO WITH THIS ORDER

        newRow['merchantID'] = 40
        newRow['shortOrderReference'] = validate.clean(currentOrder[0][1])
        newRow['returnCompany'] = 'Nomorerack.com'
        newRow['returnCompany2'] = 'Customer Service: customercare@nomorerack.com'
        newRow['returnAdd1'] = '8900 Rosehill Rd'
        newRow['returnAdd2'] = 'Unit B Dock'
        newRow['returnCity'] = 'Lenexa'
        newRow['returnState'] = 'KS'
        newRow['returnZip'] = '66215'
        newRow["bulk"] = 0

        newRow["carrier"] = 26
        newRow['serviceClass'] = 12
        newRow['weight'] = float(4/16);

        # save the package row in completedLines
        if len(columns) == len(newRow):
            parsedRows.append(list(newRow.values()))
        else:
            print("Oops, NMR shipping allocator added a column")
            quit()

        orderStart = orderEnd # move on to the next order
        
    print("Created " + str(len(parsedRows)) + " packages from '" + os.path.basename(path) + "'")

    return parsedRows
