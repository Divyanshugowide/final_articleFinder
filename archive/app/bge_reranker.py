"""
BAAI/bge-reranker-v2-m3 Integration for Enhanced Search Results
Quality Booster for Week-2
"""

import torch
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import CrossEncoder
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BGEReranker:
    """
    BAAI/bge-reranker-v2-m3 for multilingual reranking
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        """
        Initialize BGE reranker model
        
        Args:
            model_name: BGE reranker model name
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.loaded = False
        
    def load_model(self):
        """Load BGE reranker model"""
        try:
            logger.info(f"Loading BGE reranker model: {self.model_name}")
            self.model = CrossEncoder(self.model_name, device=self.device)
            self.loaded = True
            logger.info(f"✅ BGE reranker loaded successfully on {self.device}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load BGE reranker: {e}")
            return False
    
    def rerank(self, query: str, documents: List[Dict[str, Any]], 
               top_k: int = 10, batch_size: int = 32) -> List[Dict[str, Any]]:
        """
        Rerank documents using BGE reranker
        
        Args:
            query: Search query
            documents: List of document dictionaries
            top_k: Number of top results to return
            batch_size: Batch size for processing
            
        Returns:
            Reranked list of documents
        """
        if not self.loaded:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if not documents:
            return []
        
        logger.info(f"Reranking {len(documents)} documents with BGE reranker")
        
        # Prepare query-document pairs
        pairs = []
        for doc in documents:
            # Use excerpt or text for reranking
            text = doc.get('excerpt', doc.get('text', ''))
            # Clean HTML tags if present
            text = self._clean_text(text)
            pairs.append([query, text])
        
        # Get relevance scores in batches
        scores = []
        for i in range(0, len(pairs), batch_size):
            batch_pairs = pairs[i:i + batch_size]
            batch_scores = self.model.predict(batch_pairs)
            scores.extend(batch_scores)
        
        # Sort documents by relevance score
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k results with updated scores
        reranked_docs = []
        for doc, score in scored_docs[:top_k]:
            doc_copy = doc.copy()
            doc_copy['rerank_score'] = float(score)
            doc_copy['original_score'] = doc.get('score', 0.0)
            reranked_docs.append(doc_copy)
        
        logger.info(f"✅ Reranking completed, returning top {len(reranked_docs)} results")
        return reranked_docs
    
    def _clean_text(self, text: str) -> str:
        """Clean text for reranking"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Limit length to avoid token limits
        if len(text) > 512:
            text = text[:512]
        return text

class AdvancedReranker:
    """
    Advanced reranker with multiple strategies and score fusion
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.bge_reranker = BGEReranker(model_name)
        self.loaded = False
        
    def load_model(self):
        """Load reranker model"""
        self.loaded = self.bge_reranker.load_model()
        return self.loaded
    
    def rerank_with_fusion(self, query: str, documents: List[Dict[str, Any]], 
                          top_k: int = 10,
                          rerank_weight: float = 0.7,
                          original_weight: float = 0.3) -> List[Dict[str, Any]]:
        """
        Rerank with weighted combination of original and rerank scores
        
        Args:
            query: Search query
            documents: List of document dictionaries
            top_k: Number of top results to return
            rerank_weight: Weight for rerank score
            original_weight: Weight for original score
            
        Returns:
            Reranked list of documents
        """
        if not self.loaded:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if not documents:
            return []
        
        # Get rerank scores
        reranked = self.bge_reranker.rerank(query, documents, len(documents))
        
        # Combine with original scores
        for doc in reranked:
            original_score = doc.get('original_score', 0.0)
            rerank_score = doc.get('rerank_score', 0.0)
            
            # Normalize scores to [0, 1] range
            original_score_norm = min(original_score, 1.0)
            rerank_score_norm = min(rerank_score, 1.0)
            
            # Weighted combination
            combined_score = (original_weight * original_score_norm + 
                            rerank_weight * rerank_score_norm)
            
            doc['combined_score'] = combined_score
        
        # Sort by combined score
        reranked.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return reranked[:top_k]
    
    def rerank_by_document_type(self, query: str, documents: List[Dict[str, Any]], 
                               top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Rerank with special attention to document type relevance
        
        Args:
            query: Search query
            documents: List of document dictionaries
            top_k: Number of top results to return
            
        Returns:
            Reranked list of documents
        """
        if not self.loaded:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if not documents:
            return []
        
        # Group documents by type
        doc_groups = {}
        for doc in documents:
            doc_type = doc.get('doc_id', '').split()[0]  # First word as type
            if doc_type not in doc_groups:
                doc_groups[doc_type] = []
            doc_groups[doc_type].append(doc)
        
        # Rerank within each group
        reranked_groups = []
        for doc_type, group_docs in doc_groups.items():
            if len(group_docs) == 1:
                reranked_groups.extend(group_docs)
            else:
                reranked_group = self.bge_reranker.rerank(query, group_docs, len(group_docs))
                reranked_groups.extend(reranked_group)
        
        # Final rerank across all documents
        final_reranked = self.bge_reranker.rerank(query, reranked_groups, top_k)
        
        return final_reranked

def create_reranker_script():
    """Create a script to test BGE reranker functionality"""
    script_content = '''#!/usr/bin/env python3
"""
Test script for BGE reranker functionality
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.bge_reranker import BGEReranker, AdvancedReranker

def test_bge_reranker():
    """Test BGE reranker functionality"""
    
    # Sample documents
    documents = [
        {
            'doc_id': 'Law of Civil Liability for Nuclear Damage',
            'article_no': 'Article 1',
            'text': 'This document covers nuclear damage liability and compensation procedures.',
            'excerpt': 'Nuclear damage liability compensation procedures...',
            'score': 0.8
        },
        {
            'doc_id': 'Law of Nuclear and Radiation Control', 
            'article_no': 'Article 2',
            'text': 'This discusses radiation protection measures and safety regulations.',
            'excerpt': 'Radiation protection measures safety regulations...',
            'score': 0.7
        },
        {
            'doc_id': 'National Policy for Radioactive Waste Management',
            'article_no': 'Article 3', 
            'text': 'This covers nuclear waste management procedures and disposal methods.',
            'excerpt': 'Nuclear waste management disposal methods...',
            'score': 0.6
        }
    ]
    
    query = "nuclear safety regulations"
    
    # Test BGE reranker
    print("Testing BGE reranker...")
    reranker = BGEReranker()
    if reranker.load_model():
        reranked = reranker.rerank(query, documents, top_k=2)
        print("BGE reranked results:")
        for i, doc in enumerate(reranked):
            print(f"{i+1}. {doc['doc_id']} - Rerank Score: {doc.get('rerank_score', 0):.3f}")
    
    # Test advanced reranker
    print("\\nTesting advanced reranker...")
    advanced_reranker = AdvancedReranker()
    if advanced_reranker.load_model():
        reranked = advanced_reranker.rerank_with_fusion(
            query, documents, top_k=2, rerank_weight=0.7, original_weight=0.3
        )
        print("Advanced reranked results:")
        for i, doc in enumerate(reranked):
            print(f"{i+1}. {doc['doc_id']} - Combined: {doc.get('combined_score', 0):.3f}")

if __name__ == "__main__":
    test_bge_reranker()
'''
    
    with open("test_bge_reranker.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("BGE reranker test script created: test_bge_reranker.py")

if __name__ == "__main__":
    create_reranker_script()
