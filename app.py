from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests as req
import re
import spacy
import pymorphy3

app = Flask(__name__)

# Initialize models for text processing
nlp = spacy.load('ru_core_news_sm')  # Spacy model for Russian language
morph = pymorphy3.MorphAnalyzer()  # Pymorphy3 morphological analyzer


# Function to scrape text from a URL
def scraping(link):
    head = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.3.949 Yowser/2.5 Safari/537.36'}
    web = req.get(link, headers=head)  # Make an HTTP GET request to the URL
    webSoup = BeautifulSoup(web.text, "html.parser")  # Parse the HTML content
    divs = webSoup.find_all('div', {'class': 'article__text'})  # Extract specific divs containing text
    PremierText = ''
    if divs:
        for div in divs:
            PremierText += div.get_text(separator=" ", strip=True)  # Get the text from the divs
    return PremierText


# Function to remove named entities from the text
def enleverEN(MonPremierText, nlp):
    doc = nlp(MonPremierText)  # Process the text with Spacy
    text_without_ner = ''.join([token.text + ' ' for token in doc if not token.ent_type_])  # Remove named entities
    return text_without_ner


# Function to clean text and split it into unique words
def ponctuation(texte):
    texte = re.sub(r"[\.\!\?\[\],;:'\"1234567890/<>()|©@#$%^&*~`=∞+«»€№_…”“]", " ", texte)  # Remove punctuation
    texte = texte.lower()  # Convert text to lowercase
    texte = re.sub(r"[qwertyuiopasdfghjklzxcvbnm]", "", texte)  # Remove Latin characters
    return set(texte.split())  # Return a set of unique words


# Function to identify neologisms using Pymorphy3
def neologisme(unique_words, morph):
    cleaned_words = [mot.strip('-') for mot in unique_words]  # Remove hyphens at the beginning and end of words
    return [mot for mot in cleaned_words if not morph.word_is_known(mot) and len(mot) > 3]  # Filter unknown words


# Function to filter words using custom dictionaries
def dans_dictionnaire(liste_candidats):
    with open("dictionnaire_version2.txt", "r", encoding="utf-8") as dictionnaire:
        liste_dict = set(dictionnaire.read().split("\n"))  # Load words from the custom dictionary
    with open("surnames_version2.txt", "r", encoding="utf-8") as surnames_file:
        list_names = surnames_file.read().split("\n")  # Load surnames
    return [mot for mot in liste_candidats if mot not in liste_dict and mot not in list_names and len(mot) > 2]  # Filter words


# Main route for the application
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # Handle POST requests
        input_text = request.form.get('text', '')  # Get the input text from the user
        input_url = request.form.get('url', '')  # Get the URL from the user

        MonPremierText = ""
        if input_url:
            MonPremierText = scraping(input_url)  # Scrape text from the provided URL
        elif input_text:
            MonPremierText = input_text  # Use the provided text

        if not MonPremierText:  # If no text is provided, show an error
            return render_template('index.html', error="Please enter text or a URL for analysis.")

        # Process the text
        text_without_ner = enleverEN(MonPremierText, nlp)  # Remove named entities
        unique_words = ponctuation(text_without_ner)  # Clean and tokenize the text
        liste_candidats1 = neologisme(unique_words, morph)  # Identify potential neologisms with Pymorphy
        final_neologisms = dans_dictionnaire(liste_candidats1)  # Filter neologisms through custom dictionaries

        # Return the results as a single list of neologisms
        return render_template(
            'results.html',
            neologisms=final_neologisms,
            input_url=input_url,
            input_text=input_text
        )

    return render_template('index.html')  # Render the main page for GET requests


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode
