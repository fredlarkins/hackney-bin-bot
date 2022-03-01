### Random stuff
- All residential properties should have a street number (123 WHATEVER STREET)
- Properties may have:
    - A suffix (123A WHATEVER STREET)
    - A flat number (Flat 4 123 WHATEVER STREET)
- The suffix has its own field in the attributes of the property, but the flat number does not
- Therefore, the user can be asked for their street number, but their flat number will have to be obtained by parsing the address


### Functions to write
- Something that flattens out a list of dictionaries with the same keys into one dict
    - Seemingly a lot of the requests return 'attribute' data where the keys are all the same