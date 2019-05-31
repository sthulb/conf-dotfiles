# vim: set fileencoding=utf-8
"""
Helper things for AWS Alfred
"""

_region_map = {
    'us-east-1': ['Northern Virginia', 'IAD'],
    'us-east-2': ['Ohio', 'CMH'],
    'us-west-1': ['Oregon', 'SFO'],
    'us-west-2': ['Northern California', 'PDX'],
    'eu-west-1': ['Ireland', 'DUB'],
    'eu-west-2': ['London', 'LHR'],
    'eu-central-1': ['Frankfurt', 'FRA'],
    'ca-central-1': ['Montreal', 'YUL'],
    'ap-south-1': ['Mumbai', 'BOM'],
    'ap-northeast-3': ['Osaka', 'KIX'],
    'ap-northeast-2': ['Seoul', 'ICN'],
    'ap-northeast-1': ['Tokyo', 'NRT'],
    'ap-southeast-1': ['Singapore', 'SIN'],
    'ap-southeast-2': ['Sydney', 'SYD'],
    'eu-west-3': ['Paris', 'CDG'],
    'eu-north-1': ['Stockholm', 'ARN'],
    'sa-east-1': ['São Paulo', 'GRU']
}

_region_unmap = {}

for region in _region_map:
    _region_unmap[_region_map[region][0]] = region


def region_shortname_to_name(shortname):
    try:
        return _region_map[shortname][0]
    except KeyError:
        return None


def shortname_to_airport(shortname):
    try:
        return _region_map[shortname][1]
    except KeyError:
        return None
    except IndexError:
        return None


def region_name_to_shortname(name):
    try:
        return _region_unmap[name]
    except KeyError:
        return None
