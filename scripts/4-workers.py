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

manualSpam = {1:[3262732,6574449],
            2:[],
            3:[],
            4:[],
            5:[],
            6:[],
            7:[],
            8:[30276268],
            9:[31913360,32427474],
            10:[],
            11:[31910622],
            12:[],
            13:[21913197],
            14:[31726043,32306791],
            15:[32438173,32660177]}


# temp: make list of job id's
jobs = range(1,16)

# construct a list of sound id's
r = requests.get('http://crowdtruth.lan/api/search?noCache&collection=entities&match[type]=unit&match[documentType]=sound&limit=100000')
entities = {d['content']['id']:d['_id'] for d in r.json()['documents']}

w = open('../steps/3-results/workers.csv', 'wb')
wr = unicodecsv.writer(w, encoding='utf-8')
wr.writerow(['filename','worker','CT spam','manual spam','workerCosine','workerDisagreement','sounds','keywordsPerSound','wordsPerSound','charPerSound','wordsPerKeyword','charPerKeyword','charPerWord','duplicates'])

# for each job get the units and workers
for job in jobs:
    
    inputKeywords = 0
    outputKeywords = 0
    
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
        manual = 0
        if workerId in manualSpam[job]:
            manual = 1
            #print filename,workerId

        cosine = round(workers[worker]['worker_cosine'],3)
        disagreement = round(1.0-workers[worker]['avg_worker_agreement'],3)

        sounds = workers[worker]['no_of_units']
        keywordsPerSound = round(workers[worker]['ann_per_unit'],3)
        wordsPerSound = round(workers[worker]['words_per_unit'],3)
        charPerSound = round(workers[worker]['characters_per_unit'],3)

        wordsPerKeyword = round(workers[worker]['words_per_keyword'],3)
        charPerKeyword = round(workers[worker]['characters_per_keyword'],3)

        charPerWord = round(workers[worker]['characters_per_word'],3)
        
        duplicates = round(workers[worker]['duplicate_count'],3)
      
        wr.writerow([filename,workerId,spam,manual,cosine,disagreement,sounds,keywordsPerSound,wordsPerSound,charPerSound,wordsPerKeyword,charPerKeyword,charPerWord,duplicates])
    
    c.close()
    print 'processed',filename
w.close()