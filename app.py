from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests as req
import re
import spacy
import pymorphy3
import csv

app = Flask(__name__)

# Initialize models
nlp = spacy.load('ru_core_news_sm')  # Load Spacy model for Russian language
morph = pymorphy3.MorphAnalyzer()   # Initialize Pymorphy3 morphological analyzer

# Function to scrape text from a webpage
def scraping(link):
    head = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.3.949 Yowser/2.5 Safari/537.36'}
    web = req.get(link, headers=head)  # Send GET request to the URL
    webSoup = BeautifulSoup(web.text, "html.parser")  # Parse the webpage content
    divs = webSoup.find_all('div', {'class': 'article__text'})  # Find text in specific divs
    PremierText = ''
    if divs:
        for div in divs:
            PremierText += div.get_text(separator=" ", strip=True)  # Extract text from divs
    return PremierText

# Function to remove named entities from the text
def enleverEN(MonPremierText, nlp):
    doc = nlp(MonPremierText)  # Process text with Spacy
    text_without_ner = ''.join([token.text + ' ' for token in doc if not token.ent_type_])  # Keep tokens without named entities
    return text_without_ner

# Function to clean text and split it into unique words
def ponctuation(texte):
    texte = re.sub(r"[\.\!\?\[\],;:'\"1234567890/<>()|©@#$%^&*~`=∞+«»€№_…”“]", " ", texte)  # Remove punctuation and special symbols
    texte = texte.lower()  # Convert text to lowercase
    texte = re.sub(r"[qwertyuiopasdfghjklzxcvbnm]", "", texte)  # Remove Latin letters
    return set(texte.split())  # Split text into unique words

# Function to identify neologisms using Pymorphy3
def neologisme(unique_words, morph):
    cleaned_words = [mot.strip('-') for mot in unique_words]  # Remove hyphens at the beginning and end of words
    return [mot for mot in cleaned_words if not morph.word_is_known(mot) and len(mot) > 3]  # Filter unknown words longer than 3 characters

# Function to filter words using custom dictionaries
def dans_dictionnaire(liste_candidats):
    with open("dictionnaire_version2.txt", "r", encoding="utf-8") as dictionnaire:
        liste_dict = set(dictionnaire.read().split("\n"))  # Load custom dictionary
    with open("surnames_version2.txt", "r", encoding="utf-8") as surnames_file:
        list_names = surnames_file.read().split("\n")  # Load surnames
    return [mot for mot in liste_candidats if mot not in liste_dict and mot not in list_names and len(mot) > 2]  # Filter words not in dictionaries

# Function to find context sentences for neologisms
def Contexte(liste_candidats3, MonPremierText, nlp):
    neologism_sentences = []
    doc = nlp(MonPremierText)  # Process text with Spacy
    for mot in liste_candidats3:
        for sent in doc.sents:  # Iterate through sentences
            if mot in sent.text.lower():  # Check if the word is in the sentence
                neologism_sentences.append((mot, sent.text))  # Store the word and its context
    return neologism_sentences

# Flask route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form.get('text', '')  # Get user input text
        input_url = request.form.get('url', '')   # Get user input URL

        MonPremierText = ""
        if input_url:
            MonPremierText = scraping(input_url)  # Scrape text from the URL
        elif input_text:
            MonPremierText = input_text  # Use input text

        if not MonPremierText:  # If no text is provided, show an error
            return render_template('index.html', error="Enter text or a URL for analysis.")

        # Text analysis
        text_without_ner = enleverEN(MonPremierText, nlp)  # Remove named entities
        unique_words = ponctuation(text_without_ner)  # Extract unique words
        liste_candidats1 = neologisme(unique_words, morph)  # Identify neologisms
        liste_candidats2 = dans_dictionnaire(liste_candidats1)  # Filter using dictionaries
        neologism_sentences_list = Contexte(liste_candidats2, MonPremierText, nlp)  # Find contexts

        # Return results
        return render_template(
            'results.html',
            candidats_pymorphy=liste_candidats1,
            candidats_dict=liste_candidats2,
            contexts=neologism_sentences_list,
            input_url=input_url,
            input_text=input_text
        )

    return render_template('index.html')  # Render the main page

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode
