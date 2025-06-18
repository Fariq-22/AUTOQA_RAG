from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from config import embedding_model



async def Recursive_chunking(text:str)->list:
    '''
     It will take the extracted text as input
     chunk the text and produce the list with chunks
    '''
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,   
    chunk_overlap=72,
    length_function=len,
    )
    chunked_text = text_splitter.split_text(text)
    return chunked_text


async def get_embeddings(chunked_text:List) -> List:
    embeddings = embedding_model.encode(chunked_text).tolist()
    return embeddings

async def bm25_tonized(chunked_text:List)-> List:
    tokenized_corpus = [chunk.split() for chunk in chunked_text]
    return tokenized_corpus