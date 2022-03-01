# Explainer: the requests workflow for Hackney Waste services

Hackney residents can check their bin collection dates on Hackney council's [waste collection checker tool](https://hackney-waste-pages.azurewebsites.net/).


This process can be boiled down to a series of requests to several endpoints at the following URL:

```
https://api.uk.alloyapp.io/api/
```

We can simulate these requests in Python, with a little help from the user.

**The workflow consists of five 'steps':**

## 1. Retrieving the `itemId` for the user's home address

These requests retrieve all the street addresses for the given postcode. The user is then asked to select their own address.

| Request component | Value | Notes |
| --- | --- | --- |
| Endpoint | `https://api.uk.alloyapp.io/api/aqs/query` | |
| Method | `POST` | |
| Params| `{'page': n, 'pageSize': 100, 'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'}` | `n` is an integer and each request has a different value for `n`. A request can return up to 100 addresses, so unlikely that n will ever have to exceed 3 (that's 3 requests / 300 addresses). |
| Payload | `payload_1.json` | The value for `payload['aqs']['children'][0]['children'][1]['properties']['value'][0]` is the **user's postcode**. |

### What do we want?
The `itemId` for the user's property; the user confirms what their address is via the command line.

This gives us the necessary data to proceed with the next request.

### Example response data
```json
{
  "page": 1,
  "pageSize": 100,
  "results": [
    {
      "itemId": "5f898d4790478c0067f863e5", # this is the piece of data we need for the next step
      "designCode": "designs_nlpgPremises",
      "collection": "Live",
      "start": "9999-12-31T23:59:59.999Z",
      "end": "9999-12-31T23:59:59.999Z",
      "icon": "icon-resource-house",
      "colour": "#4aa36b",
      "locked": false,
      "context": "Customer",
      "attributes": [
        {
          "attributeCode": "attributes_premisesPrimaryStartNumber",
          "value": 20
        },
        {
          "attributeCode": "attributes_itemsSubtitle",
          "value": "E8 3TA"
        },
        {
          "attributeCode": "attributes_itemsTitle",
          "value": "     20      BUTTERMERE WALK" # we will display this address in the terminal for the user to choose
        },
        {
          "attributeCode": "attributes_premisesPostcode",
          "value": "E8 3TA"
        },
        {
          "attributeCode": "attributes_premisesBlpuClass",
          "value": "RD06"
        }
      ],
      "signature": "61d5d55cccda3c01687b6b71"
    }
    # blah blah blah - returns the above fields for every address found for that postcode
}
```

## 2.  Using the `idemId` to check the waste collection services available for that property

This request established what (if any) waste collection services are available to the property.

| Request component | Value | Notes |
| --- | --- | --- |
| Endpoint | `https://api.uk.alloyapp.io/api/item/{itemId}` | `{itemId}` component of endpoint obtained in the previous step. |
| Method | `GET` |  |
| Params | `{'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'}` | |
| Payload | n/a | |
    
### What do we want?
The values returned for the `attributes_wasteContainersAssignableWasteContainers` field in the json response.

_Note:_ we can't yet identify which service (i.e. black bins, recycling) relates to each code. We'll establish this in the next step.

### Example response data
```json
{
  "itemId": "5f898d4790478c0067f863e7",
  "designCode": "designs_nlpgPremises",
  "collection": "Live",
  "start": "9999-12-31T23:59:59.999Z",
  "end": "9999-12-31T23:59:59.999Z",
  "icon": "icon-resource-house",
  "colour": "#4aa36b",
  "locked": false,
  "context": "Customer",
  "attributes": [
# blah blah blah
    {
      "attributeCode": "attributes_wasteContainersAssignableWasteContainers", 
      "value": [ # these are the values we need to extract
        "5fa55a536b4fb50065fffb14",
        "5fae9f9908c64000671b08d4",
        "5fb2742f6541e10069a60347",
        "5fb2d1545415eb0066346e95"
      ]
    },
# blah blah blah
  ],
  "signature": "61d5d0b8ccda3c01685f33d3"
}
```

## 3. Mapping each of the `attributes_wasteContainersAssignableWasteContainers` values to an actual service

At present, we do not know which of the alphanumeric codes obtained in the previous step correspond to a service - i.e. black bins, food waste & recycling, and garden waste.

This step maps those values to actual services.

| Request component | Value | Notes |
| --- | --- | --- |
| Endpoint | `https://api.uk.alloyapp.io/api/item/{wasteContainerId}` | `{wasteContainerId}` is each of the values obtained in the previous step. |
| Method | `GET` |  |
| Params | `{'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'}` | |
| Payload | n/a | |

## What do we want?
The values returned for the `attributes_wasteContainersAssignableWasteContainers` field in the json response.

### Example response data
```json
{
  "item": {
    "itemId": "5fa55a536b4fb50065fffb14",
    "designCode": "designs_wasteContainers",
    "collection": "Live",
    "start": "9999-12-31T23:59:59.999Z",
    "end": "9999-12-31T23:59:59.999Z",
    "icon": "icon-resource-waste-point",
    "colour": "#4aa36b",
    "locked": false,
    "context": "Customer",
    "attributes": [
  # blah blah blah (more json)
      {
        "attributeCode": "attributes_itemsSubtitle",
        "value": "Recycling Sack" # this is the 'human readable' equivalent of the alphanumeric value we got in the previous step
      }
    ],
    "signature": "5fa55add6b4fb50065045ff6"
  }
}
```

## 4. Retreiving the endpoints to get the schedules for each waste service
The schedules for each waste collection service will be retrieved in the next step - we can't do that without knowing the endpoints to query to get those schedules!

We'll do that in this step with a series of `POST` requests - one for each service.

| Request component | Value | Notes |
| --- | --- | --- |
| Endpoint | `https://api.uk.alloyapp.io/api/aqs/query` | |
| Method | `POST` |  |
| Params | `{'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'}` | |
| Payload | `payload_step_4.json` | The value for `payload['aqs']['children'][0]['children'][1]['properties']['value'][0]` is the id for the service / waste container. |

## What do we want?
The value returned for `attributes_scheduleCodeWorkflowID_5f8dbfdce27d98006789b4ec` - this is the endpoint that we'll be hitting for the actual schedule of waste pickup.

### Example response data
```json
{
  "page": 1,
  "pageSize": 20,
  "results": [
    {
      "itemId": "5fe49fc579bb4a0064b4dda1",
      "designCode": "designs_scheduleCode_5f8d5eac8dae040066c53c8c",
      "collection": "Live",
      "start": "9999-12-31T23:59:59.999Z",
      "end": "9999-12-31T23:59:59.999Z",
      "icon": "icon-display-list",
      "colour": "#8b8b8b",
      "locked": false,
      "context": "Customer",
      "attributes": [
        {
          "attributeCode": "attributes_scheduleCodeName_5f8d5f052802f700676fb147",
          "value": "Garden Monday Week 1"
        },
        {
          "attributeCode": "attributes_scheduleCodeCode_5f8d5f3f0e567e0066100ee7",
          "value": "GARD_MON_1"
        },
        {
          "attributeCode": "attributes_scheduleCodeWorkflowID_5f8dbfdce27d98006789b4ec",
          "value": "workflows_dWFortnightlyMonWeek1Garden_5fe49dd70d410400612800a2" # this is the endpoint for the final step
        }
      ],
      "signature": "618d4c366809f1015531d577"
    }
  ]
}
```

## 5. Retrieving the timetables for each waste service
Finally, we've got all the data we need to make `GET` requests to the timetable database. This will tell us when each bin (black bins, recyling etc.) is actually being collected!

| Request component | Value | Notes |
| --- | --- | --- |
| Endpoint | `https://api.uk.alloyapp.io/api/workflow/{workflowEndpoint}` | `{workflowEndpoint}` are the endpoints we got in the previous stage. |
| Method | `GET` |  |
| Params | `{'token': '67ad2108-dd2b-407a-849a-411a15adf0b1'}` | |
| Payload | n/a | |

## What do we want?
The timetable data contained in the response for each workflow.

### Example response data
```json
{
  "workflow": {
    "workflow": {
      "name": "Workflow_Round Mon",
      "enabled": true,
      "trigger": {
        "dates": [ # this is the precious bin timetable data!
          "2020-04-13T00:00:00.000Z",
          "2020-04-20T00:00:00.000Z",
          "2020-04-27T00:00:00.000Z"
          # etc
        ],
        "discriminator": "TimeCalendarTrigger"
      },
      # blah blah blah (more json)
    }
```
------
**And that's the workflow!**