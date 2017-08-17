
# coding: utf-8

# In[6]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "map"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Plaza", "Broadway", "Circle", "Park", "Driveway","Highway",
            "Real", "Way", 'Bridge', 'Center']

mapping = {"St": "Street",
           "St.": "Street",
           "Ave": "Avenue",
           "Rd.": "Road",
           'Rd': 'Road',
           'Ave': 'Avenue',
           'Blvd': 'Boulevard',
           'Dr': 'Drive',
           'parkway': 'Parkway'
            }


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
    osm_file.close()
    return street_types

def update_name(name, mapping):

    m = street_type_re.search(name)
    if m not in expected: #Check for streets that can be automatically corrected using mapping
        if m.group() in mapping.keys():
            name = re.sub(m.group(), mapping[m.group()], name)
            
    # Correcting individual street names
    if name == 'El Camino Real #D':
        name = name.replace('#D','')

    if name == 'Se Quad Sr 92 / Ralston Ic':
        name = name.replace('Se Quad Sr 92 / Ralston Ic','Highway 92')
    
    if name == 'Leslie':
        name = 'Leslie Street'
    
    if name == 'Ne Quad Us 101 / 3rd Ave Off Lindbergh':
        name = '3rd Avenue'
    
    if name == 'Avlameda de las Pulgas':
        name = 'Alameda de las Pulgas'
    
    if name == 'Nw Quad I-280 / Sr 35 Ic @ Jct Hayne Rd, Golf Course Dr, Skyline Blvd,':
        name = 'Skyline Boulevard'
    
    if name == 'Adrian Road Ste 6':
        name = 'Adrian Road'
    
    if name == 'Under Ramp Sw Quad Of Us 101 / Sr 92 Ic Off 19th Ave & Fashion Island Boulevard':
        name = 'Fashion Island Boulevard'
    
    if name == 'Adrian Court, Suite A':
        name = 'Adrian Court'
    return name
    

update_street = audit(OSMFILE)

pprint.pprint(dict(update_street))

for street_type, ways in update_street.iteritems():
    for name in ways:
        better_name = update_name(name, mapping)
        print  '{x} -> {y}'.format(x = name, y = better_name)




# In[18]:

def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit_postcode(postcodes, postcode):
    postcodes[postcode].add(postcode)
    return postcodes

def audit_post(osmfile):
    osm_file = open(osmfile, "r")
    postcodes = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    audit_postcode(postcodes, tag.attrib['v'])
    osm_file.close()
    return postcodes

update_postcodes = audit_post(OSMFILE)
pprint.pprint(dict(update_postcodes))


# In[53]:

def update_postcode(postcode):
    if len(postcode) == 5:
        valid_postcode = postcode
        return valid_postcode
    if 'CA' in postcode:
        valid_postcode = postcode[3:]
        return valid_postcode
    if postcode.find('-'):
        valid_postcode = postcode[:5]
        return valid_postcode    
    if len(postcode) == 9 and not postcode.find('CA'):
        valid_postcode = postcode[:5]
        return valid_postcode

for postcodes, ways in update_postcodes.iteritems():
    for name in ways:
        better_name = update_postcode(name)
        print  '{x} => {y}'.format(x = name, y = better_name)


# In[ ]:



