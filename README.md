# AUTOQA_RAG

rag_api/
├── .env                   
├── requirements.txt      python-dotenv
├── docker-compose.yml     # Milvus service definition
└── app/
    ├── main.py            # FastAPI app entrypoint, include routers
    ├── config.py          # Load .env & constants
    ├── routers/           # HTTP endpoints
    │   ├── db.py          # POST /databases, GET /databases
    │   ├── coll.py        # POST /collections, GET /collections/
    │   └── search.py      # GET /search?q=&database=&
    ├── services/         # Business logic
    │   ├── milvus_client.py   # get_milvus_client()
    │   ├── db.py              # create_database(), 
    │   ├── collection.py      # create_collection(), 
    │   ├── data.py            # insert_data_to_collection()
    │   └── retrieve.py        # hybrid_search()
    └── utils/            # Scraper & preprocessing
        ├── scraper.py       # crawl_website()
        ├── extractor.py     # extract_pages_to_json(), 
        ├── chunker.py       # Recursive_chunking()
        └── embedder.py      # get_embeddings(), bm25_tokenize()