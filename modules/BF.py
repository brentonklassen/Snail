# Brenton Klassen
# 07/30/2014
# Updated 9/17/14 with new column mapping that included return address and ; seperated format
# Betafresh parser

import os
import csv
import time
import collections
import shutil
import validate
import settings
import mail


# global list var for errors
errors = list()


def getErrors():
    errorsToReturn = tuple(errors)
    del errors[:]
    return errorsToReturn


def email(body):
    if settings.isset('mailBFto'):
        to = settings.get('mailBFto')
        subject = 'SkuTouch could not validate orders from Betafresh'
        print('Sending email to ' + to)
        mail.sendmail(to,subject,body)


def getFiles():

    # source dir
    sourceDir = settings.get('bfdrop')

    files = list()
    
    for file in os.listdir(sourceDir):
        filename, ext = os.path.splitext(file)
        if ext == ".csv":
            files.append(os.path.join(sourceDir,file))
            
    return files


def archiveFile(path):

    # archive dir
    archivedir = settings.get('bfarchive')
    
    # move file to archive folder
    if not os.path.isfile(os.path.join(archivedir, os.path.basename(path))):
        shutil.move(path, os.path.join(archivedir, os.path.basename(path)))
    else: # or delete it if it's already there
        os.remove(path)


def getOrders(path, columns):
    with open(path) as file:
        reader = csv.reader(file,delimiter=';') # create a CSV reader object
        parsedRows = list() # create a list to hold the new rows
        next(reader) # skip header row

        for row in reader:
            
            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            if len(row) < 2 or row[13] == '':
                continue # skip if < 2 cols or no sku

            newRow['merchant'] = 'Betafresh'
            newRow["completeOrderReference"] = validate.clean(row[0])
            newRow["shortOrderReference"] = validate.clean(row[0])
            newRow["merchantID"] = 38
            newRow["fullName"] = validate.clean(row[11] + " " + row[12])
            newRow["phoneNumber"] = "".join([char for char in row[18] if str.isdigit(char)])
            newRow["address1"] = validate.clean(row[13])
            newRow["town"] = validate.clean(row[14])
            
            newRow["country"] = validate.country(row[17])
            if not newRow['country']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate country: ' + row[17]
                errors.append(msg)
                continue
            
            newRow["region"] = validate.region(row[15], newRow['country'])
            if not newRow['region']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate region: ' + row[15]
                errors.append(msg)
                continue
                
            newRow["postCode"] = validate.postCode(row[16], newRow['country'])
            if not newRow['postCode']:
                msg = newRow['completeOrderReference'] + " from file '" + os.path.basename(path) + "' was skipped.\n"
                msg += 'Could not validate post code: ' + row[16]
                errors.append(msg)
                continue
            
            newRow["dateStamp"] = time.strftime("%Y-%m-%d")
            newRow['packingSlip'] = 1
            
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops BF order parser added a column")
                quit()

        if errors:
            print()
            print('FIX ERRORS, RECORDS WERE SKIPPED')
            print('\n'+'\n'.join(errors))
            print('\nEND SKIP RECORD SECTION')
            print()
            email('\n'.join(errors))
        print("\nImported " + str(len(parsedRows)) + " orders from Betafresh file '" + os.path.basename(path) + "'")
        return parsedRows


def getItems(path, columns):
    with open(path) as file:
        reader = csv.reader(file,delimiter=';')
        parsedRows = list()
        next(reader) # skip header

        for row in reader:

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            if len(row) < 2 or row[13] == '':
                continue # skip if < 2 cols or no sku

            newRow["shortOrderReference"] = validate.clean(row[0])
            newRow["merchantID"] = 38

            newRow["lineNumber"] = 0
            skuCol = 19
            while skuCol < len(row) and row[skuCol]:
                newRow["lineNumber"] += 1
                newRow["itemSKU"] = row[skuCol]
                newRow["itemQuantity"] = row[skuCol+1]

                if len(columns) == len(newRow):
                    parsedRows.append(list(newRow.values()))
                else:
                    print("Oops BF item parser added a column")
                    quit()
                
                skuCol += 2

        print("Imported " + str(len(parsedRows)) + " item lines from Betafresh file '" + os.path.basename(path) + "'")
        return(parsedRows)


def getPackages(path, columns):
    with open(path) as file:
        reader = csv.reader(file,delimiter=';')
        parsedRows = list()
        next(reader)

        for row in reader:

            # create a new ordered dictionary to hold the row info
            newRow = collections.OrderedDict.fromkeys(columns)

            if len(row) < 2 or row[13] == '':
                continue # skip if < 2 cols or no sku

            newRow['shortOrderReference'] = validate.clean(row[0])
            newRow['merchantID'] = 38
            newRow['returnCompany'] = validate.clean(row[4])
            newRow['returnAdd1'] = validate.clean(row[5])
            newRow['returnAdd2'] = validate.clean(row[6])
            newRow['returnCity'] = validate.clean(row[7])
            newRow['returnState'] = validate.region(row[8])
            newRow['returnZip'] = validate.postCode(row[9])
            newRow['dateStamp'] = time.strftime("%Y-%m-%d")
            newRow['bulk'] = 1
            newRow['packageNumber'] = 1
            newRow['carrier'] = 26
            newRow['serviceClass'] = 12

            
            if len(columns) == len(newRow):
                parsedRows.append(list(newRow.values()))
            else:
                print("Oops BF package parser added a column")
                quit()

        print("Imported " + str(len(parsedRows)) + " packages from Betafresh file '" + os.path.basename(path) + "'")
        return parsedRows

