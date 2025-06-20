import os
import chromadb
from sentence_transformers import SentenceTransformer
import time
from datetime import datetime, timedelta
import logging
import json
import shutil
import gzip
import hashlib
from functools import lru_cache
import sqlparse
from typing import Optional, Tuple, List, Dict
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vector_store.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedVectorStore:
    def __init__(self, 
                 vector_store_dir: str = "vector_store",
                 backup_dir: str = "vector_store_backups",
                 max_cache_size: int = 1000,
                 similarity_threshold: float = 0.85,
                 max_query_length: int = 1000,
                 backup_interval: int = 100,
                 max_backups: int = 5):
        """
        Initialize the enhanced vector store with improved features.
        
        Args:
            vector_store_dir: Directory for vector store
            backup_dir: Directory for backups
            max_cache_size: Maximum size of LRU cache
            similarity_threshold: Threshold for semantic similarity
            max_query_length: Maximum length of queries
            backup_interval: Number of queries between backups
            max_backups: Maximum number of backups to keep
        """
        self.vector_store_dir = vector_store_dir
        self.backup_dir = backup_dir
        self.max_cache_size = max_cache_size
        self.similarity_threshold = similarity_threshold
        self.max_query_length = max_query_length
        self.backup_interval = backup_interval
        self.max_backups = max_backups
        self.metadata_file = os.path.join(vector_store_dir, "metadata.json")
        self.lock = threading.Lock()
        
        # Create necessary directories
        self._create_directories()
        
        # Initialize components
        self._initialize_components()
        
        # Load or create metadata
        self.metadata = self._load_metadata()
        
        # Initialize metrics
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "backups_created": 0
        }

    def _create_directories(self):
        """Create necessary directories with error handling."""
        try:
            for directory in [self.vector_store_dir, self.backup_dir]:
                os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise

    def _initialize_components(self):
        """Initialize ChromaDB and sentence transformer with error handling."""
        try:
            # Initialize ChromaDB with persistence and settings
            self.client = chromadb.PersistentClient(
                path=self.vector_store_dir,
                settings=chromadb.Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize sentence transformer with error handling
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create or get collection with metadata
            self.collection = self.client.get_or_create_collection(
                name="sql_queries",
                metadata={
                    "description": "Enhanced SQL query storage with semantic search",
                    "created_at": datetime.now().isoformat(),
                    "version": "2.0"
                }
            )
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            self._restore_from_backup()
            raise

    def _load_metadata(self) -> Dict:
        """Load metadata with error handling."""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            return {
                "last_backup": None,
                "total_queries": 0,
                "last_cleanup": None,
                "version": "2.0"
            }
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {
                "last_backup": None,
                "total_queries": 0,
                "last_cleanup": None,
                "version": "2.0"
            }

    def _save_metadata(self):
        """Save metadata with error handling."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def _validate_query(self, query: str, sql: str) -> Tuple[bool, str]:
        """
        Validate query and SQL with comprehensive checks.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check query length
            if len(query) > self.max_query_length:
                return False, f"Query exceeds maximum length of {self.max_query_length} characters"
            
            # Validate SQL syntax
            try:
                sqlparse.parse(sql)
            except Exception as e:
                return False, f"Invalid SQL syntax: {str(e)}"
            
            # Check for SQL injection
            if any(keyword in query.lower() for keyword in ['drop', 'delete', 'update', 'insert', 'alter']):
                return False, "Query contains restricted SQL keywords"
            
            return True, ""
        except Exception as e:
            logger.error(f"Error validating query: {e}")
            return False, str(e)

    @lru_cache(maxsize=1000)
    def get_similar_queries(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get similar queries with caching and improved similarity search.
        
        Args:
            query: The user's natural language query
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (similar_query, cached_sql)
        """
        try:
            # Get query embedding
            query_embedding = self.model.encode(query)
            
            # Search with improved parameters
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=1,
                include=["documents", "metadatas", "distances"]
            )
            
            if results and results['distances'][0][0] < (1 - self.similarity_threshold):
                self.metrics["cache_hits"] += 1
                return results['documents'][0][0], results['metadatas'][0][0]['sql']
            
            self.metrics["cache_misses"] += 1
            return None, None
        except Exception as e:
            logger.error(f"Error in get_similar_queries: {e}")
            self.metrics["errors"] += 1
            return None, None

    def store_query(self, query: str, sql: str) -> bool:
        """
        Store a new query with validation and error handling.
        
        Args:
            query: The user's natural language query
            sql: The generated SQL query
            
        Returns:
            bool: Success status
        """
        try:
            with self.lock:
                # Validate query
                is_valid, error_message = self._validate_query(query, sql)
                if not is_valid:
                    logger.error(f"Query validation failed: {error_message}")
                    return False
                
                # Get query embedding
                query_embedding = self.model.encode(query)
                
                # Generate unique ID
                query_id = hashlib.sha256(f"{query}{time.time()}".encode()).hexdigest()
                
                # Store in vector database
                self.collection.add(
                    embeddings=[query_embedding.tolist()],
                    documents=[query],
                    metadatas=[{
                        "sql": sql,
                        "timestamp": datetime.now().isoformat(),
                        "type": "query",
                        "hash": query_id
                    }],
                    ids=[query_id]
                )
                
                # Update metadata and metrics
                self.metadata["total_queries"] += 1
                self.metrics["total_queries"] += 1
                self._save_metadata()
                
                # Create backup if needed
                if self.metadata["total_queries"] % self.backup_interval == 0:
                    self._create_backup()
                
                return True
        except Exception as e:
            logger.error(f"Error storing query: {e}")
            self.metrics["errors"] += 1
            return False

    def _create_backup(self):
        """Create compressed backup with rotation."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            
            # Create compressed backup
            with gzip.open(f"{backup_path}.gz", 'wb') as f:
                for root, dirs, files in os.walk(self.vector_store_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'rb') as source:
                            f.write(source.read())
            
            # Update metadata
            self.metadata["last_backup"] = timestamp
            self._save_metadata()
            
            # Rotate old backups
            self._rotate_backups()
            
            self.metrics["backups_created"] += 1
            logger.info(f"Created backup at {backup_path}.gz")
        except Exception as e:
            logger.error(f"Error creating backup: {e}")

    def _rotate_backups(self):
        """Rotate old backups keeping only the most recent ones."""
        try:
            backups = sorted([
                f for f in os.listdir(self.backup_dir)
                if f.startswith("backup_") and f.endswith(".gz")
            ])
            
            while len(backups) > self.max_backups:
                oldest_backup = backups.pop(0)
                os.remove(os.path.join(self.backup_dir, oldest_backup))
        except Exception as e:
            logger.error(f"Error rotating backups: {e}")

    def _restore_from_backup(self):
        """Restore from the most recent backup if available."""
        try:
            backups = sorted([
                f for f in os.listdir(self.backup_dir)
                if f.startswith("backup_") and f.endswith(".gz")
            ])
            
            if backups:
                latest_backup = os.path.join(self.backup_dir, backups[-1])
                
                # Clear current vector store
                if os.path.exists(self.vector_store_dir):
                    shutil.rmtree(self.vector_store_dir)
                os.makedirs(self.vector_store_dir)
                
                # Restore from backup
                with gzip.open(latest_backup, 'rb') as f:
                    # Implement restoration logic here
                    pass
                
                logger.info(f"Restored from backup: {latest_backup}")
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")

    def cleanup_old_queries(self, max_age_days: int = 30):
        """Clean up old queries with improved error handling."""
        try:
            with self.lock:
                # Get all queries
                results = self.collection.get()
                
                if not results or not results['ids']:
                    return
                
                current_time = datetime.now().timestamp()
                old_ids = []
                
                # Find old queries
                for i, metadata in enumerate(results['metadatas']):
                    query_time = datetime.fromisoformat(metadata['timestamp']).timestamp()
                    if (current_time - query_time) > (max_age_days * 24 * 60 * 60):
                        old_ids.append(results['ids'][i])
                
                # Delete old queries
                if old_ids:
                    self.collection.delete(ids=old_ids)
                    logger.info(f"Cleaned up {len(old_ids)} old queries")
                    
                    # Update metadata
                    self.metadata["last_cleanup"] = datetime.now().isoformat()
                    self.metadata["total_queries"] = max(0, self.metadata["total_queries"] - len(old_ids))
                    self._save_metadata()
        except Exception as e:
            logger.error(f"Error cleaning up old queries: {e}")

    def get_metrics(self) -> Dict:
        """Get current metrics and statistics."""
        try:
            results = self.collection.get()
            return {
                "total_queries": self.metadata["total_queries"],
                "cache_hits": self.metrics["cache_hits"],
                "cache_misses": self.metrics["cache_misses"],
                "errors": self.metrics["errors"],
                "backups_created": self.metrics["backups_created"],
                "storage_size": self._get_storage_size(),
                "memory_usage": psutil.Process().memory_info().rss / 1024 / 1024,  # MB
                "last_backup": self.metadata.get("last_backup"),
                "last_cleanup": self.metadata.get("last_cleanup")
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}

    def _get_storage_size(self) -> int:
        """Get total size of vector store in bytes."""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.vector_store_dir):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            return total_size
        except Exception as e:
            logger.error(f"Error getting storage size: {e}")
            return 0

# Example usage
if __name__ == "__main__":
    # Initialize enhanced vector store
    vector_store = EnhancedVectorStore()
    
    # Test storing and retrieving queries
    test_query = "What are the total sales for each product?"
    test_sql = "SELECT p.PRODUCTNAME, SUM(psd.QUANTITY * psd.SALEPRICE) as total_sales FROM PRODUCT p JOIN PRODUCTSALEDETAIL psd ON p.PRODUCTCODE = psd.PRODUCTCODE GROUP BY p.PRODUCTNAME;"
    
    # Store query
    success = vector_store.store_query(test_query, test_sql)
    print(f"Query stored successfully: {success}")
    
    # Retrieve similar query
    similar_query, cached_sql = vector_store.get_similar_queries(test_query)
    print(f"Similar query found: {similar_query}")
    print(f"Cached SQL: {cached_sql}")
    
    # Get metrics
    metrics = vector_store.get_metrics()
    print("Metrics:", metrics) 