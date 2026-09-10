"""FAISS vector baseline and BM25 fusion over exactly the graph's evidence corpus.

Every recorded relationship is already expressed in source text. Unlike the
reference's node-only baseline, neither retriever receives exclusive facts.
"""
from __future__ import annotations

from collections import Counter
import math
import re
import faiss
import numpy as np

from graph_builder import eligible_documents


class VectorRAG:
    def __init__(self, corpus):
        self.corpus = corpus
        embedding = corpus["embedding"]
        self.vocab = {word: i for i, word in enumerate(embedding["vocab"])}
        self.stop = set(embedding["stop_words"])
        self.idf = np.asarray(embedding["idf"], dtype=np.float32)
        self.projection = np.asarray(embedding["projection"], dtype=np.float32)
        self.chunks = corpus["chunks"]
        self.vectors = np.asarray([chunk["vector"] for chunk in self.chunks], dtype=np.float32)

    def tokens(self, text):
        return [word for word in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())
                if word not in self.stop and len(word) > 1]

    def embed(self, text):
        vector = np.zeros(len(self.vocab), dtype=np.float32)
        for word, count in Counter(self.tokens(text)).items():
            if word in self.vocab:
                vector[self.vocab[word]] = (1 + math.log(count)) * self.idf[self.vocab[word]]
        dense = vector @ self.projection.T
        return dense / max(float(np.linalg.norm(dense)), 1e-12)

    def search(self, question, options, strategy="vector", documents=None):
        allowed = documents if documents is not None else eligible_documents(self.corpus, options)
        indexes = [i for i, chunk in enumerate(self.chunks) if chunk["id"] in allowed]
        if not indexes:
            return []
        # Restrict before search, not top-k then post-filter. No index is shared
        # between principals; only immutable source arrays are cached.
        index = faiss.IndexFlatIP(self.vectors.shape[1])
        index.add(np.ascontiguousarray(self.vectors[indexes]))
        scores, order = index.search(self.embed(question).reshape(1, -1), len(indexes))
        dense = {indexes[int(local)]: float(score) for local, score in zip(order[0], scores[0])}
        terms = set(self.tokens(question))
        average = sum(self.chunks[i]["length"] for i in indexes) / len(indexes)
        df = Counter(word for i in indexes for word in self.chunks[i]["terms"])
        sparse = {}
        coverage = {}
        for i in indexes:
            chunk = self.chunks[i]
            coverage[i] = len(terms & chunk["terms"].keys()) / max(1, len(terms))
            sparse[i] = sum(
                math.log(1 + (len(indexes) - df[word] + .5) / (df[word] + .5))
                * chunk["terms"].get(word, 0) * 2.2
                / (chunk["terms"].get(word, 0) + 1.2 * (.25 + .75 * chunk["length"] / max(average, 1)))
                for word in terms
            )
        dense_rank = {i: rank for rank, i in enumerate(sorted(indexes, key=lambda i: (-dense[i], i)), 1)}
        sparse_rank = {i: rank for rank, i in enumerate(sorted(indexes, key=lambda i: (-sparse[i], i)), 1)}
        results = []
        for i in indexes:
            score = dense[i] if strategy == "vector" else 1/(60+dense_rank[i]) + 1/(60+sparse_rank[i])
            results.append({"chunk": self.chunks[i], "score": score, "dense": dense[i],
                            "sparse": sparse[i], "coverage": coverage[i]})
        return sorted(results, key=lambda row: (-row["score"], row["chunk"]["chunk_id"]))

    def answer(self, question, options=None):
        from graph_rag import GraphRAG
        from settings import QueryOptions
        return GraphRAG(self.corpus, vectors=self).answer(question, options or QueryOptions(), "vector")
