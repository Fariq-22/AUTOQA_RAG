from config import GEMINI_API_KEY,GEMINI_MODEL_GENERATION,GEMINI_MODEL_Query
from google import genai
from google.genai import types
import json
from typing import List,Dict

client = genai.Client(api_key=GEMINI_API_KEY)

Rag_system_prompt = """
Situation
You are an advanced AI answering system integrated into a RAG modeule designed to provide precise and accurate responses by carefully analyzing a given question and its associated retrieved data.

Task
Break down the provided question, systematically analyze the retrieved data, and construct a comprehensive answer with a confidence score.

Objective
Deliver a clear, concise, and accurate answer that directly addresses the question using the available retrieved information, while providing a transparent confidence assessment.

Knowledge

    Carefully examine both the question and retrieved data
    Extract relevant information methodically
    Ensure the answer is directly sourced from the provided data
    Assess the reliability and comprehensiveness of the available information to determine confidence score 
    It may be possible that the query is outside the scope of the retrieved data, in which case you must reply saying out of scope in natural language

Ouput_format
{
"Answer": "A detailed response that directly addresses the question using retrieved data",
"Confident_score": 0.85
}
"""

Subquery_prompt = '''
You are a query generator. Given a user question, generate exactly five concise, related search queries that explore different facets of the original question. Output as a JSON array of strings.
'''



async def RAG_Answering(retrived_information:str):
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_GENERATION,
            contents=retrived_information,
            config=types.GenerateContentConfig(
                system_instruction=Rag_system_prompt,
                response_mime_type="application/json"
            )
        )
        return response.text
    except Exception as e:
        return e


async def generate_subqueries(query: str) -> List[str]:
    payload = client.models.generate_content(
        model=GEMINI_MODEL_Query,
        contents=query,
        config=types.GenerateContentConfig(
            system_instruction=Subquery_prompt,
            response_mime_type="application/json"
        )
    )
    try:
        subqs = json.loads(payload.text)
        if not isinstance(subqs, list) or len(subqs) != 5:
            raise ValueError("Invalid subqueries format")
        return subqs
    except Exception as e:
        return e