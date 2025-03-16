import os

from bertopic import BERTopic
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from umap import UMAP

def get_topic_name(topic_id, topic_model):
    if topic_id != -1:
        topic_words = topic_model.get_topic(topic_id)
        if topic_words:
            return ", ".join([word for word, _ in topic_words])
    else:
        return "No Topic"

def topic_modeling(df, documents):

    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.1, metric='cosine', n_jobs=1)
    custom_stop_words = stopwords.words("english")
    vectorizer_model = CountVectorizer(stop_words=custom_stop_words)
    topic_model = BERTopic(umap_model=umap_model, vectorizer_model=vectorizer_model)

    topics, _ = topic_model.fit_transform(documents)
    df['topics'] = topics
    df["topic_names"] = df["topics"].map(lambda x: get_topic_name(x, topic_model))
    return df