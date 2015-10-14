import re
import io, json

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}

# temp: make list of job id's
jobs = range(1,16)

r = requests.get('http://localhost/api/search?noCache&collection=entities&match[type]=unit&match[documentType]=sound&limit=100000')
entities = {d['content']['id']:d['_id'] for d in r.json()['documents']}

xml = et.Element("soundcollection")

task = 1
inputKeywords = 0
outputKeywords = 0
# for each job get the units and workers
for job in jobs:
    
    # load analytics from CrowdTruth platform
    r = requests.get('http://localhost/api/analytics/job?job=entity/sounds/job/'+str(job))
    results = r.json()['infoStat']
    

    with io.open('data.txt', 'w', encoding='utf-8') as f:
    f.write(unicode(json.dumps(data, ensure_ascii=False)))