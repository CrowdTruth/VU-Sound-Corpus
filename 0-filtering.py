import os
import unicodecsv
import seaborn as sns
import pandas as pd
import csv

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}

# filter judgments that are obvious outliers

files = os.listdir('0-input-crowd')
for filename in files:

    inputJudgments = 0
    outputJudgments = 0
    inputKeywords = 0
    outputKeywords = 0
    uniqueKeywords = {}

    f = open('0-input-crowd/'+filename, 'r')
    reader = csv.DictReader(f)
   
    w = open('1-filtered/'+filename, 'wb')

    # write column names
    fieldnames = reader.fieldnames
    wr = unicodecsv.DictWriter(w, fieldnames=fieldnames)
    wr.writeheader()
    
    for row in reader:
        
        inputJudgments += 1
        if row['id'] not in uniqueKeywords:
            uniqueKeywords[row['id']] = set()
        
        # tokenize and clean the judgment:
        # - lowercase all
        # - strip spaces
        # - remove empty tags
        tags = row['keywords'].lower().strip().split(',')
        tags = [tag.strip() for tag in tags if len(tag.strip()) > 0]
        
        inputKeywords += len(tags)
        
        # - remove duplicate tags
        tags = set(tags)
       
        #print row[35],"->",",".join(tags)
        outputKeywords += len(tags)
        for tag in tags:
            if tag not in uniqueKeywords[row['id']]:
                uniqueKeywords[row['id']].add(tag)
                
        row['keywords'] = ",".join(tags)
        wr.writerow(row)
        outputJudgments += 1
    
    f.close()
    w.close()

    uniqueKeywords = [len(uniqueKeywords[s]) for s in uniqueKeywords]  
    uniqueKeywords = float(sum(uniqueKeywords)) / len(uniqueKeywords)
        
    print "Processed",filename,"(Judgments:",outputJudgments,"Keywords:",inputKeywords-outputKeywords,"removed,",outputKeywords,"left,",uniqueKeywords,"unique)"
