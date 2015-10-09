from lxml import etree as et
import requests
import csv
import unicodecsv
import re
import json

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}

trueSpammers = [3262732,6574449,31913360,32427474,31910622,31726043,32306791,32438173,32660177,31033819]

tp = 0
tn = 0
fp = 0
fn = 0


# temp: make list of job id's
jobs = range(1,16)

# construct a list of sound id's
r = requests.get('http://crowdtruth.lan/api/search?noCache&collection=entities&match[type]=unit&match[documentType]=sound&limit=100000')
entities = {d['content']['id']:d['_id'] for d in r.json()['documents']}

w = open('../steps/3-results/workers.csv', 'wb')
wr = unicodecsv.writer(w, encoding='utf-8')
wr.writerow(['filename','worker','CT spam','true spam','workerCosine','workerDisagreement','sounds','keywordsPerSound','wordsPerSound','charPerSound','wordsPerKeyword','charPerKeyword','charPerWord','duplicateUnits','duplicateKeywords'])

# for each job get the units and workers
for job in jobs:
    
    # load analytics from CrowdTruth platform
    r = requests.get('http://localhost/api/analytics/job?job=entity/sounds/job/'+str(job))
    results = r.json()['infoStat']
    
    # open the file of this job
    filename = results['platformJobId'] + '.csv'
    batch = results['platformJobId'].split('-')
    workers = results['metrics']['workers']['withoutFilter']
    metrics = results['metrics']['units']['withoutSpam']
    units = results['results']['withoutSpam']
    spammers = results['metrics']['spammers']['list']

    # open the files to combine the original input
    c = open('../steps/2-clustered/'+filename, 'r')
    clustered = UnicodeDictReader(c)

    # go through all judgments and aggregate the results to the corpus
    for worker in workers:
        workerId = int(worker.split('/')[-1])

        # did CrowdTruth tag this worker as spammer?
        spam = 0
        if worker in spammers:
            spam = 1

        # did we manually tag this worker as spammer?
        true = 0
        if workerId in trueSpammers:
            true = 1

        # statistics
        if true == 1 and spam == 1:
            tp += 1
        elif true == 0 and spam == 0:
            tn += 1
        elif true == 0 and spam == 1:
            fp += 1
        elif true == 1 and spam == 0:
            fn += 1

        cosine = round(workers[worker]['worker_cosine'],3)
        disagreement = round(1.0-workers[worker]['avg_worker_agreement'],3)

        sounds = workers[worker]['no_of_units']
        keywordsPerSound = round(workers[worker]['ann_per_unit'],3)
        wordsPerSound = round(workers[worker]['words_per_unit'],3)
        charPerSound = round(workers[worker]['characters_per_unit'],3)

        wordsPerKeyword = round(workers[worker]['words_per_keyword'],3)
        charPerKeyword = round(workers[worker]['characters_per_keyword'],3)

        charPerWord = round(workers[worker]['characters_per_word'],3)
        
        duplicateUnits = round(workers[worker]['duplicate_units'],3)
        duplicateKeywords = round(workers[worker]['duplicate_keywords'],3)
     
        wr.writerow([filename,workerId,spam,true,cosine,disagreement,sounds,keywordsPerSound,wordsPerSound,charPerSound,wordsPerKeyword,charPerKeyword,charPerWord,duplicateUnits,duplicateKeywords])
    
    c.close()
        
    print 'processed',filename,"tp:",tp,"tn:",tn,"fp:",fp,"fn:",fn


precision = tp / (tp + fp * 1.0)
recall = tp / (tp + fn * 1.0)
print "precision:",precision,"recall:",recall

w.close()