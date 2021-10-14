# Usage
## Retrieve records from AWS and Cloudflare first:

### Cloudflare:

`python get_all_cloudflare_zone_records.py --zone <zone id> --name <zone name> --key <api key>`

### AWS:

`python get_all_aws_hosted_zone_records.py --name <name of account> --profile <profile config>`

### Example:

```sh
python get_all_cloudflare_zone_records.py --zone zyxw9876 --name sofwarepundit.com --key 123abc
python get_all_aws_hosted_zone_records.py --name aws_new_account --profile default  
python get_all_aws_hosted_zone_records.py --name aws_old_account --profile ta-old
```

## Combine the results of retrieving records:

`python combine_all_records.py <path to csv1> <path to csv2> <etc>`

### Example:

```sh
python combine_all_records.py ./files/aws/aws_new_account_dns_records.csv ./files/aws/aws_old_account_dns_records.csv ./files/cloudflare/softwarepundit.com_dns_records.csv
```

## Run StatusCake uptime test check on results of combining records:

`python get_statuscake_uptime_status.py`

## Run StatusCake TLS certificate check on results of combining records:

`python get_statuscake_cert_status.py`

## Update Google Sheets with results
