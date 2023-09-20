from joblib import load
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import numpy as np
import nltk
import string
from database import ClickhouseData
import pandas as pd

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)


# Define the stop words and lemmatizer
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

#Load the saved model
model = load('ml_model/model_tasks.joblib')


def classify_commit_messages(clickhouse_data):
    
    commit_messages = clickhouse_data.get_commit_messages()

    # Check if there are any commit messages
    if len(commit_messages) == 0:
        print("No commit messages found.")
        return

    # Preprocess the commit messages
    preprocessed_messages = [preprocess_text(msg) for msg in commit_messages]

    # Predict the tasks using the loaded model and get probabilities
    task_probabilities = model.predict_proba(preprocessed_messages)

    # Define the confidence threshold
    confidence_threshold = 0.7

    # For each commit message, get the task with the highest probability
    # Only classify the message if the highest probability is above the threshold
    tasks = [model.classes_[np.argmax(probs)] if np.max(probs) > confidence_threshold else None for probs in task_probabilities]

    # Exclude messages that were not classified (those assigned None)
    tasks = [task for task in tasks if task is not None]
    
    # Generate the task-count dictionary
    task_counts = dict(Counter(tasks))

    # Make sure all task categories are in the dictionary
    all_categories = ['Corrective', 'Adaptive', 'Perfective', 
                      'Implementation', 'Non-functional', 'Other']
    for category in all_categories:
        if category not in task_counts:
            task_counts[category] = 0

    print(list(task_counts.items())[:5]) 
    return task_counts

    

def preprocess_text(text):
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    return ' '.join(tokens)