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
        
        if len(row) < 2:
            pass
        
        settings[row[0].strip()] = row[1].strip()

    settings['basepath'] = os.path.join(os.getcwd(),os.pardir)


def isset(key):
    return (key in settings) and settings[key]


def get(key):
    return settings[key]
