import faiss
import numpy as np
import pandas as pd
import pickle


def faiss_search(query_embedding: np.ndarray, top_n: int, faiss_index):
    return faiss_index.search(query_embedding, top_n)

def format_faiss_results(faiss_indices, df):
    results = []
    
    if len(faiss_indices) == 0 or len(faiss_indices[0]) == 0:
        return results 

    for idx in faiss_indices[0]:
        if 0 <= idx < len(df): 
            case = df.iloc[idx]
            case_info = {
                'case_id': case['id'],
                'title': case['title'],
                'url': case['url'],
                'topic_names': case['topic_names']
            }
            results.append(case_info)

        return results

