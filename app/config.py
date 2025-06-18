from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer,CrossEncoder

# Load environment variables
load_dotenv()

# Consistent uppercase naming
FIRE_CRAWL_API = os.getenv("FIRE_CRAWL_API")

MILVUS_URI = os.getenv("MILVUS_URI")
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN")

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

