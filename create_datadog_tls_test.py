import csv
import sys
import getopt
import requests

def parseArguments(argv):
    global ddApiKey
    global ddAppKey

    opts, args = getopt.getopt(argv,"hk:a:", ["help", "api-key=", "app-key="])

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('create_datadog_tls_test.py --api-key <api_key> --app-key <app_key>')
            sys.exit()
        elif opt in ("-k", "--api-key"):
            ddApiKey = arg
        elif opt in ("-a", "--app-key"):
            ddAppKey = arg
        
    if not ddApiKey:
        print("Must pass a DataDog API key to use this script")
        sys.exit(1)
    if not ddAppKey:
        print("Must pass a DataDog APP key to use this script")
        sys.exit(1)

    print(f'DataDog API key set to "{ddApiKey}"')
    print(f'DataDog APP key set to "{ddAppKey}"')

parseArguments(sys.argv[1:])

create_tests_file = open('./files/datadog/tls_cert/create_test.csv',)

csv_reader_create = csv.reader(create_tests_file, delimiter=',')

for row in csv_reader_create:
    print(f'Making test for {row[0]}')

    # Make request to site to see if we get a 2xx response
    try:
        headers = {
            'content-type': 'application/json',
            'DD-API-KEY': ddApiKey,
            'DD-APPLICATION-KEY': ddAppKey
        }
        json = {
            "status": "live",
            "tags": [
                "origin:" + row[2]
            ],
            "locations": [
                "azure:eastus",
                "aws:us-west-1"
            ],
            "message": "@slack-critical_ops_alerts \n\n{{#is_alert}} " + row[0] + " failed SSL test! {{/is_alert}}\n{{#is_alert_recovery}} " + row[0] + " is now passing SSL test. {{/is_alert_recovery}} ",
            "name": "TLS test for " + row[0],
            "type": "api",
            "subtype": "ssl",
            "config": {
                "request": {
                    "host": row[0],
                    "port": 443
                },
                "assertions": [
                    {
                        "operator": "isInMoreThan",
                        "type": "certificate",
                        "target": 29
                    },
                    {
                        "operator": "moreThanOrEqual",
                        "type": "tlsVersion",
                        "target": "1.2"
                    },
                    {
                        "operator": "lessThan",
                        "type": "responseTime",
                        "target": 3000
                    }
                ]
            },
            "options": {
                "accept_self_signed": False,
                "min_location_failed": 1,
                "monitor_options": {
                    "renotify_interval": 1440
                },
                "tick_every": 86400,
                "monitor_priority": 2,
                "monitor_name": "SSL Test",
                "min_failure_duration": 0
            }
        }
        result = requests.post(
            'https://api.datadoghq.com/api/v1/synthetics/tests/api', 
            headers=headers,
            json=json
        )
    except Exception as e:
        print(e)

create_tests_file.close()
