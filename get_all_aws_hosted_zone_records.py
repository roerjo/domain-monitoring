import subprocess
import csv
import sys
import getopt
import json
import boto3

awsProfile = ''
accountName = ''

def parseArguments(argv):
    global awsProfile
    global accountName

    opts, args = getopt.getopt(argv,"hn:p:", ["help", "name=", "profile="])

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('get_all_aws_hosted_zone_records.py --profile default --name old_account')
            sys.exit()
        elif opt in ("-p", "--profile"):
            awsProfile = arg
        elif opt in ("-n", "--name"):
            accountName = arg
        
    if not awsProfile:
        print("Must pass an AWS profile name to use this script")
        sys.exit(1)
    if not accountName:
        print("Must pass a name for the AWS account to use this script")
        sys.exit(1)

    print(f'AWS profile set to "{awsProfile}"')
    print(f'Account name set to "{accountName}"')

parseArguments(sys.argv[1:])

hostedZonesFile = open(f"./files/aws/tmp/{accountName}_hosted_zones.json", 'w')


session = boto3.session.Session(profile_name=awsProfile)
route53 = session.client('route53')
route53_paginator = route53.get_paginator('list_hosted_zones')
response_iterator = route53_paginator.paginate(
    PaginationConfig={
        'MaxItems': 1000
    }
)

hostedZonesAccumulator = []

for page in response_iterator:
    hostedZonesAccumulator.extend(page['HostedZones'])

hostedZonesFile.write(json.dumps(hostedZonesAccumulator, indent=4))
hostedZonesFile.close()

hostedZonesFile = open(f"./files/aws/tmp/{accountName}_hosted_zones.json", 'r')
dnsRecordsFile = open(f"./files/aws/{accountName}_dns_records.csv", 'w', newline="")
dnsRecordsWriter = csv.writer(dnsRecordsFile, quoting=csv.QUOTE_ALL)

hostedZoneCount = 0

hostedZonesJson = json.load(hostedZonesFile)
for zone in hostedZonesJson:
    hostedZoneCount += 1
    hostedZoneId = zone.get('Id')[12:].strip()
    hostedZoneName = zone.get('Name')
    print(f"Processing {hostedZoneId}")
    currentZoneFile = open("./files/aws/tmp/current_zone_records.json", 'wb')
    awsCall = subprocess.Popen(['aws', '--profile', awsProfile, '--output', 'json', 'route53', 'list-resource-record-sets', '--hosted-zone-id', hostedZoneId], stdout=subprocess.PIPE)
    filterCall = subprocess.Popen(['jq', '-r', '."ResourceRecordSets"'], stdin=awsCall.stdout, stdout=currentZoneFile)
    filterCall.communicate()
    currentZoneFile.close()
    
    currentZoneFile = open("./files/aws/tmp/current_zone_records.json", 'r')
    currentZoneJson = json.load(currentZoneFile)
    for record in currentZoneJson:
        recordName = record.get('Name', "N/A")
        recordType = record.get('Type', "N/A")
        recordTTL = record.get('TTL', "N/A")
        recordValues = record.get('ResourceRecords',"N/A")
        recordAlias = record.get('AliasTarget', "N/A")
        dnsRecordsWriter.writerow([accountName, hostedZoneName, hostedZoneId, recordName, recordType, recordTTL, recordValues, recordAlias])
    currentZoneFile.close()

print(f"{accountName} has {hostedZoneCount} hosted zones")

hostedZonesFile.close()
dnsRecordsFile.close()
