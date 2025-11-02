"""
Enhanced Retrieval System with Quality Boosters
Week-2 Quality Boosters Integration
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

# Import our quality booster modules
from .arabert_integration import AraBERTIntegration, HybridSearchWithAraBERT
from .bge_reranker import BGEReranker, AdvancedReranker
from .synonym_expander import QueryProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRetrievalSystem:
    """
    Enhanced retrieval system with all quality boosters
    """
    
    def __init__(self, 
                 me5_model=None,
                 bm25_index=None,
                 faiss_me5=None,
                 meta=None,
                 enable_arabert: bool = True,
                 enable_reranker: bool = True,
                 enable_synonyms: bool = True):
        """
        Initialize enhanced retrieval system
        
        Args:
            me5_model: mE5 embedding model
            bm25_index: BM25 index
            faiss_me5: FAISS index for mE5
            meta: Metadata
            enable_arabert: Enable AraBERT integration
            enable_reranker: Enable BGE reranker
            enable_synonyms: Enable synonym expansion
        """
        self.me5_model = me5_model
        self.bm25_index = bm25_index
        self.faiss_me5 = faiss_me5
        self.meta = meta
        
        # Quality booster components
        self.arabert_integration = None
        self.faiss_arabert = None
        self.bge_reranker = None
        self.query_processor = None
        
        # Configuration
        self.enable_arabert = enable_arabert
        self.enable_reranker = enable_reranker
        self.enable_synonyms = enable_synonyms
        
        # Default weights (0.7 mE5 / 0.3 AraBERT as requested)
        self.me5_weight = 0.7
        self.arabert_weight = 0.3
        self.bm25_weight = 0.0  # Disabled by default for semantic focus
        
    def load_quality_boosters(self):
        """Load all quality booster components"""
        logger.info("Loading quality boosters...")
        
        # Load AraBERT integration
        if self.enable_arabert:
            try:
                self.arabert_integration = AraBERTIntegration()
                if self.arabert_integration.load_model():
                    logger.info("✅ AraBERT integration loaded")
                    
                    # Try to load AraBERT FAISS index
                    arabert_index_path = "data/idx/arabert.faiss"
                    if Path(arabert_index_path).exists():
                        import faiss
                        self.faiss_arabert = faiss.read_index(arabert_index_path)
                        logger.info("✅ AraBERT FAISS index loaded")
                    else:
                        logger.warning("⚠️ AraBERT FAISS index not found, will use mE5 only")
                        self.enable_arabert = False
                else:
                    logger.warning("⚠️ Failed to load AraBERT, disabling")
                    self.enable_arabert = False
            except Exception as e:
                logger.error(f"❌ AraBERT integration failed: {e}")
                self.enable_arabert = False
        
        # Load BGE reranker
        if self.enable_reranker:
            try:
                self.bge_reranker = AdvancedReranker()
                if self.bge_reranker.load_model():
                    logger.info("✅ BGE reranker loaded")
                else:
                    logger.warning("⚠️ Failed to load BGE reranker, disabling")
                    self.enable_reranker = False
            except Exception as e:
                logger.error(f"❌ BGE reranker failed: {e}")
                self.enable_reranker = False
        
        # Load synonym expander
        if self.enable_synonyms:
            try:
                self.query_processor = QueryProcessor()
                if self.query_processor.load():
                    logger.info("✅ Synonym expander loaded")
                else:
                    logger.warning("⚠️ Failed to load synonym expander, disabling")
                    self.enable_synonyms = False
            except Exception as e:
                logger.error(f"❌ Synonym expander failed: {e}")
                self.enable_synonyms = False
        
        logger.info("Quality boosters loading completed")
        return True
    
    def search(self, query: str, topk: int = 10, 
               fusion_method: str = "weighted",
               enable_reranking: bool = True,
               enable_synonym_expansion: bool = True) -> Dict[str, Any]:
        """
        Enhanced search with all quality boosters
        
        Args:
            query: Search query
            topk: Number of results to return
            fusion_method: "weighted" or "rrf"
            enable_reranking: Enable BGE reranking
            enable_synonym_expansion: Enable synonym expansion
            
        Returns:
            Dictionary with search results and metadata
        """
        logger.info(f"Enhanced search: '{query}' (topk={topk})")
        
        # Step 1: Process query with synonym expansion
        processed_query = query
        query_info = {}
        
        if enable_synonym_expansion and self.enable_synonyms and self.query_processor:
            query_info = self.query_processor.process_query(query, expand_synonyms=True, max_synonyms=2)
            processed_query = query_info['expanded_query']
            logger.info(f"Query expanded: '{query}' -> '{processed_query}'")
        
        # Step 2: Perform hybrid search
        if self.enable_arabert and self.faiss_arabert:
            # Use AraBERT + mE5 hybrid search
            hybrid_search = HybridSearchWithAraBERT(
                self.me5_model,
                self.arabert_integration,
                self.bm25_index,
                self.faiss_me5,
                self.faiss_arabert,
                self.meta
            )
            
            # Get top-50 candidates for reranking
            candidates = hybrid_search.search(
                processed_query, 
                topk=50,  # Get more candidates for reranking
                me5_weight=self.me5_weight,
                arabert_weight=self.arabert_weight,
                bm25_weight=self.bm25_weight,
                fusion_method=fusion_method
            )
            
            logger.info(f"Hybrid search returned {len(candidates)} candidates")
        else:
            # Fallback to mE5 only
            logger.info("Using mE5-only search (AraBERT not available)")
            candidates = self._m5_only_search(processed_query, 50)
        
        # Step 3: Rerank top-50 candidates
        final_results = candidates
        reranking_info = {}
        
        if enable_reranking and self.enable_reranker and self.bge_reranker and len(candidates) > 0:
            logger.info(f"Reranking {len(candidates)} candidates with BGE reranker")
            
            try:
                reranked = self.bge_reranker.rerank_with_fusion(
                    processed_query,
                    candidates,
                    top_k=topk,
                    rerank_weight=0.7,
                    original_weight=0.3
                )
                
                final_results = reranked
                reranking_info = {
                    'reranking_applied': True,
                    'candidates_reranked': len(candidates),
                    'final_results': len(final_results)
                }
                
                logger.info(f"✅ Reranking completed: {len(final_results)} final results")
                
            except Exception as e:
                logger.error(f"❌ Reranking failed: {e}")
                # Fallback to original results
                final_results = candidates[:topk]
                reranking_info = {
                    'reranking_applied': False,
                    'error': str(e)
                }
        else:
            # No reranking, just take top-k
            final_results = candidates[:topk]
            reranking_info = {
                'reranking_applied': False,
                'reason': 'Reranker not available or disabled'
            }
        
        # Step 4: Prepare response
        response = {
            'query': query,
            'processed_query': processed_query,
            'results': final_results,
            'total_results': len(final_results),
            'quality_boosters': {
                'arabert_enabled': self.enable_arabert,
                'reranker_enabled': self.enable_reranker,
                'synonyms_enabled': self.enable_synonyms,
                'fusion_method': fusion_method,
                'weights': {
                    'me5': self.me5_weight,
                    'arabert': self.arabert_weight,
                    'bm25': self.bm25_weight
                }
            },
            'query_info': query_info,
            'reranking_info': reranking_info
        }
        
        logger.info(f"Enhanced search completed: {len(final_results)} results")
        return response
    
    def _m5_only_search(self, query: str, topk: int) -> List[Dict[str, Any]]:
        """Fallback mE5-only search"""
        try:
            # Get mE5 results
            query_embedding = self.me5_model.encode([query])
            scores, indices = self.faiss_me5.search(query_embedding, topk)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.meta):
                    result = self.meta[idx].copy()
                    result['score'] = float(scores[0][i])
                    result['fusion_method'] = 'm5_only'
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"mE5-only search failed: {e}")
            return []
    
    def update_weights(self, me5_weight: float = 0.7, arabert_weight: float = 0.3, bm25_weight: float = 0.0):
        """Update fusion weights"""
        self.me5_weight = me5_weight
        self.arabert_weight = arabert_weight
        self.bm25_weight = bm25_weight
        logger.info(f"Weights updated: mE5={me5_weight}, AraBERT={arabert_weight}, BM25={bm25_weight}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'arabert_enabled': self.enable_arabert and self.arabert_integration is not None,
            'reranker_enabled': self.enable_reranker and self.bge_reranker is not None,
            'synonyms_enabled': self.enable_synonyms and self.query_processor is not None,
            'arabert_index_loaded': self.faiss_arabert is not None,
            'weights': {
                'me5': self.me5_weight,
                'arabert': self.arabert_weight,
                'bm25': self.bm25_weight
            }
        }

def create_enhanced_retrieval_test():
    """Create test script for enhanced retrieval system"""
    script_content = '''#!/usr/bin/env python3
"""
Test script for enhanced retrieval system
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.enhanced_retrieval import EnhancedRetrievalSystem
from app.retrieval import load_bm25, load_faiss, load_meta, load_model

def test_enhanced_retrieval():
    """Test enhanced retrieval system"""
    
    print("Loading base components...")
    
    # Load base components
    bm25 = load_bm25("data/idx/bm25.pkl")
    faiss_me5 = load_faiss("data/idx/mE5.faiss")
    meta = load_meta("data/idx/meta.json")
    me5_model = load_model("intfloat/multilingual-e5-base")
    
    print("Initializing enhanced retrieval system...")
    
    # Initialize enhanced system
    enhanced_system = EnhancedRetrievalSystem(
        me5_model=me5_model,
        bm25_index=bm25,
        faiss_me5=faiss_me5,
        meta=meta,
        enable_arabert=True,
        enable_reranker=True,
        enable_synonyms=True
    )
    
    # Load quality boosters
    enhanced_system.load_quality_boosters()
    
    # Test queries
    test_queries = [
        "ما هو حد مسؤولية المشغل؟",
        "ما هي المواد النووية؟",
        "ما هو الترخيص المطلوب؟"
    ]
    
    print("Testing enhanced search...")
    
    for query in test_queries:
        print(f"\\nQuery: {query}")
        print("-" * 50)
        
        result = enhanced_system.search(
            query,
            topk=5,
            fusion_method="weighted",
            enable_reranking=True,
            enable_synonym_expansion=True
        )
        
        print(f"Results: {result['total_results']}")
        print(f"Processed query: {result['processed_query']}")
        print(f"Quality boosters: {result['quality_boosters']}")
        
        for i, doc in enumerate(result['results'][:3]):
            print(f"{i+1}. {doc.get('doc_id', 'Unknown')} - Score: {doc.get('score', 0):.3f}")
    
    # Test status
    print("\\nSystem status:")
    status = enhanced_system.get_status()
    for key, value in status.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_enhanced_retrieval()
'''
    
    with open("test_enhanced_retrieval.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("Enhanced retrieval test script created: test_enhanced_retrieval.py")

if __name__ == "__main__":
    create_enhanced_retrieval_test()
