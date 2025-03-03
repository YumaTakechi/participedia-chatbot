import os
import re

from bertopic import BERTopic
import faiss
import nltk
from nltk.corpus import stopwords
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from umap import UMAP


nltk_data_path = os.path.expanduser("~") + "/nltk_data/corpora/stopwords"
if not os.path.exists(nltk_data_path):
    nltk.download("stopwords")


umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.1, metric='cosine')
custom_stop_words = stopwords.words("english")
vectorizer_model = vectorizer_model = CountVectorizer(stop_words=custom_stop_words)
topic_model = BERTopic(umap_model=umap_model, vectorizer_model=vectorizer_model)


def clean_text(text):
    text = re.sub(r'https?://\S+ | [^A-Za-z0-9\s.,?]', '', text)
    return text.strip().lower() 

def preprocess_text(df):
    df = df.dropna(subset=['body']).fillna('')
    df['text'] = df['title'] + " - " + df['description'] + " - " + df['body']
    df['text'] = df['text'].apply(clean_text)
    documents = df['text'].tolist()
    return df, documents

def get_topic_name(topic_id):
    if topic_id != -1:
        return topic_model.get_topic(topic_id) 
    else: 
        return "No Topic"

def create_embedding(documents):
     embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
     return embedding_model.encode(documents)


def topic_modeling(df, documents):
    topics, probs = topic_model.fit_transform(documents)
    df['topic'] = topics
    df['topic_name'] = df['topic'].apply(get_topic_name)
    return df

def index_embeddings(case_embeddings):
    embedding_dimension = case_embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(embedding_dimension)
    faiss_index.add(case_embeddings)
    return faiss_index


