# coding: utf-8

import csv
from lxml import etree
from collections import Counter, defaultdict
from tabulate import tabulate
from scipy.stats import pearsonr, spearmanr

def searchterms():
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

def search_term_counts():
    d = defaultdict(int)
    for term, count in searchterms():
        d[term] += count
    return d

def get_author_tags(sound):
    return {tag.attrib['label'].lower() for tag in sound.xpath('./author-tags/tag')}

def get_normalized_tags(sound):
    return {tag.attrib['label'].lower() for tag in sound.xpath('./crowd-tags/tag')}

def get_raw_tags(sound):
    return {tag.attrib['label'].lower() for tag in sound.xpath('./crowd-tags/tag/raw')}

search_count_dict   = search_term_counts()
total_search_terms  = sum(b for a,b in search_count_dict.items())
set_of_search_terms = set(a for a,b in search_count_dict.items())

root                = etree.parse('../steps/4-results/results.xml').getroot()

def all_xpath_labels(query):
    return [tag.attrib['label'].lower() for tag in root.xpath(query)]

all_author_tags     = set(all_xpath_labels('.//author-tags/tag'))
author_tag_counter  = Counter(all_xpath_labels('.//author-tags/tag'))
author_tags_freq2   = {tag for tag, count in author_tag_counter.items() if count >= 2}
author_tags_freq5   = {tag for tag, count in author_tag_counter.items() if count >= 5}

id_authortags = {sound.attrib['id']: get_author_tags(sound) for sound in root.xpath('./sound')}
id_normaltags = {sound.attrib['id']: get_normalized_tags(sound) for sound in root.xpath('./sound')}
id_rawtags    = {sound.attrib['id']: get_raw_tags(sound) for sound in root.xpath('./sound')}

################################################################################
# Matches per sound (types)
################################################################################

def avg(l): return "{0:.2f}".format(float(sum(l))/len(l))

authortags_mps = avg([len(tags & set_of_search_terms) for tags in id_authortags.values()])
normaltags_mps = avg([len(tags & set_of_search_terms) for tags in id_normaltags.values()])
rawtags_mps    = avg([len(tags & set_of_search_terms) for tags in id_rawtags.values()])

author_normal_mps = avg([len((tags|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_normaltags.items()])

cons_normaltags_mps = avg([len(((tags & all_author_tags)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_normaltags.items()])

cons2_normaltags_mps = avg([len(((tags & author_tags_freq2)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_normaltags.items()])

cons5_normaltags_mps = avg([len(((tags & author_tags_freq5)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_normaltags.items()])

author_raw_mps = avg([len((tags|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_rawtags.items()])
                         
cons_rawtags_mps    = avg([len(((tags & all_author_tags)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_rawtags.items()])

cons2_rawtags_mps    = avg([len(((tags & author_tags_freq2)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_rawtags.items()])

cons5_rawtags_mps    = avg([len(((tags & author_tags_freq5)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_rawtags.items()])

################################################################################
# Matches per sound (tokens)
################################################################################

def tm(s):
    "Returns number of matches (tokens)"
    return sum(search_count_dict[i] for i in s)

tok_authortags_mps = avg([tm(tags & set_of_search_terms) for tags in id_authortags.values()])
tok_normaltags_mps = avg([tm(tags & set_of_search_terms) for tags in id_normaltags.values()])
tok_rawtags_mps    = avg([tm(tags & set_of_search_terms) for tags in id_rawtags.values()])

tok_author_normal_mps    = avg([tm((tags | id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_normaltags.items()])

tok_cons_normaltags_mps  = avg([tm(((tags & all_author_tags)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_normaltags.items()])

tok_cons2_normaltags_mps = avg([tm(((tags & author_tags_freq2)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_normaltags.items()])

tok_cons5_normaltags_mps = avg([tm(((tags & author_tags_freq5)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_normaltags.items()])

tok_author_raw_mps = avg([tm((tags | id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_rawtags.items()])

tok_cons_rawtags_mps     = avg([tm(((tags & all_author_tags)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_rawtags.items()])

tok_cons2_rawtags_mps    = avg([tm(((tags & author_tags_freq2)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_rawtags.items()])

tok_cons5_rawtags_mps    = avg([tm(((tags & author_tags_freq5)|id_authortags[i]) & set_of_search_terms)
                           for i,tags in id_rawtags.items()])

table = [['author tags', authortags_mps, tok_authortags_mps],
         ['normalized tags', normaltags_mps, tok_normaltags_mps],
         ['raw tags', rawtags_mps, tok_rawtags_mps],
         ['<b>Normalized + Author</b>', '<b>MPS (types)</b>', '<b>MPS (tokens)</b>'],
         ['normalized tags', author_normal_mps, tok_author_normal_mps],
         ['conservative normalized tags', cons_normaltags_mps, tok_cons_normaltags_mps],
         ['conservative normalized tags >= 2', cons2_normaltags_mps, tok_cons2_normaltags_mps],
         ['conservative normalized tags >= 5', cons5_normaltags_mps, tok_cons5_normaltags_mps],
         ['<b>Raw + Author</b>', '<b>MPS (types)</b>', '<b>MPS (tokens)</b>'],
         ['raw tags', author_raw_mps, tok_author_raw_mps],
         ['conservative raw tags', cons_rawtags_mps, tok_cons_rawtags_mps],
         ['conservative raw tags >= 2', cons2_rawtags_mps, tok_cons2_rawtags_mps],
         ['conservative raw tags >= 5', cons5_rawtags_mps, tok_cons5_rawtags_mps],
        ]

with open('../steps/4-results/search_matches_per_sound/mps.csv','w') as f:
    writer = csv.writer(f)
    writer.writerow(['Method','MPS (types)', 'MPS (tokens)'])
    for row in table:
        if not '<b>MPS (types)</b>' in row:
            writer.writerow(row)

print(tabulate(table, headers=['Method', 'MPS (types)', 'MPS (tokens)'],tablefmt='simple'))

x = [float(row[1]) for row in table if not '<b>MPS (types)</b>' in row]
y = [float(row[2]) for row in table if not '<b>MPS (types)</b>' in row]

print('Correlation between type and token MPS (corr,significance):')
print('Spearman: ' + str(spearmanr(x,y)[0]))
print('Pearson: ' + str(pearsonr(x,y)[0]))
