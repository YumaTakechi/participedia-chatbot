import os

import pandas as pd
from case_embedding import preprocess_text, create_embedding, topic_modeling, index_embeddings
from sentence_transformers import SentenceTransformer
import faiss
   
def main(df):
    case_preprocessed_df, documents = preprocess_text(df)
    case_embeddings = create_embedding(documents)
    case_topics_df = topic_modeling(case_preprocessed_df, documents)
    faiss_index = index_embeddings(case_embeddings)
    return case_topics_df, faiss_index

case_df = pd.read_csv('cases.csv')
case_topics_df, faiss_index = main(case_df)


faiss_index_file = "case_index.faiss"
if not os.path.exists(faiss_index_file):
    faiss.write_index(faiss_index, "case_index.faiss")
else:
    print('faiss index already exists')

