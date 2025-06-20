import os
import chromadb
from sentence_transformers import SentenceTransformer
import time
from datetime import datetime, timedelta

# Initialize vector store
VECTOR_STORE_DIR = "vector_store"
BACKUP_DIR = "vector_store_backups"
METADATA_FILE = os.path.join(VECTOR_STORE_DIR, "metadata.json")

# Create directories if they don't exist
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)

# Initialize sentence transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create or get collection
collection = client.get_or_create_collection(
    name="sql_queries",
    metadata={"description": "Stored SQL queries and their natural language descriptions"}
)

def test_scenario_1():
    """Test basic query storage and retrieval"""
    print("\nTest Scenario 1: Basic Query Storage and Retrieval")
    
    # Store a test query
    query = "What are the total sales for each product?"
    sql = "SELECT p.PRODUCTNAME, SUM(psd.QUANTITY * psd.SALEPRICE) as total_sales FROM PRODUCT p JOIN PRODUCTSALEDETAIL psd ON p.PRODUCTCODE = psd.PRODUCTCODE GROUP BY p.PRODUCTNAME;"
    
    # Store the query
    collection.add(
        documents=[query],
        metadatas=[{"sql": sql, "timestamp": datetime.now().isoformat()}],
        ids=[str(int(time.time()))]
    )
    
    # Try to retrieve similar query
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    
    print("Stored query:", query)
    print("Retrieved query:", results['documents'][0][0])
    print("Retrieved SQL:", results['metadatas'][0][0]['sql'])
    print("Test passed:", results['documents'][0][0] == query)

def test_scenario_2():
    """Test semantic similarity with different phrasings"""
    print("\nTest Scenario 2: Semantic Similarity")
    
    # Store original query
    original_query = "Show me the sales by product category"
    original_sql = "SELECT c.DESCRIPTIONS as category, SUM(psd.QUANTITY * psd.SALEPRICE) as total_sales FROM CATEGORY c JOIN PRODUCT p ON c.CATEGORYID = p.SUBCATEGORYID JOIN PRODUCTSALEDETAIL psd ON p.PRODUCTCODE = psd.PRODUCTCODE GROUP BY c.DESCRIPTIONS;"
    
    collection.add(
        documents=[original_query],
        metadatas=[{"sql": original_sql, "timestamp": datetime.now().isoformat()}],
        ids=[str(int(time.time()))]
    )
    
    # Try with different phrasing
    similar_query = "What are the total sales grouped by product categories?"
    results = collection.query(
        query_texts=[similar_query],
        n_results=1
    )
    
    print("Original query:", original_query)
    print("Similar query:", similar_query)
    print("Retrieved query:", results['documents'][0][0])
    print("Test passed:", results['documents'][0][0] == original_query)

def test_scenario_3():
    """Test cleanup of old queries"""
    print("\nTest Scenario 3: Cleanup of Old Queries")
    
    # Add an old query
    old_query = "Show old sales data"
    old_sql = "SELECT * FROM PRODUCTSALE WHERE BILLDATE < DATEADD(day, -30, CURRENT_DATE());"
    old_timestamp = (datetime.now() - timedelta(days=31)).isoformat()
    
    collection.add(
        documents=[old_query],
        metadatas=[{"sql": old_sql, "timestamp": old_timestamp}],
        ids=[str(int(time.time()))]
    )
    
    # Add a recent query
    recent_query = "Show recent sales data"
    recent_sql = "SELECT * FROM PRODUCTSALE WHERE BILLDATE >= DATEADD(day, -7, CURRENT_DATE());"
    
    collection.add(
        documents=[recent_query],
        metadatas=[{"sql": recent_sql, "timestamp": datetime.now().isoformat()}],
        ids=[str(int(time.time()))]
    )
    
    # Get all queries
    results = collection.get()
    print("Total queries before cleanup:", len(results['ids']))
    
    # Cleanup old queries (older than 30 days)
    collection.delete(
        where={"timestamp": {"$lt": (datetime.now() - timedelta(days=30)).isoformat()}}
    )
    
    # Get remaining queries
    results = collection.get()
    print("Total queries after cleanup:", len(results['ids']))
    print("Test passed:", len(results['ids']) == 1)

if __name__ == "__main__":
    print("Starting vector store tests...")
    test_scenario_1()
    test_scenario_2()
    test_scenario_3()
    print("\nAll tests completed!") 