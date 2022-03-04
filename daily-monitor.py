'''
What will this script do?

daily-monitor.py will run every day, checking the bin_collection_data.json file to see whether the bin collection is due the following day.
If the collection is due the following morning, the script will send an email notifying which bins are due.
'''

import json
from datetime import datetime as dt
from pathlib import Path
import sys

# this script will only work if the user has first run through the check-bins.py flow and declared their address
if not Path('bin_collection_data.json').exists():
    print('No bin collection details present in the working directory -- have you run check-bins.py?')
    sys.exit()

# loading up our collection data
with open('bin_collection_data.json') as f:
    collection_data = json.load(f)

# saving today's date to a variable
today = dt.today().date()

# emoji equivalents of the bin collections for the email that'll be sent:
emojis = {
    'Recycling Sack': '♻️',
    'Food Caddy (Small)': '🍔',
    'Garden Waste Bin': '🌿',
    'Wheeled Bin (180ltr)': '🗑️'
}

# we need a function that works out whether it's the day before the collection date:
# if collections are happening tomorrow, this list will store what is being collected

collection_is_due_tomorrow = []

for service in collection_data.keys():
    
    # converting the timetable into list of datetime objects so it can be compared to today's date
    timetable = [dt.strptime(date, '%Y-%m-%d').date() for date in collection_data[service]['timetable']]

    # looping through the timetable, getting the difference between today's date and the date in that iteration of the loop
    for date in timetable:
        
        # if it's the day before collection is due, this value will equal 1
        if (date - today).days == 1:
            collection_is_due_tomorrow.append(collection_data[service]['name'])


if collection_is_due_tomorrow:
    print([emojis[bin] for bin in collection_is_due_tomorrow])

else:
    print('Nothing is due tomorrow.')




