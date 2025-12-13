from typing import List
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingModel:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model = HuggingFaceEmbeddings(model_name=model_name, cache_folder='./hf-cache/')
        self.dim = len(self.model.embed_query("test"))

    def encode(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.embed_documents(texts)
        return np.array(embeddings)

    def encode_one(self, text: str) -> np.ndarray:
        embedding = self.model.embed_query(text)
        return np.array(embedding)