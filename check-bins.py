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
from string import ascii_lowercase
import colorama
from colorama import Fore
colorama.init(autoreset=True)


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
postcode = input('\nEnter your postcode > ').lower().strip()

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

# if the API call returns no addresses...
if len(address_data) == 0:
    print(f'\nNo addresses in Hackney found for {postcode.upper()} - try again!')
    sys.exit()

'''
We want to display a list of selectable options to the user like this:

    (a) 123 Baker Street
    (b) 124 Baker Street

Therefore, we'll use a list of letter that the user can type into the terminal.

We will have to deal with the situation where the list of addresses exceeds 26.
'''

# letter of the alphabet
letters = list(ascii_lowercase)

# our first conditional: list of addresses is < letters of alphabet
if len(address_data) < len(letters):
    print('\nSelect your address from the list below:')
    
    selection_options = dict(zip(letters, address_data))

    for letter, option in selection_options.items():
        
        # formatting the output in fancy letters
        print(f'{Fore.RED}({letter}){Fore.RESET} {option["attributes"]["attributes_itemsTitle"]}')
    
    user_selection = input(f'\nType the letter - {Fore.RED}a{Fore.RESET}, {Fore.RED}b{Fore.RESET}, etc - next to your address and hit ENTER > ')
    address = selection_options[user_selection]





# # writing the user's address details to a json file
# with open('address_details.json', 'w') as f:
#     json.dump(address, f)

# # confirmation message to use
# print(f'\nThank you! Checking bin collection dates for {Fore.GREEN}{address["attributes"]["attributes_itemsTitle"]}...')