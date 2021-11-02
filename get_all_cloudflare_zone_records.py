import csv
import sys
import getopt
import requests

cloudflareApiKey = ''
cloudflareZoneId = ''

def parseArguments(argv):
    global cloudflareApiKey
    global cloudflareZoneId
    global cloudflareZoneName

    opts, args = getopt.getopt(argv,"hk:z:n:", ["help", "key=", "zone=", "name="])

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('get_all_cloudflare_zone_records.py --name <zone_name> --key <api_key> --zone <zone_id>')
            sys.exit()
        elif opt in ("-k", "--key"):
            cloudflareApiKey = arg
        elif opt in ("-z", "--zone"):
            cloudflareZoneId = arg
        elif opt in ("-n", "--name"):
            cloudflareZoneName = arg
        
    if not cloudflareApiKey:
        print("Must pass a Cloudflare API key to use this script")
        sys.exit(1)
    if not cloudflareZoneId:
        print("Must pass a Cloudflare Zone ID to use this script")
        sys.exit(1)
    if not cloudflareZoneName:
        print("Must pass a Cloudflare Zone Name to use this script")
        sys.exit(1)

    print(f'Cloudflare API key set to "{cloudflareApiKey}"')
    print(f'Cloudflare Zone ID set to "{cloudflareZoneId}"')
    print(f'Cloudflare Zone Name set to "{cloudflareZoneName}"')

parseArguments(sys.argv[1:])

dnsRecordsFile = open(f"./files/cloudflare/{cloudflareZoneName}_dns_records.csv", 'w', newline="")
dnsRecordsWriter = csv.writer(dnsRecordsFile, quoting=csv.QUOTE_ALL)

headers = {
    'Authorization': "Bearer " + cloudflareApiKey,
    'Content-Type': 'application/json'
}
result = requests.get(f"https://api.cloudflare.com/client/v4/zones/{cloudflareZoneId}/dns_records?per_page=100", headers=headers)

resultJson = result.json().get('result')

for record in resultJson:
    hostedZoneId = cloudflareZoneId
    hostedZoneName = cloudflareZoneName

    recordName = record.get('name', "N/A")
    recordType = record.get('type', "N/A")
    recordTTL = record.get('ttl', "N/A")
    recordValues = record.get('content',"N/A")
    recordAlias = "N/A"
    dnsRecordsWriter.writerow(["cloudflare", hostedZoneName, hostedZoneId, recordName, recordType, recordTTL, recordValues, recordAlias])

dnsRecordsFile.close()
