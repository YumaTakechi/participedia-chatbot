import os
import pandas as pd
import faiss

from case_embedding import preprocess_text, create_case_embeddings
from topic_modeling import topic_modeling
from faiss_indexing import index_case_embeddings

import nltk

nltk_data_path = os.path.expanduser("~") + "/nltk_data/corpora/stopwords"
if not os.path.exists(nltk_data_path):
        nltk.download("stopwords")

cases_df = pd.read_csv('./cases_original.csv')

case_preprocessed_df, documents = preprocess_text(cases_df)
print('preprocess complete')
case_embeddings = create_case_embeddings(documents)
print('embedding complete')

faiss_file = 'case_index.faiss'
if not os.path.exists(faiss_file):
    faiss_index = index_case_embeddings(case_embeddings)
    faiss.write_index(faiss_index, faiss_file)
else:
    print('faiss index already exists')

case_topics_csv = 'cases_with_topics.csv'
if not os.path.exists(case_topics_csv):
    cases_with_topics_df = topic_modeling(case_preprocessed_df, documents)
    cases_with_topics_df.to_csv('cases_with_topics.csv', index=False)
else:
    print('cases with topics csv already exists')