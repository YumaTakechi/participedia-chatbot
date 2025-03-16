import re
from sentence_transformers import SentenceTransformer


def clean_text(text):
    text = re.sub(r'https?://\S+|[^A-Za-z0-9\s.,?]', '', text).strip().lower()
    return text

def preprocess_text(df):
    df = df.dropna(subset=['body']).fillna('')
    df['text'] = (df['title'] + " - " + df['description'] + " - " + df['body']).apply(clean_text)
    documents = df['text'].tolist()
    return df, documents

def create_case_embeddings(documents: list):
     embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
     embeddings = embedding_model.encode(documents)
     return embeddings