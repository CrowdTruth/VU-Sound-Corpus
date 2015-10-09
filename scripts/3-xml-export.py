from lxml import etree as et
import requests
import csv
import re
import json

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}


# temp: make list of job id's
jobs = range(1,16)

# construct a list of sound id's
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
    
    # open the file of this job
    filename = results['platformJobId'] + '.csv'
    batch = results['platformJobId'].split('-')
    workers = results['metrics']['workers']['withFilter']
    metrics = results['metrics']['units']['withoutSpam']
    units = results['results']['withoutSpam']
    spammers = results['metrics']['spammers']['list']

    # open the files to combine the original input
    c = open('../2-clustered/'+filename, 'r')
    clustered = UnicodeDictReader(c)

    # keep a list of units in this task
    task_units = []
                                          
    # go through all judgments and aggregate the results to the corpus
    for sound in clustered:
        
        # sounds were grouped in tasks of three, however this data is not in the input
        # we replicate this by adding a task number, incremented for every three sounds
        if sound['_unit_id'] not in task_units and len(task_units) >= 3:
            task_units = []
            task += 1
        elif sound['_unit_id'] not in task_units:
            task_units.append(sound['_unit_id'])
        
        # only add if sound is not yet in the corpus
        if xml.find(".//sound[@id='"+sound['id']+"']") is None:
            s = et.SubElement(xml, "sound")
            s.set('id', sound['id'])
            s.set('batch', batch[0]+'.'+batch[1])
            s.set('task', str(task))
            s.set('name', sound['name'])
            s.set('type', sound['type'])
            s.set('samplerate', sound['samplerate'])
            s.set('duration', sound['duration'])
            s.set('channels', sound['channels'])
            s.set('bitrate', sound['bitrate'])
            s.set('bitdepth', sound['bitdepth'])
            
            # add file elements to sound
            mp3 = et.SubElement(s, "file")
            mp3.text = sound['preview-hq-mp3']
            mp3.set('type', 'mp3')
            ogg = et.SubElement(s, "file")
            ogg.text = sound['preview-hq-ogg']
            ogg.set('type', 'ogg')
                                  
            # add uri element to sound
            uri = et.SubElement(s, "uri")
            uri.text = str(sound['url'])
            uri.set('author', sound['username'])
            uri.set('license', sound['license'])
            
            # add description element to sound
            descr = et.SubElement(s, "description")
            descr.text = sound['description']
            
            # add ratings element to sound
            ratings = et.SubElement(s, "ratings")
            # clarity of sound from CrowdTruth metrics
            clarity = et.SubElement(ratings, "clarity")
            clarity.set('count', str(metrics[entities[sound['id']]]['avg']['no_annotators']))
            clarity.text = str(metrics[entities[sound['id']]]['avg']['max_relation_Cos'])
            # web rating of sound from freesound.org
            webrating = et.SubElement(ratings, "webrating")
            webrating.set('count', sound['num_ratings'])
            webrating.text = sound['avg_rating']
                        
            # add author tags element to sound
            tags = et.SubElement(s, "author-tags")
            for t in re.split(r' |,', sound['tags']):
                # add each tag
                tag = et.SubElement(tags, "tag")
                tag.set('label', t)
            
            
            # add crowd tags element to sound
            tags = et.SubElement(s, "crowd-tags")

        clusters = json.loads(sound['clustering'])
        inputKeywords += len(clusters)
                          
        # add the tags to the crowd-tags element if this worker was not a spammer
        if "crowdagent/CF/"+sound['_worker_id'] not in spammers:
            outputKeywords += len(clusters)

            # add for each cluster the raw tag and clustered tag
            for cluster in clusters:
                tag = tags.find("./tag[@label='"+clusters[cluster]+"']")
                # if the cluster is not in the xml
                if tag is None:
                    tag = et.SubElement(tags, "tag")
                    tag.set('label', clusters[cluster])
                    tag.set('count', '1')
                    tag.set('children', '0')
                else:
                    tag.set('count', str(int(tag.attrib['count']) + 1))
                
                raw = tag.find("./raw[@label='"+cluster+"']")
                # if the raw tag is not yet in the cluster
                if raw is None:
                    # add raw tag
                    raw = et.SubElement(tag, "raw")
                    raw.set('label', cluster)
                    raw.set('count', "1")
                    tag.set('children', str(int(tag.attrib['children']) + 1))
                else:
                    raw.set('count', str(int(raw.attrib['count']) + 1))

            
    c.close()
    
    print 'processed',filename,"Keywords:",inputKeywords-outputKeywords,"filtered,",outputKeywords,"left)"

# output tree as XML
tree = et.ElementTree(xml)
tree.write('../3-results/results.xml',pretty_print=True)
