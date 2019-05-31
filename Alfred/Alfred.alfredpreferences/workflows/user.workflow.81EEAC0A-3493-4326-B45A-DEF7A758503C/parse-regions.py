import json
import itertools
from bs4 import BeautifulSoup

with open('./regional-product-services.html', 'r') as fh:
    html_doc = fh.read()

soup = BeautifulSoup(html_doc, 'html.parser')

aws_tables = soup.find_all("div", class_='lb-tbl')

services_list = {}

for table in aws_tables:
    found_regions = None
    for row in table.find_all('tr'):
        if not found_regions:
            # Examine the first td to see if it contains "Services Offered:"
            # If so, read the rest of the row to populate the services list
            try:
                if row.find_all('td')[0].get_text() == 'Services Offered:':
                    # Remaining cells are region names
                    found_regions = [cell.get_text().strip().replace('*', '') for cell in row.find_all('td')[1:]]
            except IndexError:
                pass
        else:
            # We know the regions for this table
            # Each remaining row will be the service name and then regions
            service_name = row.find_all('td')[0].get_text().strip()
            region_map = [1 if cell.get_text().strip() == "✓" else 0 for cell in row.find_all('td')[1:]]
            # print("|{}|".format(service_name))
            available_regions = list(itertools.compress(found_regions, region_map))
            if service_name in services_list.keys():
                services_list[service_name].extend(available_regions)
            else:
                services_list[service_name] = available_regions
# for service_name in services_list.keys():
#    print("{} is available in: {}".format(
#        service_name,
#        ", ".join(services_list[service_name])
#    ))
with open('regions.json', 'w') as fh:
    json.dump(services_list, fh)
