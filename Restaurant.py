# Brenton Klassen
# 09/09/2014
# Restaurant parser

import os
import csv
import shutil
import collections
import operator
import validate
import settings
import productWeights
import tkinter.messagebox


# global list var for errors
errors = list()
data = list()

def outputErrors():

    if errors:

        # show the errors in a message box
        tkinter.messagebox.showinfo(message='\n'.join(errors))

        # email the errors
        email('\n'.join(errors))

        # write the errors to a file
        if settings.isset('restauranterrordir'):
            with open(os.path.join(settings.get('restauranterrordir'),'errorlog.txt'), 'a') as f:
                for error in errors:
                    f.write(error + '\n')

        # delete the errors
        del errors[:]


def email(body):
    if settings.isset('mailrestaurantto'):
        to = settings.get('mailrestaurantto')
        subject = 'SkuTouch could not validate orders from Restaurant'
        print('Sending email to ' + to)
        mail.sendmail(to, subject, body)


def getNextFile():

    # source dir
    sourceDir = settings.get('restaurantdrop')
    MarvellousDrop = os.path.join(sourceDir,'Marvellous')

    for file in os.listdir(MarvellousDrop):
        filename, ext = os.path.splitext(file)
        if ext == '.csv':
            return os.path.join(MarvellousDrop,file)

    return ''


def archiveFile(path):

    # archive dir
    archiveDir = settings.get('restaurantarchive')

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
        data = sorted(reader, key=operator.itemgetter(0))

        for row in data:

            if len(row) < 2 or (prevRow and row[0] == prevRow[0]):
                continue # skip if < 2 cols or same order as prev row

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            newRow['companyCode'] = 112 # marvellous
            newRow['merchantID'] = 42

            newRow['completeOrderReference'] = validate.clean(row[0])
            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow["originFile"] = os.path.basename(path)
            newRow['fullName'] = validate.clean(row[17])
            newRow['phoneNumber'] = validate.phone(row[7])
            newRow['address1'] = validate.clean(row[18])
            newRow['address2'] = validate.clean(row[19])
            newRow['town'] = validate.clean(row[20])
            newRow['packingSlip'] = 1
            
            newRow['country'] = validate.country(validate.clean(row[23]))
            if not newRow['country']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate country: ' + row[23]
                errors.append(msg)
                continue

            newRow['region'] = validate.region(validate.clean(row[21]), newRow['country'])
            if not newRow['region']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate region: ' + row[21]
                errors.append(msg)
                continue

            newRow['postCode'] = validate.postCode(validate.clean(row[22]), newRow['country'])
            if not newRow['postCode']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate post code: ' + row[22]
                errors.append(msg)
                continue

            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, Restaurant order parser added a column")
                quit()

            prevRow = row

    print("\nImported " + str(len(parsedRows)) + " orders from Restaurant file '" + os.path.basename(path) + "'")
    return parsedRows


def getItems(path, columns):
    with open(path) as file:
        reader = csv.reader(file)
        parsedRows = list()
        prevRow = list()
        next(reader) # skip first row
        data = sorted(reader, key=operator.itemgetter(0))

        for row in data:

            if len(row) < 2:
                continue # skip if < 2 columns

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            if prevRow and row[0] == prevRow[0]:

                # if this is another row of the same item
                if row[36] == prevRow[36]:
                    # grab the last row and increment the qty
                    parsedRows[-1][5] = int(parsedRows[-1][5]) + 1
                    continue # ignore this line

                # else, make a new line
                lineNumber += 1
            else:
                lineNumber = 1

            newRow['merchantID'] = 42
            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow['lineNumber'] = lineNumber
            newRow['itemTitle'] = validate.clean(row[3])
            newRow['itemSKU'] = validate.clean(row[36])
            newRow['itemQuantity'] = validate.clean(row[12])

            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, Restaurant item parser added a column")
                quit()

            prevRow = row

    print("Imported " + str(len(parsedRows)) + " item rows from Restaurant file '" + os.path.basename(path) + "'")
    return parsedRows


def getPackages(path, columns):

    lines = list()
    parsedRows = list()

    with open(path) as file:
        reader = csv.reader(file)
        next(reader) # skip header row
        data = sorted(reader, key=operator.itemgetter(0))
        for row in data:
            # read the whole file into memory so that I can index it and
            # iterate over parts of it multiple times
            if len(row) > 2 and row[10]: # if > 2 cols and sku exists
                lines.append(row)


    orderStart = 0
    orderEnd = 0
    while orderEnd < len(lines):

        orderEnd += 1
        while orderEnd < len(lines) and lines[orderStart][0] == lines[orderEnd][0]:
            orderEnd += 1 # increment the orderEnd counter

        # grab the slice of the file that contains the next order
        currentOrder = lines[orderStart:orderEnd]

        # create a new ordered dictionary to hold the row info
        newRow = collections.OrderedDict.fromkeys(columns)

        # FIGURE OUT WHAT TO DO WITH THIS ORDER

        # count skus to set for unique set
        skus = set()
        for line in currentOrder:
            skus.add(line[36])

        if len(skus) == 1:
            sku = skus.pop()
            qty = sum(int(row[12]) for row in currentOrder)
            newRow['merchantID'] = 42
            newRow['shortOrderReference'] = validate.clean(currentOrder[0][0])
            newRow["carrier"] = 26
            newRow['serviceClass'] = 12
            newRow["bulk"] = 1
            newRow['note'] = str(qty) + '-' + sku

            # save the package row in completedLines
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, Restaurant shipping allocator added a column")
                quit()

        else: 
            newRow['merchantID'] = 42
            newRow['shortOrderReference'] = validate.clean(currentOrder[0][0])
            newRow["carrier"] = 26
            newRow['serviceClass'] = 12
            newRow["bulk"] = 0

            # save the package row in completedLines
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, Restaurant shipping allocator added a column")
                quit()


        orderStart = orderEnd # move on to the next order

        
    print("Created " + str(len(parsedRows)) + " packages from '" + os.path.basename(path) + "'")
    return parsedRows
