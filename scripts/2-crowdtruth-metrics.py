import requests
import os

# save results to CrowdTruth and run CrowdTruth metrics
for f in os.listdir('../2-clustered/'):
    files = {'file': open('../2-clustered/'+f, 'rb')}
    values = {'input-project':'sounds',
              'input-type':'sound',
              'output-type':'sound2'}
    r = requests.post('http://localhost/api/import/importresults', files=files, data=values)
    print f,r.text

    # break if there was an error
#    if r.text is not 'done':
#        break
