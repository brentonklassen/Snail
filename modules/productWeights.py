# Brenton Klassen
# 08/25/2014
# Import settings for Snail

import csv
import os
import settings

productWeightsPath = os.path.join(settings.get('basepath'),'productWeights.dat')
productWeights = dict()

print('Loading product weights...')
with open(productWeightsPath) as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        
        if len(row) < 3:
            pass
        
        productWeights[(row[0].strip(),row[1].strip())] = row[2].strip()


def isset(key):
    return (key in productWeights) and productWeights[key]


def get(key):

	if isset(key):
		return productWeights[key]
	else:
		return ''
