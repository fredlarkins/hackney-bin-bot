#!/usr/bin/python3

from distutils.command.clean import clean
import requests
import json
import sys
from colorama import init, Fore
init(autoreset=True)
from string import ascii_lowercase
import re

'''
--- REQUESTS 1-3 ---
Method: POST
Endpoint: https://api.uk.alloyapp.io/api/aqs/query
Params: {
    page: n, # i.e. 1-3
    pageSize: 100,
    token: 67ad2108-dd2b-407a-849a-411a15adf0b1
}
Payload: payload_1.json... changing the value of json['aqs']['children'][0]['children'][1]['properties']['value'][0] to the postcode in question
Response: response_1.json... each property has an item id (used to make the next request for bin details), plus attribute values like premises number, long name etc
'''

# running through the first set of requests to get the details for each property

postcode = input('Enter your postcode >> ').lower().strip()
# postcode = 'n16 0ra'
house_number = int(input('Enter your house number >> ').lower().strip())
# house_number = 1

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


# ----------------- Making the first three requests to get our property details -----------------#

# opening and reading our sample payload from the json file
with open('payload_1.json') as f:
    payload = json.load(f)


# the endpoint for the first set of API calls
endpoint = 'https://api.uk.alloyapp.io/api/aqs/query'


# setting the payload's postcode value (the only thing that changes/matters) to our user input postcode
payload['aqs']['children'][0]['children'][1]['properties']['value'][0] = postcode


# creating a re-useable requests.Session object
session = requests.session()


# an empty list that we'll append the results of the inital api calls to
results = []


# we'll use n to change the page= parameter
for n in range(1, 4):

    # specifying the parameters for the endpoint
    params = {
        'page': n,
        'pageSize': 100,
        'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'
    }

    # making the request
    r = session.post(
        url=endpoint,
        params=params,
        json=payload
    )

    # getting the json data from the request object
    data = r.json()

    # appending the results of the api call to the empty list
    results.extend(data['results'])

'''
All residential properties *should* have a house number - i.e. an `attributes_premisesPrimaryStartNumber`.
We can use this number to try and help the program intelligently select a property based on the house number speficied by the user.
'''
# empty list where we will store the address candidates
candidates = []
cleaned_results = []

# looping through the results of the API call
for result in results:
    d = {}  # we'll need this to flatten out the 'attributes' section of the api call result

    # looping through the attributes for each property
    for attribute in result['attributes']:
        values_list = list(attribute.values())
        d[values_list[0]] = values_list[1]
        result['attributes'] = d  # the 'attributes' section is now the flattened list --> dict
        
        cleaned_results.append(result)  # keeping a separate list of all the cleaned addresses in case we have to ask the user to select from the full list

        # if the premises start number equals the number specified by the user, then append to the candidates list
        if attribute['attributeCode'] == 'attributes_premisesPrimaryStartNumber':
            if int(attribute['value']) == house_number:
                candidates.append(result)


'''
Now, we'll ask the user to verify which is their address using a selectable list with letters of the alphabet as options
'''
# defining a function that we can use both in the case that there are no candidates, and if the user selects 'none of the above'
def user_has_not_found_address(cleaned_results=cleaned_results):
    
    print('''
    Type the letter next to your address, i.e. "a", "b" and hit ENTER:
    ''')

    cleaned_results_dict = {}

    for num, r in zip(list(range(1, len(cleaned_results) + 1)), cleaned_results):
        cleaned_results_dict[num] = r
        address = re.sub('[ ]{2,}',' ', r['attributes']['attributes_itemsTitle'].strip().title())
        print(f'{Fore.RED}({num}){Fore.RESET} {address}')
    user_selection = int(input('\n> ').strip())

    return user_selection

if not len(candidates) == 0:  # i.e. there is at least one candidate
    # using the ascii_lowercase string imported from the string module
    letters_of_alphabet = list(ascii_lowercase)


    # we need to create a dict with the letter of the alphabet as keys (that correspond to a user selection)...
    # ...and the candidate as a value
        
    candidates_dict = {}  # an empty dict that'll be populated via a for loop

    # asking the user to specify their choice
    print('''
    Type the letter next to your address, i.e. "a", "b" and hit ENTER:
    ''')


    # looping through the candidates list
    for l, c in zip(letters_of_alphabet, candidates):
        candidates_dict[l] = c  # we've now got a dict that can be used later

        # subbing out the white space in the address and making the text into title case
        address = re.sub('[ ]{2,}',' ', c['attributes']['attributes_itemsTitle'].strip().title())
        
        # printing the choice to the console
        print(f'{Fore.RED}({l}){Fore.RESET} {address}')


    # giving the user the option that their address is not found in the list above
    none_of_the_above = letters_of_alphabet[letters_of_alphabet.index(list(candidates_dict.keys())[-1]) + 1]  # getting the next letter
    print(f'{Fore.BLUE}({none_of_the_above}){Fore.RESET} None of the above')  # user can select none of the above

    # capturing user selection
    user_selection = input('\n> ').lower().strip()

    if user_selection == none_of_the_above:  # user has not found their address in the list of candidates
        user_selection = user_has_not_found_address()

else:
    user_selection = user_has_not_found_address()