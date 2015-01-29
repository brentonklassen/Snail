# Brenton Klassen
# 08/25/2014
# Import settings for Snail

import csv
import os

settingsPath = '..\\settings.dat'
settings = dict()

print('Loading settings...')
with open(settingsPath) as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        
        if len(row) < 2: pass

        key = row[0].strip().upper()
        val = row[1].strip()
        
        settings[key] = val

    settings['BASEPATH'] = os.path.join(os.getcwd(),os.pardir)


def isset(key):
    return (key.upper() in settings) and settings[key.upper()]


def get(key):
    return settings[key.upper()]
