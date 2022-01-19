#!/usr/bin/python
import argparse
import requests
import json

# Exports contract ABI in JSON



# parser = argparse.ArgumentParser()
# parser.add_argument('addr', type=str, help='Contract address')
# parser.add_argument('-o', '--output', type=str, help="Path to the output JSON file", required=True)

def __main__():

    # args = parser.parse_args()

    response = requests.get('https://api.bscscan.com/api?module=contract&action=getabi&address=0x660876c86655882f106727fcabf5faed5a932d32&apikey=BBFG2Q35F6FNNWCBG22D7K38T484MHKIDP')
    response_json = response.json()
    abi_json = json.loads(response_json['result'])
    result = json.dumps({"abi":abi_json}, indent=4, sort_keys=True)

    with open('unipairabi.json', 'w') as outfile:
        json.dump(abi_json, outfile)

if __name__ == '__main__':
    __main__()