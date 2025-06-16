from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Consistent uppercase naming
FIRE_CRAWL_API = os.getenv("FIRE_CRAWL_API")

MILVUS_URI = os.getenv("MILVUS_URI")
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN")



