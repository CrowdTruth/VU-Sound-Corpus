# coding: utf-8

import csv
from lxml import etree
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd

pd.options.display.mpl_style = 'default'
plt.rcParams['font.family'] = ['sans-serif']

def searchterms():
    "Generator that yields tuples of search terms (str) and their counts (int)"
    with open('../resources/searchterms/Analytics Search page Search Terms 20150316-20150818.csv') as f:
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
root = etree.parse('../steps/4-results/results.xml').getroot()

def all_xpath_labels(query):
    "Function that returns all labels of nodes that match a given xpath query."
    return [tag.attrib['label'].lower() for tag in root.xpath(query)]

def number_in_set(c,s):
    """Function that takes a counter and a set and returns the sum of counts for all
    items in that set"""
    return sum(v for k,v in c.items() if k in s)

# Get all the author, crowd(clustered) and crowd(raw) tags.
all_author_tags = set(all_xpath_labels('.//author-tags/tag'))
all_crowd_tags = set(all_xpath_labels('.//crowd-tags/tag'))
all_raw_tags = set(all_xpath_labels('.//crowd-tags/tag/raw'))
raw_tag_counter = Counter(all_xpath_labels('.//crowd-tags/tag/raw'))
total_raw = float(sum(raw_tag_counter.values()))

# Get all groups.
just_author = (all_author_tags - all_search_terms) & all_raw_tags
just_search = (all_search_terms - all_author_tags) & all_raw_tags
author_and_search = (all_author_tags & all_search_terms) & all_raw_tags
rest = all_raw_tags - (all_author_tags | all_search_terms)

# Get percentages.
just_author_num = (number_in_set(raw_tag_counter, just_author) / total_raw) * 100
just_search_num = (number_in_set(raw_tag_counter, just_search) / total_raw) * 100
author_and_search_num = (number_in_set(raw_tag_counter, author_and_search) / total_raw) * 100
rest_num = (number_in_set(raw_tag_counter, rest) / total_raw) * 100

# Put them in a dictionary.
d = {'Groups': ["Author tags", "Search terms", "Both", "Rest"],
     'Percentage': [just_author_num, just_search_num, author_and_search_num, rest_num]}

df = pd.DataFrame([[just_author_num, just_search_num, author_and_search_num, rest_num]],
                  columns=["Author tags", "Search terms", "Both", "Rest"])

bar_chart = df.plot(kind='barh', stacked=True, width=0.1, label=None, figsize=(4,2));

for container in bar_chart.containers:
    container.get_children()[0].set_y(-0.25)

bar_chart.grid(axis='y',b=False)
bar_chart.set_yticklabels([''])
# Create bar chart.
#ax = sns.barplot(x="Groups", y="Percentage", data=d, color='dodgerblue')
plt.savefig('../steps/4-results/figures/barchart.pdf')
