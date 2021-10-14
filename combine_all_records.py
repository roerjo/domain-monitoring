import csv
import sys

##########
# Usage: python combine_all_records.py <path to csv1> <path to filecsv2> <etc>
##########

# Parse arguments
fileArray = []

for file in sys.argv[1:]:
    fileArray.append(file)

# Setup files
combinedRecordsFile = open("./files/combined_dns_records.csv", 'w')
topDomainsFile = open("./files/main_domains_file.csv", 'w')
allDomainsFile = open("./files/all_domains_file.csv", 'w')

combinedRecordsWriter = csv.writer(combinedRecordsFile, quoting=csv.QUOTE_ALL)
topDomainsWriter = csv.writer(topDomainsFile, quoting=csv.QUOTE_ALL)
allDomainsWriter = csv.writer(allDomainsFile, quoting=csv.QUOTE_ALL)

# Initialize domain lists
mainDomainsList = []
allDomainsList = []

# Loop through the passed in files
for file in fileArray:
    print(f"Opening file {file}")
    currentFile = open(file)
    currentFileReader = csv.reader(currentFile, delimiter=",")

    # Loop through each row in the CSV
    for row in currentFileReader:
        # Every row should be added to the combined_dns_records.csv
        combinedRecordsWriter.writerow(row)

        # AWS likes to add "." to the end of the domains...strip it
        hostSite = row[1].rstrip(".")
        dnsSite = row[3].rstrip(".")

        # The main domain, host zone name, should be added to both domain lists
        if (hostSite not in mainDomainsList) and (hostSite not in allDomainsList):
            mainDomainsList.append(hostSite)
            allDomainsList.append(hostSite)
        
        # Add all A and CNAME record domains (subdomains) to the all_domains.csv
        if (row[4] == 'A' or row[4] == 'CNAME') and (dnsSite not in allDomainsList):
            allDomainsList.append(dnsSite)

    currentFile.close()

# Write main domain list to CSV file
for domain in mainDomainsList:
    topDomainsWriter.writerow([domain])
    
# Wirte main and subdomain list to CSV file
for domain in allDomainsList:
    allDomainsWriter.writerow([domain])

# Close files
combinedRecordsFile.close()
allDomainsFile.close()
topDomainsFile.close()
