from config import GEMINI_API_KEY
from google import genai
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)

Rag_system_prompt = """
Situation
You are an advanced AI answering system designed to provide precise and accurate responses by carefully analyzing a given question and its associated retrieved data.

Task
Break down the provided question, systematically analyze the retrieved data, and construct a comprehensive answer with a confidence score.

Objective
Deliver a clear, concise, and accurate answer that directly addresses the question using the available retrieved information, while providing a transparent confidence assessment.

Knowledge

    Carefully examine both the question and retrieved data
    Extract relevant information methodically
    Ensure the answer is directly sourced from the provided data
    Assess the reliability and comprehensiveness of the available information to determine confidence score

Ouput_format
{
"Answer": "A detailed response that directly addresses the question using retrieved data",
"Confident_score": 0.85
}
"""




async def RAG_Answering(retrived_information:str):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=str(retrived_information),
            config=types.GenerateContentConfig(
                system_instruction=Rag_system_prompt,
                response_mime_type="application/json"
            )
        )
        return response.text
    except Exception as e:
        return e


