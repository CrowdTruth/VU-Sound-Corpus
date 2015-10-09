
# coding: utf-8

# DTD generator
#
# This code generates a (flawed) DTD to bootstrap the actual DTD writing.
# Of course this assumes that the XML has no mistakes, so one should always manually check the results!

# Basic imports
from lxml import etree
from collections import Counter

# Load the data
parser = etree.parse('../3-results/results.xml')
root = parser.getroot()

def attlist(element):
    "Function to generate an attribute list."
    if len(element.attrib) == 0:
        return ''
    attributes = ['\n\t' + attr + ' CDATA #REQUIRED ' for attr in element.attrib.keys()]
    components = ['<!ATTLIST ' + element.tag] + attributes + ['>']
    return '\n'+''.join(components)
    
def subtags(element):
    "Function to declare an element and its sub-elements."
    c = Counter([el.tag for el in element.getchildren()])
    children = [tag + '+' if count > 1 else tag
                for tag, count in c.items()]
    if len(children) > 0:
        child_declaration =  ' (' + ','.join(children) + ')' if len(children) > 0 else ''
    elif element.text is None:
        child_declaration = ' EMPTY'
    else:
        child_declaration = ' (#PCDATA)'
    return '<!ELEMENT ' + element.tag + child_declaration + '>'

def properties(element):
    "Function that combines the output of the two functions above."
    return subtags(element) + attlist(element)

def generate_dtd(root):
    "Recursive function that generates a DTD-template for the XML file."
    print('processing the tag ' + root.tag)
    todo = {element.tag:element for element in root.getchildren()}
    return [properties(root)] + [dtd for tag in todo for dtd in generate_dtd(todo[tag])]

# Write to file
with open('../3-results/soundcollection-template.dtd','w') as f:
    f.write('\n'.join(generate_dtd(root)))
