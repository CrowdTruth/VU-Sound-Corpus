# Standard
from math import log
from collections import defaultdict, Counter
from itertools import combinations,product,permutations

# Non-standard
import unicodecsv
from tabulate import tabulate
from gensim.models import Word2Vec
import networkx as nx
import os
import csv
import re

"load vector space model (this takes a few minutes)"

from gensim.models import Word2Vec
global model
global vocab
googlenews = 'c:/GoogleNews-vectors-negative300.bin.gz'
model      = Word2Vec.load_word2vec_format(googlenews, binary=True)
vocab      = set(model.vocab.keys())
print "Done loading GoogleNews vector space model."


################################################################################
# I/O

def crowd_dict(filename):
    "Create a dictionary: k=id, v=list of tags associated with the id."
  
    # Open the file:
    with open(filename) as f:
        reader = csv.DictReader(f)
        
        d = {}
        for row in reader:
            if row['id'] not in d:
                d[row['id']] = []
            tags = row['keywords'].lower().strip().split(',')
            for tag in tags:
                tag = re.sub('[^a-z0-9- ]+', '', tag)
                tag = tag.strip()
                if len(tag) > 0:
                    d[row['id']].append(tag)
        return d

def freesound_dict():
    data = {}
    with open("../data/all_tags.txt") as f:
        for line in f:
            split = line.split()
            data[split[0]] = split[1:]
    return data

################################################################################
# Stats

def log_likelihood(corpus_1_counts,corpus_2_counts):
    """Computes the log likelihood for words to appear more in one corpus than
    in the other."""
    # Rayson, P. and Garside, R. (2000)
    # http://dl.acm.org/citation.cfm?id=1117730
    total_c1    = float(sum(corpus_1_counts.values()))
    total_c2    = float(sum(corpus_2_counts.values()))
    total       = total_c1 + total_c2
    overlap     = set(corpus_1_counts.keys()) & set(corpus_2_counts.keys())
    l = []
    for k in overlap:
        a = float(corpus_1_counts[k])
        b = float(corpus_2_counts[k])
        E1 = total_c1 * (a+b) / total
        E2 = total_c2 * (a+b) / total
        LL = 2 * ((a * log(a/E1)) + (b * log(b/E2)))
        l.append((LL,k))
    return sorted(l,reverse=True)

def typical_words(corpus_1_counts,corpus_2_counts,c1_name='c1',c2_name='c2'):
    """Uses the log likelihood function to determine words that are typical for
    the first corpus (c1) and the second corpus (c2)."""
    
    # Thanks to Paul Rayson's website (http://ucrel.lancs.ac.uk/llwizard.html)
    # we are able to say something about which words occur *significantly* more
    # in one corpus than in the other. See the other note below.
    
    sorted_log_scores = log_likelihood(corpus_1_counts,corpus_2_counts)
    
    total       = sum(corpus_1_counts.values())
    c1_rel_freq = dict((k,float(val)/total) for k,val in corpus_1_counts.items())
    
    total       = sum(corpus_2_counts.values())
    c2_rel_freq = dict((k,float(val)/total) for k,val in corpus_2_counts.items())
    
    c1_words = []
    c2_words = []
    for val,word in sorted_log_scores:
        if not val > 3.84:
            # this corresponds to the 0.05 significance level according to:
            # http://ucrel.lancs.ac.uk/llwizard.html
            break
        if c1_rel_freq[word] > c2_rel_freq[word]:
            c1_words.append(word)
        elif c1_rel_freq[word] < c2_rel_freq[word]:
            c2_words.append(word)
    return {c1_name:c1_words, c2_name:c2_words}

def spacetodash(l):
    "Replace spaces by dashes to ease the comparison."
    return [w.replace(' ','-') for w in l]



################################################################################
# Cleaner decorator

def cleaner(func):
    "Clean the pair lists that are produced by the cleaning functions below."
    
    def clean_pairlist(*args, **kwargs):
    # If something needs to be done with the output of the cleaning functions,
    # put it here and it will apply to all of them.
    
    # This code prevents strings from mapping to multiple strings.
    # It chooses the most frequent target string.
        pairs   = set(func(*args, **kwargs))
        d       = defaultdict(list)
        second  = [b for a,b in pairs]
        for a,b in pairs:
            d[a].append(b)
        return set([(a,max(d[a], key=lambda b:second.count(b))) for a in d])
    return clean_pairlist

################################################################################
# Some useful cleaning functions.

def levenshtein(s, t):
        ''' From Wikipedia article; Iterative with two matrix rows. '''
        if s == t: return 0
        elif len(s) == 0: return len(t)
        elif len(t) == 0: return len(s)
        v0 = [None] * (len(t) + 1)
        v1 = [None] * (len(t) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s)):
            v1[0] = i + 1
            for j in range(len(t)):
                cost = 0 if s[i] == t[j] else 1
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
 
        return v1[len(t)]

def clean(l,check_function):
    """General function that takes a list of tags-to-be-cleaned and a cleaning
    function (defined below) and returns a cleaned list."""
    d = dict(check_function(l))
    for k in set(l):
        if not k in d.keys():
            d[k] = k
    cleaned_list = [d[i] for i in l]
    return cleaned_list, d.items()

def clean_all(d,check_function,replacements=None):
    "Cleans all the entries in the dictionary using a particular function."
    # Initialize:
    num_items          = float(len(d.keys()))
    new_index          = dict()

    # For each sound, and its associated list of tags:
    for sound_id,tags in d.items():
        # Compute stats before, then initialize some variables for the loop.
        old_tags = []
        new_tags = tags
        counter  = 0
        # Clean the list until a next round of cleaning doesn't yield any difference.
        # Maximum number of rounds: 10. Else we assume there's an infinite loop.
        # I don't expect this to happen, but it's best to be safe. We'll get a notification
        # if this happens.
        while old_tags != new_tags:
            old_tags    = new_tags
            new_tags,changes = clean(old_tags,check_function)
            replacements[sound_id].update(changes)
            counter    += 1
            if counter > 10:
                print "Infinite loop? I'm out!"
                break
        # Update the tags for the sound, and add length of the list after cleaning
        # to the stats.
        new_index[sound_id] = new_tags
    # Print the stats for this round, and return new index + all replacement data.
    return new_index, replacements

def changed(d,check_function):
    "Returns the keys of the items for which changes are proposed."
    return [k for k in d if not check_function(d[k]) == set([])]

################################################################################
# Syntactic Cleaning
# - order
# - misspelling
# - spaces
# - morphology

# Same problems as in phonological theory: how do you order these functions?
# A function may make the list more suitable for another function, so that it can
# reduce it further (FEEDING), or it may actually change the data so that another
# function cannot reduce the list anymore (BLEEDING). Reference:
#
# Kiparsky, Paul. 1968. Linguistic universals and linguistic change. In Universal in Linguistic
# Theory, ed. Emmon Bach and Robert T. Harms, 170-202. New York: Holt, Reinhart, and Winston.

@cleaner
def check_dashes(l):
    "Normalizes strings by replacing all dashes by spaces."
    return [(w,w.replace('-',' ')) for w in l]

@cleaner
def check_order(l):
    """Eliminates order variation in multiword expressions, by taking all order-
    variants and mapping them to a string where all words are sorted alphabetically."""
    pairs = []
    phrases = [w.split() for w in set(l) if ' ' in w]
    for a,b in combinations(phrases,2):
        if set(a) == set(b):
            a = ' '.join(sorted(a))
            b = ' '.join(b)
            pairs.append((a,a))
            pairs.append((b,a))
    return pairs

@cleaner
def check_spaces(l):
    "Proposes pairs (a,b) where a is equal to b without a space."
    return [(w,''.join(w.split())) for w in l if ' ' in w
                                              and ''.join(w.split()) in l]

@cleaner
def check_inclusion(l):
    "Proposes pairs (a,b) where b contains a space and a is included in b."
    words       = set(l)
    space_words = set([w for w in l if ' ' in w])
    return [(w,sw) for sw in space_words for w in words & set(sw.split(' '))]

@cleaner
def check_substring(l):
    "Proposes pairs (a,b) where b contains a space and a is a substring of b."
    words       = set(l)
    space_words = set([w for w in l if ' ' in w])
    nospace     = words - space_words
    return [(w,sw) for w,sw in product(nospace,space_words) if w in sw]

@cleaner
def check_spelling(l,threshold=1):
    """Proposes pairs (a,b) where b is the spell-corrected version of a.
    
    This function makes use of an extensive word list. If a word A is not in the
    list and it has a smaller Levenshtein distance to another word B in l than
    the threshold, then we assume that B is the correct spelling of A."""
    pairs = []
    for a,b in combinations(l,2):
        if len(a) > 3 and len(b) > 3:
            if a in vocab and not b in vocab:
                if levenshtein(a,b) <= threshold:
                    pairs.append((b,a))
            elif b in vocab and not a in vocab:
                if levenshtein(a,b) <= threshold:
                    pairs.append((a,b))
    return pairs

@cleaner
def check_morphology(l):
    """Proposes reductions of words to their stem if the stem or another
    morphological variant is also present in l"""
    tags  = set(l)
    pairs = []
    for w in l:
        if w.endswith('s'):
            stem     = w[:-1]
            variants = set([stem + suffix for suffix in ['','ed','ing']])
            if not variants.isdisjoint(tags):
                pairs.append((w,stem))
        elif w.endswith('ed'):
            stem     = w[:-2]
            variants = set([stem + suffix for suffix in ['','s','ing']])
            if not variants.isdisjoint(tags):
                pairs.append((w,stem))
        elif w.endswith('ing'):
            stem = w[:-3]
            variants = set([stem + suffix for suffix in ['','ed','s']])
            if not variants.isdisjoint(tags):
                pairs.append((w,stem))
    return pairs

################################################################################
# Semantic Cleaning

@cleaner
def check_semantics(l,threshold=0.75):
    "Proposes pairs of semantically related words."
    return [tuple(sorted([a,b],key=lambda x:l.count(x)))
                for a,b in combinations(set(l),2)
                if a in vocab and b in vocab
                and model.similarity(a,b) >= threshold]

################################################################################
# Shorthand functions to test everything.

def run_cleaning(filename, clean_functions = [ check_dashes,
                                     check_spaces,
                                     check_spelling,
                                     check_order,
                                     check_morphology,
                                     check_inclusion,
                                     check_semantics,
                                     check_substring   ]):
    "Wrapper to quickly test the result of the various cleaning functions."
    try:
        'test' in vocab
    except:
        print "Please load the vector space model using load_model"
        return None
    cd           = crowd_dict(filename)
    d            = cd.copy()
    sound_ids    = d.keys()
    replacements = {k:set() for k in sound_ids}
    
    
    #print sum(length_before)/num_items, "was reduced to", sum(length_after)/num_items
    
    for func in clean_functions:
        d, replacements = clean_all(d,func,replacements)
    graph_dict = dict()
    for k in sound_ids:
        G = nx.DiGraph()
        G.add_edges_from((b,a) for a,b in replacements[k])
        graph_dict[k] = G

    clusters = {k:
               {desc: tag
               for tag in set(d[k])
               for desc in nx.descendants(graph_dict[k],tag)|set([tag]) if tag is not desc}
               for k in d}

    return d, clusters


# replace the tags with their clustered variant
def replaceTags(filename):
    d,clusters = run_cleaning('../steps/1-filtered/'+filename)
    keys = d.keys()
   
    f = open('../steps/1-filtered/'+filename, 'r')
    w = open('../steps/2-clustered/'+filename, 'wb')
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    fieldnames.append('clustering')
    wr = unicodecsv.DictWriter(w, fieldnames=fieldnames)

    wr.writeheader()

    for row in reader:
        old = row['keywords']
        tags = row['keywords'].lower().strip().split(',')
        newtags = []
        clustering = []
        for tag in tags:
            tag = re.sub('[^a-z0-9- ]+', '', tag)
            tag = tag.strip()
            oldtag = tag
            if len(tag) > 0:
                if tag in clusters[row['id']]:
                    tag = clusters[row['id']][tag]
                newtags.append(tag)
                clustering.append("\""+oldtag+"\":\""+tag+"\"")
        row['clustering'] = "{"+",".join(clustering)+"}"
        row['keywords'] = ",".join(newtags)
        #rint old,"->",row[35]
        wr.writerow(row)
    
    f.close()
    w.close()
        
    print "Processed",filename

# replace tags in all crowd files
files = os.listdir('../steps/1-filtered')
for filename in files:
    replaceTags(filename)
    

import json
        
# produce stats
files = os.listdir('../steps/2-clustered')
for filename in files:

    keywordCount = 0
    keywordChange = 0
    sounds = {}

    f = open('../steps/2-clustered/'+filename, 'r')
    reader = csv.DictReader(f)

    for row in reader:
        clusters = json.loads(row['clustering'])
        if row['id'] not in sounds:
            sounds[row['id']] = set()
        for cluster in clusters:
            keywordCount += 1
            if clusters[cluster] not in sounds[row['id']]:
                sounds[row['id']].add(clusters[cluster])
            if clusters[cluster] <> cluster:
                keywordChange += 1
    clusterCount = sum([len(sounds[s]) for s in sounds])
    print "Keywords:",keywordCount,"Changes:",keywordChange,"Clusters:",clusterCount
