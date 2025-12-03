from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self, model_name : str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def encode(self, texts : List[str]) -> np.ndarray:
        return self.model.encode(texts, convert_to_numpy=True)

    def encode_one(self, text : str) -> np.ndarray:
        return self.encode([text])[0]


