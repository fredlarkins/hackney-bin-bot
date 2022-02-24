#!/usr/bin/python3

import requests
import json
import sys

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
# house_number = input('Enter your house number >> ').lower().strip()

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

endpoint = 'https://api.uk.alloyapp.io/api/aqs/query'

# setting the payload's postcode value (the only thing that changes/matters) to our user input postcode
payload['aqs']['children'][0]['children'][1]['properties']['value'][0] = postcode

# creating a re-useable requests.Session object
session = requests.session()

# an empty list that we'll append the results of the inital api calls to
results = []

# we'll use n to change the page= parameter
for n in range(1, 4):

    # specifying the parameters for the endpoint url
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

print(results)