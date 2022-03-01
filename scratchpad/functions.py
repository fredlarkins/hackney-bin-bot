import json
import pprint

json_str = '{"item":{"itemId":"5f898d4790478c0067f8cd1b","designCode":"designs_nlpgPremises","collection":"Live","start":"9999-12-31T23:59:59.999Z","end":"9999-12-31T23:59:59.999Z","icon":"icon-resource-house","colour":"#4aa36b","locked":false,"context":"Customer","attributes":[{"attributeCode":"attributes_premisesPrimaryStartNumber","value":1.0},{"attributeCode":"attributes_itemsSubtitle","value":"N16 0RA"},{"attributeCode":"attributes_itemsTitle","value":"     1      MARTON ROAD"},{"attributeCode":"attributes_premisesPostcode","value":"N16 0RA"},{"attributeCode":"attributes_premisesPostalTown","value":"LONDON"},{"attributeCode":"attributes_networkReferenceableNetworkReferences","value":["5f898dd190478c0067fd3bae"]},{"attributeCode":"attributes_nlpgPremisesUprn","value":"100021058116"},{"attributeCode":"attributes_premisesBlpuState","value":["5c4b3037e68ba84170c5dfaa"]},{"attributeCode":"attributes_premisesBlpuClass","value":"RD06"},{"attributeCode":"attributes_nlpgPremisesBlpuDate","value":"2009-08-04T00:00:00.000Z"},{"attributeCode":"attributes_nlpgPremisesLocalCustodianCode","value":5360.0},{"attributeCode":"attributes_itemsGeometry","value":{"type":"Point","coordinates":[-0.08002924400513536,51.56181410796217]}},{"attributeCode":"attributes_wasteContainersAssignableWasteContainers","value":["5fa55c586b4fb500650cbe08","5faea1a108c64000672a9767","5fb276436541e10069b5912c","5fb2d2765415eb0066418a4e"]},{"attributeCode":"attributes_nlpgPremisesServiceType_5f9beae0a198dd0064e02c1a","value":["5f9bea62a198dd0064e02bce"]},{"attributeCode":"attributes_tasksAssignableTasks","value":["5fd09c00adff540064268c15","6006e870d5c5ce00652a6e19","605086eea1c5ed000a02cc36","605086efa63399000ae6a91c","6058d30b0e0b5d000b4f89ae","6058d41dcb1513000a92fd77","6058d41e8b638a000a572ad7","6058d41ea2ecba000a1da2c7","60867053c8ceaa000a31fe66","6086705391595c000a063a97","60a774ab5bfa7a0231fd87e2","60a774ac9730b402306dc892","60b0f8f57f6b68022d33b46e","60e8535e1a393a02558d14e0","616aad0428398b01593c234b","616aad04197d68015d0e7f9d","616aad057233b70158eca3a5","6173f7f034dd550159026860","6173f7f023d4d9016617405f","617ef0ed5b4d150152440b5e"]},{"attributeCode":"attributes_nlpgPremisesPavement_5fdb837279bb4a0064ad5a96","value":["5fda5d17e6974000665caa36"]},{"attributeCode":"attributes_nlpgPremises2X80ltrs_5fda5c9526a9400064c6423a","value":false},{"attributeCode":"attributes_nlpgPremises1X190ltrs_5fda5cb80d410400611ef087","value":false},{"attributeCode":"attributes_nlpgPremisesSurveyStatus_5fda5c720d410400611ef077","value":["5fda571e0d410400611eef1c"]},{"attributeCode":"attributes_defectsAssignableDefects","value":["6058d309a52e69000af06b64"]}],"signature":"61d5d16accda3c016863b420"}}'

j = json.loads(json_str)

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