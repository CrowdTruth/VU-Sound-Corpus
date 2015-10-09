# coding: utf-8

import csv
from lxml import etree
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from collections import Counter

def searchterms():
    "Generator that yields tuples of search terms (str) and their counts (int)"
    with open('./searchterms/Analytics Search page Search Terms 20150316-20150818.csv') as f:
        for i in range(6):
            next(f)
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            if row['Search Term'] == '(other)':
                continue
            yield (row['Search Term'].lower(), int(row['Total Unique Searches'].replace(',','')))
            if row['Search Term'] == 'card flip':
                break

all_search_terms = set(a for a,b in searchterms())
root = etree.parse('./3-results/results.xml').getroot()

def all_xpath_labels(query):
    "Function that returns all labels of nodes that match a given xpath query."
    return [tag.attrib['label'].lower() for tag in root.xpath(query)]

# Get all the author, crowd(clustered) and crowd(raw) tags.
all_author_tags = set(all_xpath_labels('.//author-tags/tag'))
all_crowd_tags = set(all_xpath_labels('.//crowd-tags/tag'))
all_raw_tags = set(all_xpath_labels('.//crowd-tags/tag/raw'))


# Create a venn diagram for the overlap between the sets of tags
v = venn3([all_author_tags, all_crowd_tags, all_search_terms],['Author', 'Crowd', 'Search'])
for patch in v.patches:
    patch.set_edgecolor('black')
plt.savefig('./3-results/figures/venn_clustered.pdf')
plt.clf()

# Create another venn diagram for the overlap between the sets of tags
v = venn3([all_author_tags, all_raw_tags, all_search_terms],['Author', 'Crowd', 'Search'])
for patch in v.patches:
    patch.set_edgecolor('black')
plt.savefig('./3-results/figures/venn_raw.pdf')

# Generate frequency lists.
all_author_tags = Counter(all_xpath_labels('.//author-tags/tag')).most_common()
all_crowd_tags = Counter(all_xpath_labels('.//crowd-tags/tag')).most_common()
all_raw_tags = Counter(all_xpath_labels('.//crowd-tags/tag/raw')).most_common()

def write_freqs(l, filename):
    with open('./3-results/frequencies/' + filename, 'w') as f:
        f.writelines([a + '\t' + str(b) + '\n' for a,b in l])

write_freqs(all_author_tags,'authortags.txt')
write_freqs(all_crowd_tags,'crowdtags.txt')
write_freqs(all_raw_tags,'rawtags.txt')
write_freqs(searchterms(),'searchterms.txt')
