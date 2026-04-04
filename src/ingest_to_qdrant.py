import os
import glob
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables. Please set it in the .env file.")
    exit(1)

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "knowledge_base"

def main():
    try:
        # 1. Initialize OpenAI Embeddings generator
        logger.info("Initializing OpenAI Embeddings model: text-embedding-3-small")
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", 
            api_key=OPENAI_API_KEY
        )

        # 2. Connect to Qdrant Client
        logger.info(f"Connecting to local Qdrant instance at {QDRANT_URL}")
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

        # 3. Create the collection if it doesn't already exist
        if not client.collection_exists(collection_name=COLLECTION_NAME):
            logger.info(f"Creating collection '{COLLECTION_NAME}' in Qdrant")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                # 1536 is the dimension for text-embedding-3-small
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
        else:
            logger.info(f"Collection '{COLLECTION_NAME}' already exists.")

        # 4. Load Markdown documents from the data/knowledge_base directory
        kb_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base")
        logger.info(f"Looking for Markdown files in: {kb_dir}")
        md_files = glob.glob(os.path.join(kb_dir, "*.md"))
        
        if not md_files:
            logger.warning("No markdown files found. Exiting.")
            return

        logger.info("Splitting documents into chunks using Markdown structure...")
        
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = []
        for file_path in md_files:
            logger.info(f"Loading and splitting document: {os.path.basename(file_path)}")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 1. Split by header
            md_header_splits = markdown_splitter.split_text(content)
            
            # 2. Split further if any section is too long
            file_chunks = text_splitter.split_documents(md_header_splits)
            
            # 3. Inject file path metadata
            for chunk in file_chunks:
                chunk.metadata["source"] = file_path
                chunk.metadata["filename"] = os.path.basename(file_path)
                
            chunks.extend(file_chunks)

        logger.info(f"Generated {len(chunks)} chunks from {len(md_files)} files.")

        # 6. Generate embeddings and Upsert to Qdrant
        logger.info("Generating embeddings and upserting into Qdrant...")
        Qdrant.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=QDRANT_URL,
            collection_name=COLLECTION_NAME,
            api_key=QDRANT_API_KEY,
        )
        logger.info("Ingestion completed successfully!")

    except Exception as e:
        logger.error(f"An error occurred during during ingestion: {e}", exc_info=True)

if __name__ == "__main__":
    main()
