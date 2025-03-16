import faiss

def index_case_embeddings(case_embeddings):
    embedding_dimension = case_embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(embedding_dimension)
    faiss_index.add(case_embeddings)
    return faiss_index
