# Brenton Klassen
# 07/30/2014
# Dance Shoes Online parser

import os
import csv
import collections
import shutil
import validate
import settings
import mail
import fractions
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
        if settings.isset('dsolerrordir'):
            with open(os.path.join(settings.get('dsolerrordir'),'errorlog.txt'), 'a') as f:
                for error in errors:
                    f.write(error + '\n')

        # delete the errors
        del errors[:]


def email(body):
    if settings.isset('mailDSOLto'):
        to = settings.get('mailDSOLto')
        subject = 'SkuTouch could not validate orders from Dance Shoes Online'
        print('Sending email to ' + to)
        mail.sendmail(to, subject, body)


def getNextFile():

    # source dir
    sourceDir = settings.get('dsoldrop')
    
    for file in os.listdir(sourceDir):
        filename, ext = os.path.splitext(file)
        if ext == ".csv":
           return os.path.join(sourceDir,file)

    return ''


def archiveFile(path):

    # archive location
    archiveDir = settings.get('dsolarchive')
    
    # move file to archive folder
    if not os.path.isfile(os.path.join(archiveDir, os.path.basename(path))):
        shutil.move(path, os.path.join(archiveDir, os.path.basename(path)))
    else: # or delete it if it's already there
        os.remove(path)


def getOrders(path, columns):
    with open(path) as file:
        reader = csv.reader(file) # create a CSV reader object
        parsedRows = list() # create a list to hold the new rows
        next(reader) # skip header row

        for row in reader:

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)
            
            if len(row) < 2 or not row[10].strip():
                continue # skip row if < 2 cols or no sku
            
            if row[0]: # this line has an order number

                # map info from input file row to new row dict
                order_number = validate.clean(row[0]).replace(' ','')
                if '&' in order_number:
                    newRow["completeOrderReference"] = order_number.replace('&','/')
                    newRow["shortOrderReference"] = validate.shortenPossibleAmazon(order_number.split('&')[0])
                else:
                    newRow["completeOrderReference"] = order_number
                    newRow["shortOrderReference"] = validate.shortenPossibleAmazon(order_number)

                newRow["companyCode"] = 97
                newRow["merchantID"] = 10
                newRow["fullName"] = row[1].strip() + " " + row[2].strip()
                newRow["phoneNumber"] = "".join([char for char in row[8] if str.isdigit(char)])
                newRow["emailAddress"] = row[9].strip()
                newRow["address1"] = row[3].strip()
                newRow["town"] = row[4].strip()
                
                newRow['country'] = validate.country(validate.clean(row[7]))
                if not newRow['country']:
                    msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                    msg += 'Could not validate country: ' + row[7] + '\n'
                    errors.append(msg)
                    continue

                newRow["region"] = validate.region(validate.clean(row[5]), newRow['country'])
                if not newRow["region"]:
                    msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                    msg += 'Could not validate state: ' + row[5] + '\n'
                    errors.append(msg)
                    continue

                newRow['postCode'] = validate.postCode(validate.clean(row[6]), newRow['country'])
                if not newRow['postCode']:
                    msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                    msg += 'Could not validate post code: ' + row[6] + '\n'
                    errors.append(msg)
                    continue
                
                newRow["packingSlip"] = 1

                if len(columns) == len(newRow):
                    parsedRows.append(list(newRow.values()))
                else:
                    print("Oops, DSOL order parser added a column")
                    quit()

                    
        print("\nImported " + str(len(parsedRows)) + " orders from Dance Shoes Online file '" + os.path.basename(path) + "'")
        return parsedRows


def getItems(path, columns):
    with open(path) as file:
        reader = csv.reader(file) # create a CSV reader object
        parsedRows = list() # create a list to hold the new rows
        orderLine = 0
        next(reader) # skip header row

        for row in reader:
            
            overstock = False

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)
            
            if len(row) < 2 or not row[10].strip():
                continue # skip row if < 2 cols or no sku
            
            if row[0]: # this line has an order number
                # we've found a new order
                orderLine = 1 # reset line number to 1
                
            else: # this line has no order number
                # this is another line of the same order
                orderLine += 1 # increment the line number
                row[0] = prevRef # use the order reference from the previous line

            # map info from input file row to new row dict
            
            order_number = validate.clean(row[0]).replace(' ','')
            if '&' in order_number:
                newRow["shortOrderReference"] = validate.shortenPossibleAmazon(order_number.split('&')[0])
            else:
                newRow["shortOrderReference"] = validate.shortenPossibleAmazon(order_number)
                
            newRow["merchantID"] = 10
            newRow["lineNumber"] = orderLine

            if row[10][-3:] == "-OS":
                newRow["itemSKU"] = row[10][:-3].strip()
                overstock = True
            else:
                newRow["itemSKU"] = row[10].strip()
                
            newRow["itemQuantity"] = row[11].strip()

            # write out row with size
            newRow["itemAttribKey"] = "size"
            newRow["itemAttribVal"] = row[12].strip()

            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, DSOL item parser added a column")
                quit()

            # write out row with heel
            newRow["itemAttribKey"] = "heel"
            newRow["itemAttribVal"] = row[13].strip()
            
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, DSOL item parser added a column")
                quit()

            # write out row with width
            newRow["itemAttribKey"] = "width"
            newRow["itemAttribVal"] = row[14].strip()

            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops, DSOL item parser added a column")
                quit()

            # write out row with bin/us code
            if row[15].strip():
                newRow['itemAttribKey'] = 'bin'
                newRow['itemAttribVal'] = validate.clean(row[15]).strip()

                if len(columns) == len(newRow):
                    parsedRows.append(list(newRow.values()))
                else:
                    print("Oops, DSOL item parser added a column")
                    quit()
                

            # add overstock attrib
            if overstock:
                newRow["itemAttribKey"] = "overstock"
                newRow["itemAttribVal"] = "true"
                
                if len(columns) == len(newRow):
                    parsedRows.append(list(newRow.values()))
                else:
                    print("Oops, DSOL item parser added a column")
                    quit()

            prevRef = row[0] # keep reference in case next row needs it

        print("Imported " + str(len(parsedRows)) + " item rows from Dance Shoes Online file '" + os.path.basename(path) + "'")
        return parsedRows


def getPackages(path, columns):

    mensSkus = ["A330101","A350501"]

    lines = list() # this list will hold the whole file
    completedLines = list()

    with open(path) as file:
        reader = csv.reader(file)
        next(reader) # skip header row
        for row in reader:
            # read the whole file into memory so that I can index it and
            # iterate over parts of it multiple times
            if len(row) > 2 and row[10]: # if > 2 cols and sku exists
                lines.append(row)

    orderStart = 0
    orderEnd = 0
    while orderEnd < len(lines):

        orderEnd += 1
        while orderEnd < len(lines) and not lines[orderEnd][0].strip(): # while the line has no order number
            orderEnd += 1 # increment the orderEnd counter

        # grab the slice of the file that contains the next order
        currentOrder = lines[orderStart:orderEnd]

        # create a new ordered dictionary to hold the row info
        newRow = collections.OrderedDict.fromkeys(columns)

        # FIGURE OUT WHAT TO DO WITH THIS ORDER
        
        order_number = validate.clean(currentOrder[0][0]).replace(' ','')
        if '&' in order_number:
            newRow["shortOrderReference"] = validate.shortenPossibleAmazon(order_number.split('&')[0])
        else:
            newRow["shortOrderReference"] = validate.shortenPossibleAmazon(order_number)
    
        country = validate.country(validate.clean(currentOrder[0][7]))
        
        newRow["merchantID"] = 10
        newRow["returnCompany"] = "DanceShoesOnline.com"
        newRow["returnAdd1"] = "8527 BLUEJACKET STREET"
        newRow["returnCity"] = "Lenexa"
        newRow["returnState"] = "KS"
        newRow["returnZip"] = "66214-1656"
        newRow["bulk"] = 0

        itemCount = sum(int(row[11]) for row in currentOrder)

        # orders with 1 item
        if itemCount == 1:
            line = currentOrder[0]
            if line[10][-3:] == "-OS":
                sku = line[10][:-3].strip()
            else:
                sku = line[10].strip()
            womens = sku not in mensSkus
            size = float(sum(fractions.Fraction(s) for s in line[12].split()))

            if size < 9 and womens:
                newRow["packageNumber"] = 1
                newRow["carrier"] = 26
                newRow["serviceClass"] = 10
                newRow["length"] = 10.25
                newRow["width"] = 7
                newRow["height"] = 3.5
                if size < 7:
                    newRow["weight"] = 1
                else:
                    newRow["weight"] = 1.2
                newRow['note'] = 'Small box'

            # 1 women's 9 and above or 1 men's
            else:
                newRow["packageNumber"] = 1
                newRow["carrier"] = 26
                newRow["serviceClass"] = 10
                newRow["length"] = 12.25
                newRow["width"] = 7.25
                newRow["height"] = 4.25
                newRow["weight"] = 1.2
                newRow['note'] = 'Large box'

        # orders with 2 items
        elif itemCount == 2:

            # assume we will be able to ship combo
            # and then try to prove this false
            canShipCombo = True
            for line in currentOrder:
                if line[10][-3:] == "-OS":
                    sku = line[10][:-3].strip()
                else:
                    sku = line[10].strip()
                womens = sku not in mensSkus
                size = float(sum(fractions.Fraction(s) for s in line[12].split()))

                if not womens or not size < 9:
                    canShipCombo = False

            if canShipCombo:
                newRow["packageNumber"] = 1
                newRow["carrier"] = 26
                newRow["serviceClass"] = 10
                newRow["length"] = 14
                newRow["width"] = 10.25
                newRow["height"] = 3.5
                newRow["weight"] = 2.2
                newRow['note'] = 'Double box'

            else:
                # create a generic USPS package
                newRow['packageNumber'] = 1
                newRow['carrier'] = 26
                newRow['serviceClass'] = 10
                newRow['note'] = 'Dim add'

        # orders with more than 2 items
        else:

            if country == 'PR':
                # create a generic USPS package
                newRow['packageNumber'] = 1
                newRow['carrier'] = 26
                newRow['serviceClass'] = 10
                newRow['note'] = 'Dim add'

            else:
                orderStart = orderEnd # move on to the next order
                continue # don't create a package


        # save the package row in completedLines
        if len(columns) == len(newRow):
            completedLines.append(list(newRow.values()))
        else:
            print("Oops, DSOL shipping allocator added a column")
            quit()

        orderStart = orderEnd # move on to the next order


    print("Created " + str(len(completedLines)) + " packages from '" + os.path.basename(path) + "'")
    return completedLines

