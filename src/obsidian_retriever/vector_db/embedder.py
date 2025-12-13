from typing import List
import numpy as np
from langchain_openai import OpenAIEmbeddings

class EmbeddingModel:
    def __init__(self, model_name: str = "openai/text-embedding-3-large") -> None:
        self.model = OpenAIEmbeddings(
            model=model_name,
            api_key="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",
            base_url="https://openrouter.ai/api/v1"
        )

        self.dim = len(self.model.embed_query("test"))

    def encode(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.embed_documents(texts)
        return np.array(embeddings)

    def encode_one(self, text: str) -> np.ndarray:
        embedding = self.model.embed_query(text)
        return np.array([embedding])