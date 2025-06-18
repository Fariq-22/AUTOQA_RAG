from typing import List,Tuple
from rank_bm25 import BM25Okapi
import json

from services.milvus_client import get_milvus_client
from config import embedding_model,cross_encoder


# --- Vector search with correct API usage ---
async def vector_search(databasename:str,collection: str, query: str, top_k: int = 5, ef: int = 200) -> List:
    milvus_client = await get_milvus_client(db_name=databasename)
    q_emb = embedding_model.encode([query]).tolist()[0]
    results = milvus_client.search(
        collection_name=collection,
        anns_field="embedding",
        data=[q_emb],
        limit=top_k,
        search_params={"metric_type": "COSINE", "params": {"ef": ef}},
        output_fields=["text"]
    )
    # results is List[List[dict]]
    candidates = []
    for hits in results:
        for hit in hits:
            candidates.append((hit["entity"]["text"], hit["distance"]))
    return candidates



async def keyword_search(query: str, texts: List[str], token_corpus: List[List[str]], top_k: int = 5):
    bm25 = BM25Okapi(token_corpus)
    scores = bm25.get_scores(query.split())
    ranked = sorted(zip(texts, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


# --- Pagination fetch ---
async def fetch_all_docs(database:str,collection: str, batch_size: int = 500) -> Tuple[List[str], List[List[str]]]:
    docs = []
    offset = 0
    milvus_client = await get_milvus_client(db_name=database)
    while True:
        rows = milvus_client.query(
            collection_name=collection,
            filter="",
            output_fields=["text", "keyword_text"],
            limit=batch_size,
            offset=offset
        )
        if not rows:
            break
        docs.extend(rows)
        offset += len(rows)
        if len(rows) < batch_size:
            break

    texts, tokens = [], []
    for row in docs:
        texts.append(row["text"])
        kt = row["keyword_text"]
        if isinstance(kt, str):
            try:
                kt = json.loads(kt)
            except:
                kt = kt.split()
        tokens.append(kt)
    return texts, tokens



# --- Hybrid retrieval with reranking ---
async def hybrid_retrieve(databasename:str,collection_name: str, query: str, top_k: int = 5):

    texts, tokens = await fetch_all_docs(database=databasename,collection=collection_name)

    kw = await keyword_search(query, texts, tokens, top_k)
    vec = await vector_search(databasename=databasename,collection=collection_name,query=query)

    seen = set(); candidates = []
    for txt, _ in kw + vec:
        if txt not in seen:
            seen.add(txt)
            candidates.append(txt)

    pairs = [(query, txt) for txt in candidates]
    ce_scores = cross_encoder.predict(pairs)

    reranked = sorted(zip(candidates, ce_scores), key=lambda x: x[1], reverse=True)
    return [(text) for text, _ in reranked[:top_k]]

