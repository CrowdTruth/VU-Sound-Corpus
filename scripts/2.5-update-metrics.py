import requests
import os

# save results to CrowdTruth and run CrowdTruth metrics

jobs = range(1,16)

for j in jobs:
    r = requests.get('http://crowdtruth.lan/api/analytics/analytics?job=entity/sounds/job/'+str(j),)
    print j,r.text

    # break if there was an error
#    if r.text is not 'done':
#        break