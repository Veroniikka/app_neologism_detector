# Russian Neologism Detector
## Russian Neologism Detector is a web application designed to analyze Russian texts and detect neologisms — new or unique words that may not yet be widely recognized. 
## The app allows users to input text or provide a URL to analyze and returns a list of potential neologisms with their context.


### How It Works
#### Input Options: 
Users can input text directly or provide a URL.
#### Text Cleaning: 
The app processes the text by removing named entities, punctuation, and non-Cyrillic characters.
#### Neologism Detection:
Words are checked against the morphological database (pymorphy3).
Words are filtered using custom dictionaries to exclude common or irrelevant terms.
#### Context Analysis: 
Sentences containing potential neologisms are extracted and displayed.

URL of the site deployed on Render:
https://russian-neologism-detector.onrender.com/
