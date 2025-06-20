from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer,CrossEncoder
from pymilvus import MilvusClient

# Load environment variables
load_dotenv()

# Consistent uppercase naming
FIRE_CRAWL_API = os.getenv("FIRE_CRAWL_API")



MILVUS_URI = os.getenv("MILVUS_URI")
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN")

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_GENERATION = os.getenv("GEMINI_MODEL_GENERATION")
GEMINI_MODEL_Query = os.getenv("GEMINI_MODEL_Query")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

DB_Name = os.getenv("DB_NAME")


MONGODB_URI = os.getenv("MONGO_DB_URI")
MONGODB_NAME = os.getenv("DATABASE_NAME")

milvus_client=MilvusClient(uri=MILVUS_URI, token=MILVUS_TOKEN, db_name=DB_Name)

