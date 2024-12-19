from typing import List

import re
import string
import nltk
import zipfile
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def download_nltk_package(package_name, resource_name=None):
    """
    Verifies presence of local nltk package before download attempt
    for optimization. If the package is a ZIP file, it will be extracted
    to the same directory as the ZIP file.
    """

    if resource_name is None:
        resource_name = package_name
    try:
        nltk.data.find(resource_name)
    except LookupError:
        nltk.download(package_name)
        try:
            nltk.data.find(resource_name)
        except LookupError:
            for ntlk_path in nltk.data.path:
                try:
                    zip_file_path = ntlk_path+'/'+resource_name+'.zip'
                
                    # Extract to the same directory as the zip file
                    extract_to = os.path.dirname(zip_file_path)
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_to)

                except Exception:
                    continue

def clean_string(text: str, stop_words_filter: List = []) -> str:
    """
    Returns a NLP cleaned version of an input string
    """

    download_nltk_package('punkt', 'tokenizers/punkt')
    download_nltk_package('stopwords', 'corpora/stopwords')
    download_nltk_package('wordnet', 'corpora/wordnet')

    # Lowercase the text
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove special characters and digits
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'\W', ' ', text)
    
    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    
    stop_words = set(stopwords.words('english')) - set(stop_words_filter)
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatize the text
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    # Join the tokens back into a single string
    cleaned_text = ' '.join(tokens)
    
    return cleaned_text
