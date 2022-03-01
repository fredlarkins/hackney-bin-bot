#! /usr/bin/python3
'''
What will this script do?

tl;dr:
- The script will ask the user to find their address;
- Check the waste collection services available for that address;
- Check the collection days for those services;
- Write that data to a file

See explainer.md for a detailed explanation of what's going on. 
    '''

import requests
import json
import sys
import re


# creating a re-useable session object that we'll use throughout the script
session = requests.session()

# saving the three different endpoints used throughout this workflow as separate variables
aqs_query_endpoint = 'https://api.uk.alloyapp.io/api/aqs/query'
item_endpoint = 'https://api.uk.alloyapp.io/api/aqs/item/'
workflow_endpoint = 'https://api.uk.alloyapp.io/api/workflow/'

# reading the json files for the payloads in steps 1 and 4
with open('payloads/payload_step_1.json') as f1, open('payloads/payload_step_4.json') as f2:
    payload_step_1 = json.load(f1)
    payload_step_4 = json.load(f2)


# finally, defining a function that'll come in handy throughout the script
# lots of data we get back from the apis comes in a format of lists of dicts
# these dicts have the same structure: {'attributeCode': x, 'value': y}
# converting these into one dictionary makes the data much more accessible
def convert_to_dict(list_of_dictionaries):
    '''
    Argument: A list of dictionaries as an argument, all of which contain the same pair of keys (in our case, it's 'attributeCode', 'value').

    Returns: a dictionary where the key is the 'attributeCode' value and its value is the 'value' value (eurgh).
    '''
    d = {}
    for dictionary in list_of_dictionaries:
        values = list(dictionary.values())
        d[values[0]] = values[1]
    return d


# ---------- Asking the user for their postcode ---------- #
postcode = input('Enter your postcode > ').lower().strip()

# cleaning the user's input - making sure there is a space in the correct place (as the alloy app query service requires)
if not ' ' in postcode:
    if len(postcode) == 5:
        postcode = f'{postcode[:2]} {postcode[-3:]}'
    elif len(postcode) == 6:
        postcode = f'{postcode[:3]} {postcode[-3:]}'
    elif len(postcode) == 7:
        postcode = f'{postcode[:4]} {postcode[-3:]}'
    else:
        print('Invalid postcode! Try again.')
        sys.exit()


# ---------- Step 1: Retrieving the itemId for the user's home address ---------- #

address_data = []

# setting the relevant bit of the payload equal to the user's postcode
payload_step_1['aqs']['children'][0]['children'][1]['properties']['value'][0] = postcode

for n in range(1, 4):
    r = session.post(
        url = aqs_query_endpoint,
        json = payload_step_1,
        params = {
            'page': n,
            'pageSize': 100,
            'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'
            }
    )

    results = r.json()['results']

    for result in results:

        # converting the attributes field of each address result to a dict
        # makes the data easier to work with
        result['attributes'] = convert_to_dict(result['attributes'])

        # converting the address field into something more presentable
        # "     20      BUTTERMERE WALK" --> "20 Buttermere Walk"
        result['attributes']['attributes_itemsTitle'] = re.sub(
            ' +',   # sub 1 or more whitespace
            ' ',    # for 1 whitespace
            result['attributes']['attributes_itemsTitle'].strip().title()
        )

        address_data.append(result)