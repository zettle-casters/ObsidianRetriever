from typing import List, Optional
import numpy as np
from langchain_openai import OpenAIEmbeddings

class EmbeddingModel:
    def __init__(
        self,
        model_name: str = "openai/text-embedding-3-large",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> None:
        self.model = OpenAIEmbeddings(
            model=model_name,
            api_key=api_key,
            base_url=base_url
        )

        self.dim = len(self.model.embed_query("test"))

    def encode(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.embed_documents(texts)
        return np.array(embeddings)

    def encode_one(self, text: str) -> np.ndarray:
        embedding = self.model.embed_query(text)
        return np.array([embedding])