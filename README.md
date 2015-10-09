# The VU sound corpus
**Emiel van Miltenburg, Benjamin Timmermans, and Lora Aroyo (2015)**

This repository contains all the data and code that was used to annotate
sounds from [the Freesound.org database](www.freesound.org).

### Data
The folder  `./3-results/` contains all of our results, including `results.xml` which is the XML file that contains all the annotation data and `soundcollection.dtd`, which specifies the structure our resource. There are also four subfolders:

* `Frequencies`: this folder contains CSV files with frequency counts for all (author, raw, clustered, search) tags.
* `Search_matches_per_sound`: this folder contains a CSV file with the results from our search experiment.
* `typical_normalized` and `typical_raw`: these folders contain lists with typical keywords for the original authors and the crowd annotations. I.e. words that these different groups are biased to use in their annotations.

### XML format
The diagram below shows the XML structure of our resource. We represent our data as a collection of sounds.
Tags that may occur multiple times are marked with an asterisk.

![XML format](./images/sound_xml.png?raw=true)

Sounds have the following attributes: `id, batch, name, type, samplerate, duration, channels, bitrate` and `bitdepth` (the `id` and `name` attributes correspond to the ID and name in the Freesound.org database, and the `batch` attribute corresponds to the task batch in the crowdsourcing process, for full transparency about the data collection). 

Sounds also have a number of elements: `file, uri, descriptions, webrating` and `author-tags` correspond to the Freesound.org metadata (with `file`-elements linking to high-quality MP3 and OGG files). The `crowd-tags` element contains the normalized tags as `tag`-elements, which in turn contain the `raw` tags that they subsume. The `ratings`-element provides information about the quality of the sound: `webrating` contains the user-rating from Freesound.org, and `clarity` contains the automatically generated clarity rating (based on the clustered tags).


### How to load the sound data

Loading the data in Python is very simple: first import the `etree` module from `lxml`, and then parse the `results.xml` file.

    # Import lxml:
    from lxml import etree
    
    # Load the data:
    xml  = etree.parse('./3-results/results.xml')
    root = xml.getroot()
    
#### Selecting sounds with particular properties

We can use XPATH-expressions to find sounds with particular properties, e.g. with a certain duration or bitdepth.

    short_sounds = root.xpath('./sound[starts-with(@duration,"0.")]')
    bitdepth_24  = root.xpath('./sound[@bitdepth="24"]')

##### By crowd tag

Here is how to find all sounds with a 'bang' in them.

    def sounds_by_crowd_tag(tag):
        "Find sounds by original tags."
        for sound in root.iterfind('sound'):
            tags = [raw.attrib['label'] for raw in sound.xpath('./crowd-tags/tag/raw')]
            if tag in tags:
                yield sound
    
    bang_sounds = sounds_by_crowd_tag('bang')

##### By their description

We can also use the metadata of the sound to find the recordings you're after. Here is some code to get all the sounds that have a particular word in their description (e.g. 'periodically'):

    def sounds_by_description(word):
        "Find sounds by their description."
        for sound in root.iterfind('sound'):
            description = sound.find('description')
            if word in description.text:
                yield sound
    
    sounds_periodically = sounds_by_description("periodically")

##### By original tag

Let's look for sounds that the original author tagged 'vintage':

    def sounds_by_author_tag(tag):
        "Find sounds by original tags."
        for sound in root.iterfind('sound'):
            if sound.xpath('./author-tags/tag[@label="' + tag + '"]'):
                yield sound
    
    vintage_sounds = sounds_by_author_tag('vintage')

### Code & Replication
Our code was written in a combination of Python 2 (files 0-4) and Python 3 (files 5-8). To replicate our work, run the scripts in order. Files 2-4 require the [CrowdTruth](https://github.com/CrowdTruth/CrowdTruth) framework to be installed. 
