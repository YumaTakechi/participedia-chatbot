import numpy as np


def faiss_search(query_embedding, top_n, faiss_index):
    query_embedding = np.array(query_embedding)
    _, faiss_indices = faiss_index.search(query_embedding, top_n)
    faiss_indices = faiss_indices.astype(int).tolist()
    return faiss_indices

def format_faiss_results(faiss_indices, df):
    results = []
    
    if len(faiss_indices) == 0 or len(faiss_indices[0]) == 0:
        return results 
    
    for index in faiss_indices[0]:
        index = int(index)
        if 0 <= index < len(df):  
            case = df.iloc[index]
            case_info = {
                'case_id': case['id'],
                'title': case['title'],
                'url': case['url'],
                'topic_names': case['topic_names']
            }
            results.append(case_info)

    return results 

