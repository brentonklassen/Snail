# Brenton Klassen
# Created 8/19/2014
# Updated 9/17/2014

import string
import csv
import re

print('Loading validation data...')

countries = set()
with open('validate\\countries.tsv') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        countries.add(tuple(row))

states = set()
with open('validate\\states.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        states.add(tuple(row))


provinces = set()
with open('validate\\provinces.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        provinces.add(tuple(row))


def clean(s):
    # this creates a new string made of only printable characters
    # and also strips the result of surrounding whitespace
    return ''.join(filter(lambda x: x in string.printable, s)).strip()


def country(c):
    
    for abbrev, country in countries:
        if c.upper() == abbrev.upper():
            return abbrev.upper()
        elif c.upper() == country.upper():
            return abbrev.upper()
        
    return ''


def region(r, country='US'):
    
    if country == 'US':
        for state, abbrev in states:
            if r.upper() == abbrev.upper():
                return abbrev.upper()
            elif r.upper() == state.upper():
                return abbrev.upper()
            
    elif country == 'CA':
        for province, abbrev in provinces:
            if r.upper() == abbrev.upper():
                return abbrev.upper()
            elif r.upper() == province.upper():
                return abbrev.upper()

    elif country == 'PR' and r.upper() == 'PUERTO RICO':
        return 'PR'

    elif country == 'VI' and r.upper() == 'VIRGIN ISLANDS':
        return 'VI'
            
    elif len(r) < 5:
        return r
    
    return ''


def postCode(p, country='US'):

    if country == 'US':
        match = re.match('^(\d{5})(?:[-\s]\d{4})?$', p)
        if match:
            return match.group(1)

    elif country == 'CA':
        match = re.match('^[ABCEGHJKLMNPRSTVXY]{1}\d{1}[A-Z]{1} *\d{1}[A-Z]{1}\d{1}$', p.upper())
        if match:
            return match.group(0)

    elif len(p) < 11:
        return p

    return ''


def phone(p):
    
    # return only digits
    return ''.join([char for char in p if str.isdigit(char)])
