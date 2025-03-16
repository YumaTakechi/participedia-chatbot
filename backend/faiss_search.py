import numpy as np
from fastapi.encoders import jsonable_encoder

def faiss_search(query_embedding, top_n, faiss_index):
    _, faiss_indices = faiss_index.search(query_embedding, top_n)
    # faiss_indices = faiss_indices.astype(int).tolist()
    return faiss_indices

def format_faiss_results(faiss_indices, df):
    results = []
    
    if len(faiss_indices) == 0 or len(faiss_indices[0]) == 0:
        return results 
    
    for index in faiss_indices[0]:
        if 0 <= index < len(df):  
            case = df.iloc[index]
            case_info = {
                'case_id': case['id'].item(),
                'title': case['title'],
                'url': case['url'],
                'topic_names': case['topic_names']
            }
            results.append(case_info)

    return results

