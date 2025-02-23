import faiss
import numpy as np
import pandas as pd
import pickle

class FaissHandlerTest:
    def __init__(self, cases_csv: str = './tests/cases_sample.csv', 
                    faiss_index: str = "./tests/sample_case_index.faiss", 
                    index_to_case: str = "./tests/sample_index_to_case.pkl"):

        #Load original data 
        #TODO: find a better way to access this
        self.cases_df = pd.read_csv(cases_csv)
            
        # Load FAISS index
        self.index = faiss.read_index(faiss_index)
        
        # Load index-to-case mapping
        with open(index_to_case, 'rb') as f:
            self.index_to_case = pickle.load(f)

    def faiss_search(self, query_embedding: np.ndarray, top_n: int):
        """
        Searches the FAISS index for the top n most similar cases to the user query.

        :param query_embedding: np.ndarray, the query embedding
        :param top_n: int, number of top matches to return
        :return: tuple of distances and FAISS indices
        """
        distances, faiss_indices = self.index.search(query_embedding, top_n)
        return distances, faiss_indices

    def format_faiss_results(self, distances: np.ndarray, faiss_indices: np.ndarray):
        """
        Formats the FAISS search results into a list of dictionaries.

        :param distances: np.ndarray, distances from the query to the nearest neighbors
        :param faiss_indices: np.ndarray, indices of the nearest neighbors in the FAISS index
        :return: List of dictionaries containing case information
        """
        results = []

        for i in range(len(faiss_indices[0])):
            faiss_idx = faiss_indices[0][i]
            dist = distances[0][i]
            original_row = self.index_to_case.get(faiss_idx)

            if original_row is not None:
                case_info = {
                    'faiss_index': int(faiss_idx),
                    'distance': float(dist),
                    'case_id': self.cases_df.at[original_row, 'id'],
                    'title': self.cases_df.at[original_row, 'title'],
                    'url': self.cases_df.at[original_row, 'url']
                }
                results.append(case_info)

        return results


    def retrieve_cases(self, query_embedding: np.ndarray, top_n):
        """
        Performs a FAISS search and returns formatted results.

        :param query_embedding: np.ndarray, query embedding
        :param top_n: int, number of results
        :return: List of case dictionaries
        """
        distances, faiss_indices = self.faiss_search(query_embedding, top_n)
        retrieved_cases = self.format_faiss_results(distances, faiss_indices)
        return retrieved_cases