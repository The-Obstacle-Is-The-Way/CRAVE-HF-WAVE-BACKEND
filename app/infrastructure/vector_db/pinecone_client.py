# pinecone_client.py
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from app.config.settings import Settings

settings = Settings()

def init_pinecone():
   pc = Pinecone(api_key=settings.PINECONE_API_KEY)
   return pc

pc = init_pinecone()
index_name = settings.PINECONE_INDEX_NAME
if index_name not in pc.list_indexes().names():
   pc.create_index(
       name=index_name,
       dimension=1536,
       metric="cosine",
       spec=ServerlessSpec(
           cloud="aws",
           region="us-east-1"
       )
   )
   print(f"Index '{index_name}' created as serverless index.")
else:
   print(f"Index '{index_name}' already exists.")

def get_pinecone_index(index_name: str):
   return pc.Index(index_name)