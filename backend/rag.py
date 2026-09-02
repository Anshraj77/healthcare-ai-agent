import os
import numpy as np
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")

class RAGSystem:

    def __init__(self):
        print("Loading embedding model...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.chunks = []
        self.embeddings = None

        self.load_knowledge_base()

    def load_knowledge_base(self):

        file_path = "knowledge_base/clinic_info.txt"

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Knowledge base not found: {file_path}"
            )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

        self.chunks = self.chunk_text(text)

        self.embeddings = self.model.encode(
            self.chunks,
            convert_to_numpy=True
        )

        print(
            f"Knowledge base loaded with {len(self.chunks)} chunks"
        )

    def chunk_text(
        self,
        text,
        chunk_size=500,
        overlap=100
    ):

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    def retrieve(
        self,
        query,
        top_k=3
    ):

        query_embedding = self.model.encode(
            query,
            convert_to_numpy=True
        )

        similarities = self.cosine_similarity(
            query_embedding,
            self.embeddings
        )

        top_indices = np.argsort(
            similarities
        )[-top_k:][::-1]

        results = []

        for index in top_indices:

            results.append({
                "text": self.chunks[index],
                "score": float(similarities[index])
            })

        return results

    def cosine_similarity(
        self,
        query_embedding,
        document_embeddings
    ):

        query_norm = np.linalg.norm(query_embedding)

        document_norms = np.linalg.norm(
            document_embeddings,
            axis=1
        )

        denominator = (
            document_norms * query_norm
        )

        denominator = np.where(
            denominator == 0,
            1e-10,
            denominator
        )

        similarities = np.dot(
            document_embeddings,
            query_embedding
        ) / denominator

        return similarities