#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""
#Street name corrections dictionary, These are cases where the update_name overlaps the functionality like ST. , will be replaced by Street
edison_street_corrections = { 'St Georges Ave': "Saint George's Avenue",
           "St George's Ave": "Saint George's Avenue",
           'St. Georges Avenue':"Saint George's Avenue" ,
           "St. George's Avenue":"Saint George's Avenue" ,
           "St. Georges Avenue ":"Saint George's Avenue",
           ' Bayard St': 'Bayard Street',
           ' Wood Avenue South': 'Wood Avenue South',
            'GIBBONS CIRCLE BLDG E':'GIBBONS CIRCLE BUILDING-E',
            'NICHOL AVENUE BLD E' : 'NICHOL AVENUE BUILDING-E'
          }
# nvalid post codes with NJ pretext
invalid_alpha_zip={
    'NJ 07001' : '07001',
    'NJ 07065' : '07065',
    'NJ 08901' : '08901'
}
#Mapping dictonary , used by update_name function to replace the abbreviations with actua stringss
mapping = {'Alley': 'Alley',
           'Ave': 'Avenue',
           'Ave.': 'Avenue',
           'AVE.':'AVENUE',
           'AVE':'AVENUE',
           'Blvd': 'Boulevard',
           'Blvd.': 'Boulevard',
           'BLD' : 'BUILDING',
           'BLDG' : 'BUILDING',
           'Broadway': 'Broadway',
           'Bypass': 'Bypass',
           'Centre': 'Centre',
           'Cir': 'Circle',
           '(NJ)' : 'NJ',
           'Close': 'Close',
           'Diversion': 'Diversion',
           'Dr': 'Drive',
           'Dr.': 'Drive',
           'East': 'East',
           'Gate': 'Gate',
           'Grove': 'Grove',
           'Highway': 'Highway',
           'Hwy': 'Highway',
           'HWY.': 'Highway',
           'Mall': 'Mall',
           'Mews': 'Mews',
           'North': 'North',
           'Park': 'Park',
           'Pl': 'Place',
           'RD': 'Road',
           'Rd': 'Road',
           'Rd.': 'Road',
           'Rt.': 'Route',
           'Rt': 'Route',
           'Road,': 'Road',
           'U.S.':'US',
           'U.S':'US',
           'S.': 'South',
            "W.": "West",
            "N.": "North",
            "S.": "South",
            "E": "East",
           'South': 'South',
           'St': 'Street',
           'St.': 'Street',
           'Terminal': 'Terminal',
           'Walk': 'Walk',
           'Way': 'Way',
           'West': 'West',
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
           'Plz':'Plaza',
           'Ct':'Court',
           'Court': 'Court',
           'Trail': 'Trail',
           'Lane': 'Lane'
           }

#Reg ex expressios for pattern matching lower
lower = re.compile(r'^([a-z]|_)*$')
#Reg ex expressios for pattern matching lower colon
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
#Reg ex expressios for pattern matching proble character like special characters
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
#Node keys for Created Tag
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

#Determines if the attribute is addr:
def is_valid_address(elem):
    if elem.attrib['k'][:5] == "addr:":
        return True

#Determines if the attribute is TIGER:
def is_valid_tiger(elem):
    if elem.attrib['k'][:6] == "tiger:":
        return True

#Determines if the attribute is gnis:
def is_valid_gnis(elem):
    if elem.attrib['k'][:5] == "gnis:":
        return True

#Determines if the attribute is NHD:
def is_valid_nhd(elem):
    if elem.attrib['k'][:4] == "NHD:":
        return True

#Update the strret name after correcting the findigs in mapping keys
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

#This method shapes the osm xml to a valid JSON with sub elements created for created ,addr:,TIGER:,GNIS: and NHD:
def shape_element(element):
    node = {}
    #Shape element needs to be applied ony to nodes and ways
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        
        address_info = {}
        tiger_data={}
        nd_info = []
        gnis_data={}
        nhd_data={}
        #Type tag
        node["type"] = element.tag
        node["id"] = element.attrib["id"]
        if "visible" in element.attrib.keys():
            node["visible"] = element.attrib["visible"]
        #Add the position Info
        if "lat" in element.attrib.keys():
            node["pos"] = [float(element.attrib['lat']), float(element.attrib['lon'])]
        #Add the Created Document
        node["created"] = {"version": element.attrib['version'],
                            "changeset": element.attrib['changeset'],
                            "timestamp": element.attrib['timestamp'],
                            "uid": element.attrib['uid'],
                            "user": element.attrib['user']}
        #Loop over the primary nodes and get the attributes and retrieve key value information
        for tag in element.iter("tag"):
            #CHecking if the tag node is having any special characters
            p = problemchars.search(tag.attrib['k'])
            #Checking if there are any errors due to problem chars or if the tag Key is a "type",
            # because type should only be Way or node, Bt n data we found type tag with value as Gas,multipolygon
            if p or tag.attrib['k']=="type":
                continue
            #If address attribute found
            elif is_valid_address(tag):
                if ":" in tag.attrib['k'][5:]:
                    continue
                else:
                    #Correcting the street's data as required
                    if tag.attrib['k'][5:] == "street":
                        if tag.attrib['v'] in edison_street_corrections:
                            tag.attrib['v'] = edison_street_corrections[tag.attrib['v']]

                        tag.attrib['v'] = update_name(tag.attrib['v'],mapping)
                    elif tag.attrib['k'][5:] == "postcode":
                        if tag.attrib['v'] in invalid_alpha_zip:
                            tag.attrib['v'] = invalid_alpha_zip[tag.attrib['v']]
                        tag.attrib['v'] = tag.attrib['v'][:5]

                    address_info[tag.attrib['k'][5:]] = tag.attrib['v'].title()
            #If TIGER attribute found
            elif is_valid_tiger(tag):
                if ":" in tag.attrib['k'][6:]:
                    continue
                else:
                    tiger_data[tag.attrib['k'][6:]] = tag.attrib['v']
            #If GNIS attribute found
            elif is_valid_gnis(tag):
                if ":" in tag.attrib['k'][5:]:
                    continue
                else:
                    gnis_data[tag.attrib['k'][5:]] = tag.attrib['v']
             #If NHD attribute found
            elif is_valid_nhd(tag):
                if ":" in tag.attrib['k'][4:]:
                    continue
                else:
                    nhd_data[tag.attrib['k'][4:]] = tag.attrib['v']
            #Anyting else would be a individual attribute/key value pair in the jsno
            else:
                node[tag.attrib['k']] = tag.attrib['v']
        #preparing the JSON Objects
        if address_info != {}:
            node['address'] = address_info
        if tiger_data != {}:
            node['tiger'] = tiger_data
        if gnis_data != {}:
            node['gnis'] = gnis_data
        if nhd_data != {}:
            node['nhd'] = nhd_data
        for tagnew in element.iter("nd"):
            nd_info.append(tagnew.attrib['ref'])
            
        if nd_info != []:
            node['node_refs'] = nd_info
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('edison-nj.osm', True)


if __name__ == "__main__":
    test()