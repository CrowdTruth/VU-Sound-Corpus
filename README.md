# The VU sound corpus
**Emiel van Miltenburg, Benjamin Timmermans, and Lora Aroyo (2015)**

This repository contains all the data and code that was used to annotate
sounds from [the Freesound.org database](www.freesound.org).

### Data
The folder  `./3-results/` contains all of our results, including `results.xml` which is the XML file that contains all the annotation data and `soundcollection.dtd`, which specifies the structure our resource. There are also four subfolders:

* `Frequencies`: this folder contains CSV files with frequency counts for all (author, raw, clustered, search) tags.
* `Search_matches_per_sound`: this folder contains a CSV file with the results from our search experiment.
* `typical_normalized` and `typical_raw`: these folders contain lists with typical keywords for the original authors and the crowd annotations. I.e. words that these different groups are biased to use in their annotations.

### Code
TODO

### XML format
The diagram below shows the XML structure of our resource. We represent our data as a collection of sounds.
Tags that may occur multiple times are marked with an asterisk.

![XML format](./images/sound_xml.png?raw=true)

Sounds have the following attributes: `id, batch, name, type, samplerate, duration, channels, bitrate` and `bitdepth` (the `id` and `name` attributes correspond to the ID and name in the Freesound.org database, and the `batch` attribute corresponds to the task batch in the crowdsourcing process, for full transparency about the data collection). 

Sounds also have a number of elements: `file, uri, descriptions, webrating` and `author-tags` correspond to the Freesound.org metadata (with `file`-elements linking to high-quality MP3 and OGG files). The `crowd-tags` element contains the normalized tags as `tag`-elements, which in turn contain the `raw` tags that they subsume. The `ratings`-element provides information about the quality of the sound: `webrating` contains the user-rating from Freesound.org, and `clarity` contains the automatically generated clarity rating (based on the clustered tags).
