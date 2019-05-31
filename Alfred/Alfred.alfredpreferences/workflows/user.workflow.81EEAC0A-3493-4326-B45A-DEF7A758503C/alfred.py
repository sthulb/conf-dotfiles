#!/usr/bin/env PATH=$PATH:/usr/local/bin python3
# vim: set fileencoding=utf-8

import csv
import json
import util


class AlfredHelper():

    def __init__(self):
        self._services = {}
        self._services_alfred = {}
        self._regions = {}
        self._regions_alfred = {}
        self.load_regions()
        self.load_csv()
        self.process_services()
        self.process_region_availability()

    def load_regions(self):
        """Load service/region info from JSON."""
        with open('regions.json', 'r') as file_handle:
            self._regions = json.load(file_handle)

    def load_csv(self, filename='services.csv'):
        """Load PR-friendly service names from CSV."""
        services = {}
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                service = row[0]
                first_use = row[1]
                second_use = None
                icon = None
                try:
                    second_use = row[2]
                    if second_use == '':
                        second_use = None
                except IndexError:
                    pass
                services[service] = {
                    'first': first_use,
                    'second': second_use,
                    'icon': icon
                }
            self._services = services

    def process_services(self):
        """Prepare PR-friendly service names"""
        output = []
        for service in self._services:
            """
            {
        "uid": "desktop",
        "type": "file",
        "title": "Desktop",
        "subtitle": "~/Desktop",
        "arg": "~/Desktop",
        "autocomplete": "Desktop",
        "icon": {
            "type": "fileicon",
            "path": "~/Desktop"
        }
    }"""
            service_info = self._services[service]
            if service_info['second'] is None:
                output.append(
                    {
                        'uid': service,
                        'title': service,
                        'subtitle': service_info['first'],
                        'arg': service_info['first'],
                    }
                )
            else:
                output.append(
                    {
                        'uid': '{}-first'.format(service),
                        'title': '{} (first use)'.format(service),
                        'subtitle': service_info['first'],
                        'arg': service_info['first'],
                        'autocomplete': service
                    }
                )
                output.append(
                    {
                        'uid': '{}-second'.format(service),
                        'title': '{} (subsequent use)'.format(service),
                        'subtitle': service_info['second'],
                        'arg': service_info['second'],
                        'autocomplete': service
                    }
                )
        self._services_alfred = output


    def list_service_names(self):
        output = []
        for service in self._services:
            output.append(
                {
                    'uid': service,
                    'title': service,
                    'arg': service
                }
            )
        return output


    def process_region_availability(self):
        """Prepare per-region availablity map.

        TODO: include non-availability as "is not"
        """
        output = []
        for service in self._regions.keys():
            region_info = self._regions[service]
            for region in region_info:
                if region == 'London':
                    tag = u' 🎉'
                else:
                    tag = ''
                output.append({
                    'uid': service,
                    'title': region,
                    'subtitle': u'{} is available in {}{}'.format(service, util.region_name_to_shortname(region), tag),
                    'autocomplete': service,
                    'match': u'{} {} {} {}'.format(
                        service.replace('(', '').replace(')', ''),
                        region,
                        util.region_name_to_shortname(region),
                        util.shortname_to_airport(util.region_name_to_shortname(region))
                    )
                })
        self._regions_alfred = output

    def output_regions(self):
        print(json.dumps(AlfredHelper._alfred_items(self._regions_alfred)))

    def output_service_names(self):
        print(json.dumps(AlfredHelper._alfred_items(self._services_alfred)))

    def output_service_names_only(self):
        print(json.dumps(AlfredHelper._alfred_items(self.list_service_names())))

    @staticmethod
    def _alfred_items(*args):
        items = []
        for arg in args:
            items.extend(arg)
        return {'items': items}


if __name__ == '__main__':
    alfred = AlfredHelper()
    alfred.load_csv()
    alfred.output_services()
