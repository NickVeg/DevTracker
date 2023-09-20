from github_api_handler import GithubAPIHandler
import re
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from joblib import load
import os

# Ensure necessary NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)


#Load the saved model
model = load('ml_model/model_roles.joblib')

def predict_job_role(author_name):
    token = os.getenv('GITHUB_TOKEN')
    handler = GithubAPIHandler(token)
    author_repos = handler.get_author_repo_info(author_name)

    # fill NaN values with empty strings
    author_repos['repo_name'] = author_repos['repo_name'].fillna('')
    author_repos['description'] = author_repos['description'].fillna('')
    author_repos['readme_text'] = author_repos['readme_text'].fillna('')
    author_repos['repo_tags'] = author_repos['repo_tags'].fillna('')
    
    full_text = ' '.join(author_repos['repo_name'] + ' ' + author_repos['description'] + ' ' + author_repos['readme_text'])

    full_text = clean_text(full_text)
    predicted_role = model.predict([full_text])[0]

    return predicted_role
# The code above first concatenates the information from all repositories 
# and then predicts the job role based on this concatenated information. 
# It returns a single job role.


def clean_text(text):
    # Convert text to lowercase
    text = text.lower()
    
    # Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove special characters except '-' and '_'
    text = re.sub(r'[^a-zA-Z0-9\s\-_]', '', text)
    
    # Remove stop words
    stop_words = stopwords.words('english')
    words = nltk.word_tokenize(text)
    words = [word for word in words if word not in stop_words]
    
    # Lemmatize words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    
    # Join words back into a string
    text = ' '.join(words)
    return text