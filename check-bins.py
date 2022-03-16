'''
What will this script do?

tl;dr:
- The script will ask the user to find their address;
- Check the waste collection services available for that address;
- Check the collection days for those services;
- Write that data to a file
- It'll also ask you to register your gmail credentials with yagmail for the sending of emails

See explainer.md for a detailed explanation of what's going on. 
'''

from pathlib import Path
from dotenv import set_key
import colorama
import requests
from colorama import Fore

colorama.init(autoreset=True)
import json
import sys

from utils import ask_user_for_postcode, convert_to_dict

# creating a re-useable session object that we'll use throughout the script
session = requests.session()

# saving the three different endpoints used throughout this workflow as separate variables
aqs_query_endpoint = 'https://api.uk.alloyapp.io/api/aqs/query'
item_endpoint = 'https://api.uk.alloyapp.io/api/item'
workflow_endpoint = 'https://api.uk.alloyapp.io/api/workflow'

# ---------- Step 1: Retrieving the itemId for the user's home address ---------- #
# see the 'utils.py' file for more info on the functions below

if not Path('address_details.json').exists():
    address = ask_user_for_postcode()

else:
    with open('address_details.json') as d:
        address = json.load(d)

# ---------- Step 2: Using the idemId to check the waste collection services available for that property ---------- #
# confirmation message to use
print(f'\nChecking bin collection dates for {Fore.GREEN}{address["attributes"]["attributes_itemsTitle"]}{Fore.RESET}...')

# the alphanumeric identifier for thce address
itemId = address['itemId']

r = session.get(
    url = f'{item_endpoint}/{itemId}',
    params = {
        'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'
    },
)

available_service_data = r.json()

# flattening out the list of dicts that are returned in the attributes field again
available_service_data['item']['attributes'] = convert_to_dict(available_service_data['item']['attributes'])

# properties without waste collection (i.e. flats with communal bins) won't have 'attributes_wasteContainersAssignableWasteContainers' in the dict keys
if not 'attributes_wasteContainersAssignableWasteContainers' in available_service_data['item']['attributes'].keys():
    print(f'\nNo waste collection days found for {Fore.GREEN}{address["attributes"]["attributes_itemsTitle"]}{Fore.RESET}. As per the council\'s website: "If you live in an estate or block of flats over 8 properties it is likely you have a communal bin / receive a communal collection."')
    sys.exit()


# retrieving the alphanumeric codes for the available waste services for the given address
# storing them as keys in a dict (we'll append to the dict in the next section)

available_services = {}
for service in available_service_data['item']['attributes']['attributes_wasteContainersAssignableWasteContainers']:
    available_services[service] = {}



# ---------- Steps 3, 4, 5 ---------- #
# 3: Mapping each of the attributes_wasteContainersAssignableWasteContainers values to an actual service...
# 4: Retreiving the endpoints to get the schedules for each waste service
# 5: Retrieving the timetables for each waste service
with open('payloads/payload_step_4.json') as f:
    payload = json.load(f)


for service in available_services.keys():

    # 3:
    r = session.get(
        url = f'{item_endpoint}/{service}',
        params = {
            'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'
        }
    )

    data = r.json()

    # retrieving the 'human-readable' description for the waste service
    available_services[service]['name'] = convert_to_dict(data['item']['attributes'])['attributes_itemsSubtitle']

    # 4:
    payload['aqs']['children'][0]['children'][1]['properties']['value'][0] = service
    p = session.post(
        url = aqs_query_endpoint,
        params = {
            'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'
        },
        json = payload
    )

    workflow_data = p.json()['results'][0]
    
    # getting the workflow endpoint from the data
    available_services[service]['workflowEndpoint'] = convert_to_dict(workflow_data['attributes'])['attributes_scheduleCodeWorkflowID_5f8dbfdce27d98006789b4ec']

    # 5:
    q = session.get(
        url = f'{workflow_endpoint}/{available_services[service]["workflowEndpoint"]}',
        params = {
            'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'
        },
    )

    timetable_data = q.json()['workflow']['workflow']['trigger']['dates']
    
    # there is a useless time-of-the-day value on every date that we don't need (bins are collected in the morning)
    available_services[service]['timetable'] = [date.split('T')[0] for date in timetable_data]


'''
Finally, we have the data for the services available.
'''

with open('bin_collection_data.json', 'w') as f:
    json.dump(available_services, f)

print('\nDone.')


# asking the user to provide their email credentials and email recipients, which will be saved in a dotenv file
if not Path('.env').exists():
    gmail_info = {}
    
    gmail_info['USERNAME'] = input('\nWhat is your dummy Gmail username? > ').strip()
    
    # also writing this to a .yagmail file in the home directory of the user's machine
    with open(f'{Path.home()}/.yagmail', 'w') as y:
        y.write(gmail_info['USERNAME'])
    
    gmail_info['PASSWORD'] = input('\nWhat is the password for that account? > ').strip()

    gmail_info['RECIPIENTS'] = input('\nPlease enter email recipients for bin notifications (comma separated if more than one) > ').replace(' ', '').strip()

    # writing these values to a .env file
    with open('.env', 'w') as e:
        for k, v in gmail_info.items():
            set_key(
                dotenv_path='.env',
                key_to_set=k,
                value_to_set=v
            )
    
    print('\nThanks for the info!')

# finally, generating a .sh file that the user can package up and use in a cron job
if not Path('binbot.sh').exists():
    with open('binbot.sh', 'w') as s:
        s.writelines(
            [
                f'{line}\n' for line in [
                    '#!/bin/bash',
                    f'cd {str(Path().resolve())}',
                    '. venv/bin/activate',
                    'python3 check-bins.py',
                    'python3 daily-monitor.py',
                    'sleep 5',
                    'deactivate',
                    'exit'
                ]
            ]
        )