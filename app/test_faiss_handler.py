import faiss
import numpy as np
import pandas as pd
import pickle
import os

class FaissHandlerTest:
    def __init__(self, 
                 cases_csv: str = None, 
                 faiss_index: str = None, 
                 index_to_case: str = None):
        """
        Initialize the FaissHandlerTest class.

        :param cases_csv: Path to the CSV file containing case data.
        :param faiss_index: Path to the FAISS index file.
        :param index_to_case: Path to the index-to-case mapping pickle file.
        """
        # Set default paths relative to the project's root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

        if cases_csv is None:
            cases_csv = os.path.join(project_root, 'perticipedia-chatbot-main/tests/cases_sample.csv')
        if faiss_index is None:
            faiss_index = os.path.join(project_root, 'perticipedia-chatbot-main/tests/sample_case_index.faiss')
        if index_to_case is None:
            index_to_case = os.path.join(project_root, 'perticipedia-chatbot-main/tests/sample_index_to_case.pkl')

        # Debugging: Print the resolved paths
        print(f"Resolved cases_csv path: {cases_csv}")
        print(f"Resolved faiss_index path: {faiss_index}")
        print(f"Resolved index_to_case path: {index_to_case}")

        # Check if files exist
        if not os.path.exists(cases_csv):
            raise FileNotFoundError(f"❌ File not found: {cases_csv}")
        if not os.path.exists(faiss_index):
            raise FileNotFoundError(f"❌ File not found: {faiss_index}")
        if not os.path.exists(index_to_case):
            raise FileNotFoundError(f"❌ File not found: {index_to_case}")

        # Load original data
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
                    'faiss_index': int(faiss_idx),  # Ensure int type
                        'distance': float(dist),       # Ensure float type
                    'case_id': int(self.cases_df.at[original_row, 'id']),  # Convert np.int64 to int
                    'title': self.cases_df.at[original_row, 'title'],
                    'url': self.cases_df.at[original_row, 'url']
                }
                results.append(case_info)

        return results

    def retrieve_cases(self, query_embedding: np.ndarray, top_n: int):
        """
        Performs a FAISS search and returns formatted results.

        :param query_embedding: np.ndarray, query embedding
        :param top_n: int, number of results
        :return: List of case dictionaries
        """
        distances, faiss_indices = self.faiss_search(query_embedding, top_n)
        retrieved_cases = self.format_faiss_results(distances, faiss_indices)
        print("THESE ARE THE RESULTS", retrieved_cases)
        return retrieved_cases