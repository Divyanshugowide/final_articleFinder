"""
Synonym Expansion for Enhanced Arabic Search
Quality Booster for Week-2 - Query Time Synonym Expansion
"""

import json
import logging
from typing import List, Dict, Any, Set
from pathlib import Path
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SynonymExpander:
    """
    Synonym expansion for Arabic queries to avoid semantic drift
    """
    
    def __init__(self, glossary_path: str = "conf/glossary_ar.json"):
        """
        Initialize synonym expander
        
        Args:
            glossary_path: Path to Arabic glossary file
        """
        self.glossary_path = glossary_path
        self.synonyms = {}
        self.loaded = False
        
    def load_glossary(self):
        """Load Arabic glossary with synonyms"""
        try:
            if Path(self.glossary_path).exists():
                with open(self.glossary_path, 'r', encoding='utf-8') as f:
                    self.synonyms = json.load(f)
                logger.info(f"✅ Loaded {len(self.synonyms)} synonym groups from glossary")
            else:
                logger.warning(f"⚠️ Glossary file not found: {self.glossary_path}")
                self._create_default_glossary()
            
            self.loaded = True
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load glossary: {e}")
            return False
    
    def _create_default_glossary(self):
        """Create default Arabic glossary if none exists"""
        self.synonyms = {
            "المسؤولية": ["المسؤولية المدنية", "المسؤولية القانونية", "الالتزام"],
            "النووي": ["النووية", "الذرية", "الإشعاعي"],
            "الضرر": ["الأضرار", "الخسارة", "التلف"],
            "المشغل": ["المشغلين", "المشغلة", "المشغلات"],
            "المنشأة": ["المنشآت", "المرافق", "المحطة"],
            "الترخيص": ["التراخيص", "الإذن", "التصريح"],
            "الرقابة": ["المراقبة", "الإشراف", "التحكم"],
            "الهيئة": ["الجهة", "المؤسسة", "السلطة"],
            "التعويض": ["التعويضات", "المقابل", "البدل"],
            "التقادم": ["انقضاء", "انتهاء", "انقطاع"],
            "المطالبة": ["المطالبات", "الطلب", "الادعاء"],
            "الضمان": ["الضمانات", "الكفالة", "التأمين"],
            "المواد": ["المواد النووية", "المواد المشعة", "المواد"],
            "النفايات": ["النفايات المشعة", "المخلفات", "الفضلات"],
            "التعرض": ["التعرض الإشعاعي", "الاستقبال", "التأثر"],
            "الأمان": ["الأمان النووي", "السلامة", "الحماية"],
            "الأمن": ["الأمن النووي", "الحماية", "الوقاية"],
            "الطاقة": ["الطاقة النووية", "الطاقة الذرية", "الطاقة"],
            "الإشعاع": ["الإشعاعات", "الإشعاعي", "الإشعاعية"],
            "الوقود": ["الوقود النووي", "الوقود الذري", "الوقود"]
        }
        
        # Save default glossary
        with open(self.glossary_path, 'w', encoding='utf-8') as f:
            json.dump(self.synonyms, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Created default glossary with {len(self.synonyms)} synonym groups")
    
    def expand_query(self, query: str, max_synonyms: int = 2) -> str:
        """
        Expand query with synonyms to avoid semantic drift
        
        Args:
            query: Original search query
            max_synonyms: Maximum number of synonyms to add
            
        Returns:
            Expanded query with synonyms
        """
        if not self.loaded:
            if not self.load_glossary():
                return query
        
        # Tokenize query
        query_words = query.split()
        expanded_words = set(query_words)
        
        # Find synonyms for each word
        synonyms_added = 0
        for word in query_words:
            if synonyms_added >= max_synonyms:
                break
                
            # Clean word for matching
            clean_word = self._clean_word(word)
            
            # Find matching synonym group
            for base_word, synonyms in self.synonyms.items():
                if clean_word in synonyms or clean_word == base_word:
                    # Add up to 2 synonyms from this group
                    available_synonyms = [s for s in synonyms if s not in expanded_words]
                    if available_synonyms:
                        synonym_to_add = random.choice(available_synonyms[:2])
                        expanded_words.add(synonym_to_add)
                        synonyms_added += 1
                        logger.debug(f"Added synonym: {synonym_to_add} for {clean_word}")
                        break
        
        # Reconstruct query
        expanded_query = " ".join(sorted(expanded_words))
        
        if expanded_query != query:
            logger.info(f"Query expanded: '{query}' -> '{expanded_query}'")
        
        return expanded_query
    
    def expand_query_terms(self, query: str, max_synonyms: int = 2) -> List[str]:
        """
        Expand query into multiple query variations
        
        Args:
            query: Original search query
            max_synonyms: Maximum number of synonym variations
            
        Returns:
            List of query variations
        """
        if not self.loaded:
            if not self.load_glossary():
                return [query]
        
        query_variations = [query]
        query_words = query.split()
        
        # Create variations by replacing words with synonyms
        for word in query_words:
            clean_word = self._clean_word(word)
            
            for base_word, synonyms in self.synonyms.items():
                if clean_word in synonyms or clean_word == base_word:
                    for synonym in synonyms[:max_synonyms]:
                        if synonym != clean_word:
                            # Create variation by replacing word
                            variation_words = [synonym if w == word else w for w in query_words]
                            variation = " ".join(variation_words)
                            if variation not in query_variations:
                                query_variations.append(variation)
                    
                    break
        
        logger.info(f"Created {len(query_variations)} query variations")
        return query_variations
    
    def _clean_word(self, word: str) -> str:
        """Clean word for synonym matching"""
        # Remove punctuation and normalize
        import re
        clean_word = re.sub(r'[^\w\u0600-\u06FF]', '', word)
        return clean_word.strip()
    
    def get_synonyms_for_word(self, word: str) -> List[str]:
        """
        Get synonyms for a specific word
        
        Args:
            word: Word to find synonyms for
            
        Returns:
            List of synonyms
        """
        if not self.loaded:
            if not self.load_glossary():
                return []
        
        clean_word = self._clean_word(word)
        
        for base_word, synonyms in self.synonyms.items():
            if clean_word in synonyms or clean_word == base_word:
                return [s for s in synonyms if s != clean_word]
        
        return []
    
    def add_synonym_group(self, base_word: str, synonyms: List[str]):
        """
        Add a new synonym group
        
        Args:
            base_word: Base word
            synonyms: List of synonyms
        """
        if not self.loaded:
            self.load_glossary()
        
        self.synonyms[base_word] = synonyms
        
        # Save updated glossary
        with open(self.glossary_path, 'w', encoding='utf-8') as f:
            json.dump(self.synonyms, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Added synonym group: {base_word} -> {synonyms}")

class QueryProcessor:
    """
    Enhanced query processor with synonym expansion
    """
    
    def __init__(self, glossary_path: str = "conf/glossary_ar.json"):
        self.synonym_expander = SynonymExpander(glossary_path)
        self.loaded = False
        
    def load(self):
        """Load synonym expander"""
        self.loaded = self.synonym_expander.load_glossary()
        return self.loaded
    
    def process_query(self, query: str, expand_synonyms: bool = True, 
                     max_synonyms: int = 2) -> Dict[str, Any]:
        """
        Process query with optional synonym expansion
        
        Args:
            query: Original query
            expand_synonyms: Whether to expand with synonyms
            max_synonyms: Maximum synonyms to add
            
        Returns:
            Dictionary with processed query information
        """
        if not self.loaded:
            self.load()
        
        result = {
            'original_query': query,
            'expanded_query': query,
            'query_variations': [query],
            'synonyms_used': [],
            'expansion_applied': False
        }
        
        if expand_synonyms and self.loaded:
            # Expand query with synonyms
            expanded_query = self.synonym_expander.expand_query(query, max_synonyms)
            result['expanded_query'] = expanded_query
            
            # Get query variations
            variations = self.synonym_expander.expand_query_terms(query, max_synonyms)
            result['query_variations'] = variations
            
            # Track synonyms used
            original_words = set(query.split())
            expanded_words = set(expanded_query.split())
            synonyms_used = expanded_words - original_words
            result['synonyms_used'] = list(synonyms_used)
            result['expansion_applied'] = len(synonyms_used) > 0
        
        return result

def create_synonym_test_script():
    """Create a test script for synonym expansion"""
    script_content = '''#!/usr/bin/env python3
"""
Test script for synonym expansion functionality
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.synonym_expander import SynonymExpander, QueryProcessor

def test_synonym_expansion():
    """Test synonym expansion functionality"""
    
    # Test queries
    test_queries = [
        "ما هو حد مسؤولية المشغل؟",
        "ما هي المواد النووية؟",
        "ما هو الترخيص المطلوب؟",
        "ما هي النفايات المشعة؟",
        "ما هو التعرض الإشعاعي؟"
    ]
    
    # Test synonym expander
    print("Testing Synonym Expander...")
    expander = SynonymExpander()
    if expander.load_glossary():
        for query in test_queries:
            expanded = expander.expand_query(query, max_synonyms=2)
            print(f"Original: {query}")
            print(f"Expanded: {expanded}")
            print()
    
    # Test query processor
    print("Testing Query Processor...")
    processor = QueryProcessor()
    if processor.load():
        for query in test_queries:
            result = processor.process_query(query, expand_synonyms=True, max_synonyms=2)
            print(f"Query: {result['original_query']}")
            print(f"Expanded: {result['expanded_query']}")
            print(f"Synonyms used: {result['synonyms_used']}")
            print(f"Variations: {len(result['query_variations'])}")
            print()

if __name__ == "__main__":
    test_synonym_expansion()
'''
    
    with open("test_synonym_expansion.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("Synonym expansion test script created: test_synonym_expansion.py")

if __name__ == "__main__":
    create_synonym_test_script()
