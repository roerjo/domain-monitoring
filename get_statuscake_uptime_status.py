import csv
import requests
import urllib

# Open files
csv_file = open('./files/main_domains_file.csv')
existing_status_cake_file = open('./files/statuscake/uptime/uptime_export.csv')
all_results_file = open('./files/statuscake_uptime_results.csv', 'w', newline="")
good_results_file = open('./files/statuscake/uptime/good_results.csv', 'w', newline="")
bad_results_file = open('./files/statuscake/uptime/bad_results.csv', 'w', newline="")
already_existed_file = open('./files/statuscake/uptime/already_existed.csv', 'w', newline="")
create_tests_file = open('./files/statuscake/uptime/create_test.csv', 'w', newline="")

# Get CSV readers and writers
csv_reader = csv.reader(csv_file, delimiter=',')
csv_reader_status_cake = csv.reader(existing_status_cake_file, delimiter=',')
csv_writer_all = csv.writer(all_results_file, quoting=csv.QUOTE_ALL)
csv_writer_good = csv.writer(good_results_file, quoting=csv.QUOTE_ALL)
csv_writer_bad = csv.writer(bad_results_file, quoting=csv.QUOTE_ALL)
csv_writer_existed = csv.writer(already_existed_file, quoting=csv.QUOTE_ALL)
csv_writer_create = csv.writer(create_tests_file, quoting=csv.QUOTE_ALL)

# Initialize empty list of sites that existed in StatusCake
existing_list = []

export_line_count = 0

# Fill list of hostnames that existed in StatusCake
for row in csv_reader_status_cake:
    if export_line_count == 0:
        export_line_count += 1
        continue
    else:
        existing_website = row[4]
        parsed_obj = urllib.parse.urlparse(existing_website)
        parsed_result = parsed_obj.netloc + parsed_obj.path

        if parsed_result:
            existing_list.append(parsed_result.rstrip('/'))
        else:
            existing_list.append(row[4])

print(existing_list)

line_count = 0

# Parse the input CSV
for row in csv_reader:
    site = row[0].rstrip(".")

    print(f'Making requst to {site}')

    # Check if site already exists in StatusCake
    if (site in existing_list):
        csv_writer_existed.writerow([site])
        csv_writer_all.writerow([site, "already exists in StatusCake", site])
        continue        

    # Make request to site to see if we get a 2xx response
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        }
        result = requests.get('http://' + site, timeout=10, headers=headers, verify=False, allow_redirects=True)

        if (result.status_code < 300):
            parsed_obj = urllib.parse.urlparse(result.url)
            parsed_result = parsed_obj.netloc + parsed_obj.path
            parsed_result = parsed_result.rstrip('/')

            if ("dnserrorassist" in result.text):
                csv_writer_bad.writerow([site, str(result.status_code) + " response"])
                csv_writer_all.writerow([site, "do not put in StatusCake", "redirecting to search engine", result.status_code])
            elif (parsed_result not in existing_list):
                csv_writer_good.writerow([site, result.url, result.status_code, result.reason])
                csv_writer_all.writerow([site, "add to StatusCake", result.url, result.status_code])
            else:
                csv_writer_all.writerow([site, "already exists in StatusCake", parsed_result, result.status_code])
        else:
            csv_writer_bad.writerow([site, str(result.status_code) + " response"])
            csv_writer_all.writerow([site, "do not put in StatusCake", result.url, result.status_code])
    except Exception as e:
        print(e)
        csv_writer_bad.writerow([site, str(e)])
        csv_writer_all.writerow([site, "do not put in StatusCake", "error", "error", str(e)])
    line_count += 1

print(f'Total of {line_count} sites')

good_results_file.close()
good_results_file = open('./files/statuscake/uptime/good_results.csv')

csv_reader_good_results = csv.reader(good_results_file, delimiter=',')

unique_list = []

# Discover which sites we need to add tests for
for row in csv_reader_good_results:
    good_website = row[1]
    parsed_obj = urllib.parse.urlparse(good_website)
    parsed_result = parsed_obj.netloc + parsed_obj.path
    parsed_result = parsed_result.rstrip('/')

    if ((parsed_result not in unique_list) and (parsed_result not in existing_list)):
        unique_list.append(parsed_result)
        csv_writer_create.writerow([parsed_result, good_website])

# Tidy up
csv_file.close()
existing_status_cake_file.close()
all_results_file.close()
good_results_file.close()
bad_results_file.close()
already_existed_file.close()
create_tests_file.close()
