"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "example.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

changes = { 'ing George Hwy.': 'King George Boulevard',
           'W15th st': 'W 15th Street',
           'Howe St. Vancouver': 'Howe Street',
           'W. Hastings St. Vancouver': 'West Hastings Street',
           'Expo Blvd, #3305': 'Expo Boulevard',
           ' Beatty St': 'Beatty Street'}

mapping = {'Alley': 'Alley',
           'Ave': 'Avenue',
           'Ave.': 'Avenue',
           'Blvd': 'Boulevard',
           'Broadway': 'Broadway',
           'Bypass': 'Bypass',
           'Centre': 'Centre',
           'Close': 'Close',
           'Crescent': 'Crescent',
           'Diversion': 'Diversion',
           'Dr': 'Drive',
           'Dr.': 'Drive',
           'East': 'East',
           'Edmonds': 'Edmonds Street',
           'Gate': 'Gate',
           'Grove': 'Grove',
           'Hastings': 'Hastings Street',
           'Highway': 'Highway',
           'Hwy': 'Highway',
           'HWY.': 'Highway',
           'Kingsway': 'Kingsway',
           'Mall': 'Mall',
           'Mews': 'Mews',
           'Moncton': 'Moncton Street',
           'North': 'North',
           'Park': 'Park',
           'Pender': 'Pender Street',
           'RD': 'Road',
           'Rd': 'Road',
           'Rd.': 'Road',
           'Rt.': 'Route',
           'Rt': 'Route',
           'Road,': 'Road',
           'S.': 'South',
           'Sanders': 'Sanders Street',
           'South': 'South',
           'St': 'Street',
           'St.': 'Street',
           'Street3': 'Street',
           'Terminal': 'Terminal',
           'Tsawwassen': 'North Tsawwassen',
           'Vancouver': 'Vancouver',
           'Walk': 'Walk',
           'Way': 'Way',
           'West': 'West',
           'Willingdon': 'Willingdon',
           'Wynd': 'Wynd',
           'av': 'Avenue',
           'road': 'Road',
           'st': 'Street',
           'street': 'Street',
           'Road':'Road',
           'Street': 'Street',
           'Avenue': 'Avenue',
           'Drive': 'Drive',
           'Boulevard':'Boulevard',
           'Parkway': 'Parkway',
           'Pky': 'Parkway',
           'Pkwy': 'Parkway',
           'Place': 'Place',
           'Court': 'Court',
           'Trail': 'Trail',
           'Lane': 'Lane'
           }


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "W.": "West",
            "N.": "North",
            "S.": "South",
            "E": "East"}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


def update_name(name, mapping):

    after = []
    # Split name string to test each part of the name;
    # Replacements may come anywhere in the name.
    for part in name.split(" "):
        # Check each part of the name against the keys in the correction dict
        if part in mapping.keys():
            # If exists in dict, overwrite that part of the name with the dict value for it.
            part = mapping[part]
        # Assemble each corrected piece of the name back together.
        after.append(part)
    # Return all pieces of the name as a string joined by a space.
    return " ".join(after)

    #return name


def test():
    st_types = audit(OSMFILE)
    assert len(st_types) == 3
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            if name == "West Lexington St.":
                assert better_name == "West Lexington Street"
            if name == "Baldwin Rd.":
                assert better_name == "Baldwin Road"


if __name__ == '__main__':
    test()