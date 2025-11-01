# System Design Document - NRRC Arabic PoV Windows

## Enterprise-Grade Arabic Document Retrieval System with AI-Powered Quality Boosters

**Version:** 2.0  
**Date:** October 2025  
**Project:** NRRC Arabic PoV - Advanced Arabic Legal Document Search System

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [C4 Architecture Diagrams](#2-c4-architecture-diagrams)
   - [Level 1: System Context](#level-1-system-context-diagram)
   - [Level 2: Container](#level-2-container-diagram)
   - [Level 3: Component](#level-3-component-diagram)
   - [Level 4: Code](#level-4-code-diagram)
3. [System Design Diagrams](#3-system-design-diagrams)
   - [High-Level Architecture](#high-level-architecture)
   - [Data Flow Architecture](#data-flow-architecture)
   - [Authentication & RBAC Flow](#authentication--rbac-flow)
   - [Search & Retrieval Pipeline](#search--retrieval-pipeline)
   - [Quality Boosters Architecture](#quality-boosters-architecture)
4. [Component Details](#4-component-details)
5. [Deployment Architecture](#5-deployment-architecture)
6. [Security Architecture](#6-security-architecture)
7. [Performance & Scalability](#7-performance--scalability)

---

## 1. System Overview

### 1.1 Purpose

The NRRC Arabic PoV system is an enterprise-grade, offline Arabic document retrieval system designed for nuclear regulatory documents. It features:

- **Hybrid Search**: BM25 keyword + multilingual semantic embeddings (mE5 + AraBERT)
- **AI-Powered Quality Boosters**: BGE reranker, AraBERT integration, synonym expansion
- **Role-Based Access Control (RBAC)**: Admin, Legal, Staff roles with document-level security
- **Arabic-Native Support**: RTL interface, Arabic normalization, diacritic handling
- **Offline Operation**: Complete system operates without internet after initial setup

### 1.2 Key Features

| Feature | Description |
|---------|-------------|
| **Semantic Search** | mE5 multilingual embeddings + AraBERT Arabic-native embeddings |
| **Keyword Search** | BM25Okapi for exact term matching |
| **AI Reranking** | BAAI/bge-reranker-v2-m3 for 10-20% precision improvement |
| **Synonym Expansion** | Query-time expansion with 20+ Arabic legal glossary groups |
| **RBAC Security** | JWT authentication with role-based document filtering |
| **Fusion Methods** | Weighted fusion & RRF (Reciprocal Rank Fusion) |
| **Highlighting** | Yellow (exact) & Green (semantic) match highlighting |

---

## 2. C4 Architecture Diagrams

### Level 1: System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   NRRC Organization Boundary                     │
│                                                                   │
│  ┌──────────┐        ┌──────────────────────────┐              │
│  │  Admin   │───────▶│                          │              │
│  │  User    │        │   NRRC Arabic PoV        │              │
│  └──────────┘        │   Search System          │              │
│                      │                          │              │
│  ┌──────────┐        │  • Arabic Document       │              │
│  │  Legal   │───────▶│    Retrieval             │              │
│  │  Advisor │        │  • RBAC Security         │              │
│  └──────────┘        │  • AI-Powered Search     │              │
│                      │  • Offline Operation     │              │
│  ┌──────────┐        │                          │              │
│  │  Staff   │───────▶│                          │              │
│  │  Member  │        └────────────┬─────────────┘              │
│  └──────────┘                     │                            │
│                                   │                            │
│                          ┌────────▼────────┐                   │
│                          │  Local File     │                   │
│                          │  System (PDFs)  │                   │
│                          └─────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘

External Systems:
┌─────────────────────┐
│  HuggingFace Hub    │  (Initial model download only)
│  • mE5 Model        │
│  • AraBERT Model    │
│  • BGE Reranker     │
└─────────────────────┘
```

**Description:**
- Three user types interact with the system: Admin (full access), Legal (restricted docs), Staff (general docs)
- System operates fully offline after initial setup
- Local PDF documents are the primary data source
- External model downloads from HuggingFace only during first setup

---

### Level 2: Container Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                     NRRC Arabic PoV System                              │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      Web Browser (Client)                        │  │
│  │  ┌────────────────────┐  ┌─────────────────────────────────┐    │  │
│  │  │  Login Interface   │  │  Search Interface (Arabic RTL)  │    │  │
│  │  │  • JWT Auth        │  │  • Query Input                  │    │  │
│  │  │  • Role Display    │  │  • Result Display               │    │  │
│  │  └────────────────────┘  │  • Highlighting (Yellow/Green)  │    │  │
│  │                          └─────────────────────────────────┘    │  │
│  └───────────────────────────────────┬──────────────────────────────┘  │
│                                      │ HTTPS/REST API                  │
│                                      ▼                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                   FastAPI Application Server                     │  │
│  │  ┌────────────────┐  ┌──────────────────┐  ┌────────────────┐   │  │
│  │  │  Auth Module   │  │  Retrieval       │  │  Enhanced      │   │  │
│  │  │  • JWT Verify  │  │  Engine          │  │  Retrieval     │   │  │
│  │  │  • RBAC Check  │  │  • Hybrid Search │  │  • Boosters    │   │  │
│  │  │  • User Mgmt   │  │  • BM25 + FAISS  │  │  • Reranker    │   │  │
│  │  └────────────────┘  │  • Highlighting  │  │  • Synonyms    │   │  │
│  │                      └──────────────────┘  └────────────────┘   │  │
│  └───────────────────────────────┬──────────────────────────────────┘  │
│                                  │                                     │
│  ┌───────────────────────────────▼──────────────────────────────────┐  │
│  │                    Data Storage Layer                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐            │  │
│  │  │  BM25 Index │  │ FAISS mE5   │  │ FAISS        │            │  │
│  │  │  (Pickle)   │  │ Index       │  │ AraBERT      │            │  │
│  │  │  • Keywords │  │ • Semantic  │  │ Index        │            │  │
│  │  └─────────────┘  └─────────────┘  │ • Arabic     │            │  │
│  │                                    └──────────────┘            │  │
│  │  ┌──────────────────────────────────────────────────────────┐   │  │
│  │  │  Metadata Store (JSON)                                   │   │  │
│  │  │  • Document IDs                                          │   │  │
│  │  │  • Article Numbers                                       │   │  │
│  │  │  • Page Ranges                                           │   │  │
│  │  │  • Role Assignments                                      │   │  │
│  │  └──────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    ML Models Layer                               │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │  │
│  │  │  mE5 Model  │  │ AraBERT      │  │  BGE Reranker v2-m3     │ │  │
│  │  │  (768-dim)  │  │ Model        │  │  (Cross-Encoder)        │ │  │
│  │  └─────────────┘  │ (768-dim)    │  └─────────────────────────┘ │  │
│  │                   └──────────────┘                              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                 Configuration & Resources                        │  │
│  │  • glossary_ar.json (20+ synonym groups)                        │  │
│  │  • Raw PDFs (data/raw_pdfs/)                                    │  │
│  │  • Processed Chunks (data/processed/)                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

**Description:**
- **Client Layer**: Browser-based UI with Arabic RTL support
- **Application Layer**: FastAPI server with auth, retrieval, and enhanced search
- **Data Layer**: Multiple indices (BM25, mE5 FAISS, AraBERT FAISS) + metadata
- **ML Models**: Three transformer models for embeddings and reranking
- **Config Layer**: Glossary and document storage

---

### Level 3: Component Diagram

#### 3.1 Authentication & RBAC Component

```
┌─────────────────────────────────────────────────────────────────┐
│                    Auth & RBAC Component                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Authentication Module                       │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐   │  │
│  │  │  JWT Token  │  │  Password    │  │  Session      │   │  │
│  │  │  Manager    │  │  Hash (bcrypt)│ │  Management   │   │  │
│  │  │  • Create   │  │  • Verify    │  │  • Expire     │   │  │
│  │  │  • Verify   │  │  • Hash      │  │  • Refresh    │   │  │
│  │  └─────────────┘  └──────────────┘  └───────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              RBAC Module                                 │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐   │  │
│  │  │  Role       │  │  Permission  │  │  Document     │   │  │
│  │  │  Hierarchy  │  │  Checker     │  │  Filter       │   │  │
│  │  │  • Admin    │  │  • Check     │  │  • Filter by  │   │  │
│  │  │  • Legal    │  │  • Validate  │  │    Role       │   │  │
│  │  │  • Staff    │  │  • Authorize │  │  • Access     │   │  │
│  │  └─────────────┘  └──────────────┘  │    Control    │   │  │
│  │                                     └───────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              User Management                             │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Users Database (In-Memory)                        │  │  │
│  │  │  • admin: [admin, legal, staff]                    │  │  │
│  │  │  • legal: [legal, staff]                           │  │  │
│  │  │  • staff: [staff]                                  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

Flow:
1. User Login → Credential Verification → JWT Token Generation
2. Each Request → JWT Verification → Role Extraction
3. Search Query → Document Filtering by Role → Response
```

#### 3.2 Retrieval Engine Component

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Retrieval Engine Component                       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Query Processing Pipeline                       │  │
│  │                                                              │  │
│  │  ┌───────────┐      ┌─────────────┐      ┌──────────────┐  │  │
│  │  │  Query    │ ───▶ │  Arabic     │ ───▶ │  Synonym     │  │  │
│  │  │  Input    │      │  Normalize  │      │  Expansion   │  │  │
│  │  └───────────┘      └─────────────┘      └──────────────┘  │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                ▼                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Hybrid Search Module                            │  │
│  │                                                              │  │
│  │  ┌───────────────┐  ┌─────────────────┐  ┌──────────────┐  │  │
│  │  │  BM25 Search  │  │  mE5 FAISS      │  │  AraBERT     │  │  │
│  │  │  • Keyword    │  │  • Semantic     │  │  FAISS       │  │  │
│  │  │  • Exact      │  │  • Multilingual │  │  • Arabic    │  │  │
│  │  │    Match      │  │  • 768-dim      │  │    Native    │  │  │
│  │  │  • Top-50     │  │  • Top-50       │  │  • 768-dim   │  │  │
│  │  └───────┬───────┘  └────────┬────────┘  └──────┬───────┘  │  │
│  │          │                   │                   │          │  │
│  │          └───────────────────┼───────────────────┘          │  │
│  └────────────────────────────────┬──────────────────────────────┘  │
│                                   ▼                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Score Fusion Module                             │  │
│  │                                                              │  │
│  │  ┌────────────────────────┐  ┌────────────────────────────┐ │  │
│  │  │  Weighted Fusion       │  │  RRF Fusion               │ │  │
│  │  │  • mE5: 0.7            │  │  • Reciprocal Rank        │ │  │
│  │  │  • AraBERT: 0.3        │  │  • K=60                   │ │  │
│  │  │  • BM25: 0.0 (optional)│  │  • Equal Weighting        │ │  │
│  │  └────────────────────────┘  └────────────────────────────┘ │  │
│  └────────────────────────────────┬──────────────────────────────┘  │
│                                   ▼                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              BGE Reranking Module                            │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  BAAI/bge-reranker-v2-m3                               │  │  │
│  │  │  • Cross-Encoder                                       │  │  │
│  │  │  • Query-Document Relevance                            │  │  │
│  │  │  • Top-50 → Top-K                                      │  │  │
│  │  │  • Score Fusion: 0.7 rerank + 0.3 original            │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────┬──────────────────────────────┘  │
│                                   ▼                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Result Processing                               │  │
│  │  ┌────────────────────┐  ┌──────────────────────────────┐    │  │
│  │  │  RBAC Filtering    │  │  Highlighting                │    │  │
│  │  │  • Check Roles     │  │  • Yellow: Exact Match       │    │  │
│  │  │  • Filter Docs     │  │  • Green: Semantic Match     │    │  │
│  │  │  • Hide Restricted │  │  • Show Found Words          │    │  │
│  │  └────────────────────┘  └──────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

#### 3.3 Quality Boosters Component

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Quality Boosters Component                       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              1. Synonym Expander                             │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Glossary (glossary_ar.json)                           │  │  │
│  │  │  • 20+ Synonym Groups                                  │  │  │
│  │  │  • Arabic Legal Terms                                  │  │  │
│  │  │  • Nuclear/Radiation Terms                             │  │  │
│  │  │  • English-Arabic Cross Terms                          │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐    │  │
│  │  │  Query        │  │  Synonym     │  │  Expanded    │    │  │
│  │  │  Analysis     │→ │  Matching    │→ │  Query       │    │  │
│  │  │  • Tokenize   │  │  • Max 2     │  │  • Original  │    │  │
│  │  │  • Normalize  │  │    Synonyms  │  │    + 2 Syns  │    │  │
│  │  └────────────────┘  └──────────────┘  └──────────────┘    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              2. AraBERT Integration                          │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  aubmindlab/bert-base-arabertv2                        │  │  │
│  │  │  • Arabic-Native Embeddings                            │  │  │
│  │  │  • 768-dimensional Vectors                             │  │  │
│  │  │  • Better Arabic Understanding                         │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐  │  │
│  │  │  Query     │  │  AraBERT     │  │  FAISS Index      │  │  │
│  │  │  Encoding  │→ │  Embedding   │→ │  Search           │  │  │
│  │  └────────────┘  └──────────────┘  └────────────────────┘  │  │
│  │                                                              │  │
│  │  Fusion with mE5:                                           │  │
│  │  • 0.7 × mE5_score + 0.3 × AraBERT_score                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              3. BGE Reranker                                 │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  BAAI/bge-reranker-v2-m3                               │  │  │
│  │  │  • Cross-Encoder Architecture                          │  │  │
│  │  │  • Multilingual Support (Arabic + 100 langs)           │  │  │
│  │  │  • Query-Document Joint Encoding                       │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │  │
│  │  │  Top-50      │  │  Rerank with  │  │  Fusion Score   │  │  │
│  │  │  Candidates  │→ │  BGE Model    │→ │  0.7×rerank +   │  │  │
│  │  │  from Hybrid │  │  (Query-Doc   │  │  0.3×original   │  │  │
│  │  │  Search      │  │   Pairs)      │  └─────────────────┘  │  │
│  │  └──────────────┘  └───────────────┘                        │  │
│  │                                                              │  │
│  │  Expected Improvement: 10-20% precision boost               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Level 4: Code Diagram

#### 4.1 Search Request Flow (Code Level)

```python
# app/run_api.py
@app.post("/ask")
async def ask(payload: AskPayload, current_user: User = Depends(get_current_user)):
    """
    1. Authentication & Authorization
       ├─ JWT Token Verification
       ├─ Extract User Roles
       └─ Get Effective Roles
    """
    effective_roles = get_effective_roles(current_user.roles)
    
    """
    2. Search Execution
       ├─ Call Retrieval Engine
       └─ Pass Query + Roles
    """
    out = search(indices, payload.query, effective_roles, topk=payload.topk)
    
    """
    3. RBAC Filtering
       ├─ Filter Results by User Roles
       └─ Check Document Access
    """
    filtered_results = filter_documents_by_access(current_user.roles, out["results"])
    
    """
    4. Response Generation
       └─ Return JSON with Answer + Citations
    """
    return Response(content=json.dumps({
        "answer": answer_html, 
        "citations": filtered_results,
        "user_roles": current_user.roles,
        "total_found": len(out["results"]),
        "accessible_results": len(filtered_results)
    }))

# app/retrieval.py
def search(indices: Indices, query: str, roles: list[str], topk=5):
    """
    1. Query Processing
       ├─ Tokenize Arabic Query
       ├─ Normalize Text
       └─ Expand with Synonyms
    """
    q_tokens = tokenize_ar(query)
    glossary = load_glossary()
    green_terms = expand_terms_from_glossary(query, glossary)
    
    """
    2. BM25 Keyword Search
       ├─ Tokenize Query
       └─ Get Top-50 Results
    """
    bm25_scores = indices.bm25.get_scores(q_tokens)
    bm25_ranks = np.argsort(bm25_scores)[::-1][:50]
    
    """
    3. Semantic Search (FAISS)
       ├─ Encode Query with mE5
       └─ Search FAISS Index
    """
    q_emb = indices.model.encode([query])
    D, I = indices.faiss_index.search(q_emb, 50)
    
    """
    4. Score Fusion
       ├─ Normalize Scores
       ├─ Weighted Combination: α×semantic + (1-α)×keyword
       └─ Sort by Combined Score
    """
    final = alpha * vc_n + (1 - alpha) * bm_n
    
    """
    5. RBAC Filtering
       ├─ Check Document Roles
       └─ Filter by User Roles
    """
    if roles and not (set(roles) & set(doc_roles)):
        continue
    
    """
    6. Highlighting
       ├─ Yellow: Exact Matches
       └─ Green: Semantic Matches
    """
    highlighted = highlight_text(snippet, yellow_terms, green_terms)
    
    return {"answer": answer_html, "results": results}

# app/enhanced_retrieval.py
class EnhancedRetrievalSystem:
    def search(self, query: str, topk: int = 10):
        """
        Enhanced Search Pipeline with Quality Boosters
        
        1. Synonym Expansion
           └─ QueryProcessor.process_query()
        """
        query_info = self.query_processor.process_query(query, max_synonyms=2)
        processed_query = query_info['expanded_query']
        
        """
        2. Hybrid Search (mE5 + AraBERT + BM25)
           ├─ HybridSearchWithAraBERT.search()
           └─ Weighted Fusion: 0.7×mE5 + 0.3×AraBERT
        """
        candidates = hybrid_search.search(
            processed_query, 
            topk=50,  # Get more for reranking
            me5_weight=0.7,
            arabert_weight=0.3
        )
        
        """
        3. BGE Reranking
           ├─ AdvancedReranker.rerank_with_fusion()
           └─ Score Fusion: 0.7×rerank + 0.3×original
        """
        final_results = self.bge_reranker.rerank_with_fusion(
            processed_query,
            candidates,
            top_k=topk
        )
        
        return {
            'query': query,
            'results': final_results,
            'quality_boosters': {...}
        }
```

---

## 3. System Design Diagrams

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          NRRC Arabic PoV System                         │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        Presentation Layer                         │ │
│  │  ┌──────────────────┐     ┌──────────────────┐                   │ │
│  │  │  Web UI (RTL)    │     │  REST API        │                   │ │
│  │  │  • Login         │     │  • /ask          │                   │ │
│  │  │  • Search        │     │  • /login        │                   │ │
│  │  │  • Results       │     │  • /me           │                   │ │
│  │  └──────────────────┘     └──────────────────┘                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        Business Logic Layer                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │ │
│  │  │  Auth &      │  │  Retrieval   │  │  Enhanced            │   │ │
│  │  │  RBAC        │  │  Engine      │  │  Retrieval           │   │ │
│  │  │  • JWT       │  │  • Hybrid    │  │  • Quality Boosters  │   │ │
│  │  │  • Roles     │  │    Search    │  │  • Reranking         │   │ │
│  │  │  • Filtering │  │  • Fusion    │  │  • Synonym Exp.      │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        ML/AI Layer                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │ │
│  │  │  mE5 Model   │  │  AraBERT     │  │  BGE Reranker        │   │ │
│  │  │  768-dim     │  │  768-dim     │  │  Cross-Encoder       │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        Data Access Layer                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │ │
│  │  │  BM25 Index  │  │  FAISS mE5   │  │  FAISS AraBERT       │   │ │
│  │  │  (Pickle)    │  │  (Binary)    │  │  (Binary)            │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │ │
│  │                                                                   │ │
│  │  ┌───────────────────────────────────────────────────────────┐   │ │
│  │  │  Metadata (JSON)  •  Glossary (JSON)  •  PDFs (Local)    │   │ │
│  │  └───────────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Document Processing Pipeline                      │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: Document Ingestion
┌──────────────┐      ┌─────────────────┐      ┌────────────────┐
│  Raw PDFs    │ ───▶ │  PDF Extractor  │ ───▶ │  Text Content  │
│  (Arabic)    │      │  (PyMuPDF)      │      │  + Metadata    │
└──────────────┘      └─────────────────┘      └────────────────┘

Step 2: Text Processing & Chunking
┌────────────────┐      ┌─────────────────┐      ┌───────────────┐
│  Text Content  │ ───▶ │  Chunking       │ ───▶ │  Chunks       │
│  + Metadata    │      │  • 512 tokens   │      │  (JSONL)      │
└────────────────┘      │  • Overlap: 50  │      └───────────────┘
                        └─────────────────┘

Step 3: Index Creation (Parallel)
┌───────────────┐      ┌─────────────────┐      ┌────────────────┐
│  Chunks       │ ───▶ │  BM25 Indexing  │ ───▶ │  bm25.pkl      │
│  (JSONL)      │      │  • Tokenization │      └────────────────┘
└───────────────┘      └─────────────────┘
       │
       ├────────────▶ │  mE5 Encoding   │ ───▶ │  mE5.faiss     │
       │              │  • 768-dim      │      └────────────────┘
       │              └─────────────────┘
       │
       └────────────▶ │  AraBERT        │ ───▶ │  arabert.faiss │
                      │  Encoding       │      └────────────────┘
                      │  • 768-dim      │
                      └─────────────────┘

Step 4: Metadata Storage
┌───────────────┐      ┌─────────────────┐      ┌────────────────┐
│  Chunks +     │ ───▶ │  Metadata       │ ───▶ │  meta.json     │
│  Roles        │      │  Aggregation    │      │  • doc_id      │
└───────────────┘      └─────────────────┘      │  • article_no  │
                                                 │  • pages       │
                                                 │  • roles       │
                                                 └────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          Search Query Pipeline                           │
└─────────────────────────────────────────────────────────────────────────┘

User Query: "ما هو حد مسؤولية المشغل؟"
     │
     ▼
┌─────────────────────┐
│  1. Authentication  │  JWT Token → Verify → Extract Roles
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  2. Query           │  • Tokenize: ["ما", "هو", "حد", "مسؤولية", "المشغل"]
│     Processing      │  • Normalize: Remove diacritics
│                     │  • Expand: Add synonyms ["المسؤولية المدنية", "الالتزام"]
└──────────┬──────────┘
           ▼
┌─────────────────────────────────────────────────┐
│  3. Parallel Search                             │
│  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ BM25       │  │ mE5 FAISS  │  │ AraBERT   │ │
│  │ Search     │  │ Search     │  │ FAISS     │ │
│  │ Top-50     │  │ Top-50     │  │ Search    │ │
│  │            │  │            │  │ Top-50    │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬─────┘ │
└────────┼───────────────┼───────────────┼────────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
┌─────────────────────────────────────┐
│  4. Score Fusion                    │
│     • Weighted: 0.7×mE5 + 0.3×Arab  │
│     • OR RRF: Reciprocal Rank       │
│     • Result: Top-50 Candidates     │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│  5. BGE Reranking                   │
│     • Top-50 → BGE Cross-Encoder    │
│     • Relevance Scoring             │
│     • Fusion: 0.7×rerank + 0.3×orig │
│     • Result: Top-K Final           │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│  6. RBAC Filtering                  │
│     • Check doc_roles vs user_roles │
│     • Filter restricted documents   │
│     • Keep only accessible docs     │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│  7. Highlighting                    │
│     • Yellow: Exact matches         │
│     • Green: Semantic matches       │
│     • Show actual found words       │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│  8. Response                        │
│     {                               │
│       "answer": "<highlighted>",    │
│       "citations": [...],           │
│       "total_found": 10,            │
│       "accessible_results": 8       │
│     }                               │
└─────────────────────────────────────┘
```

---

### Authentication & RBAC Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Authentication Flow                               │
└─────────────────────────────────────────────────────────────────────────┘

User Login Sequence:

1. User enters credentials
   ┌──────────┐
   │  Browser │ ─── POST /login ───▶ ┌────────────────┐
   └──────────┘    {username, pwd}    │  Auth Module   │
                                      └────────┬───────┘
                                               │
2. Verify credentials                          │
   ┌──────────────────────────┐               │
   │  Users DB                │◀──────────────┘
   │  • admin: bcrypt(hash)   │  Check password hash
   │  • legal: bcrypt(hash)   │
   │  • staff: bcrypt(hash)   │
   └──────────┬───────────────┘
              │
              ▼
3. Generate JWT Token
   ┌────────────────────────────────────┐
   │  JWT Token                         │
   │  {                                 │
   │    "sub": "admin",                 │
   │    "exp": "2025-10-27T08:00:00Z"   │
   │  }                                 │
   │  Signed with SECRET_KEY (HS256)    │
   └────────────────┬───────────────────┘
                    │
                    ▼
4. Return token to client
   ┌──────────┐◀─── {access_token, type} ───┐
   │  Browser │                              │
   └────┬─────┘                              │
        │                                    │
        │  Store token in memory             │
        │                                    │
        ▼                                    │

┌─────────────────────────────────────────────────────────────────────────┐
│                        Authorization Flow                                │
└─────────────────────────────────────────────────────────────────────────┘

Search Request with Auth:

1. Send request with token
   ┌──────────┐
   │  Browser │ ─── POST /ask ───────────────▶ ┌────────────────┐
   └──────────┘    Authorization: Bearer <JWT>  │  API Endpoint  │
                                                 └────────┬───────┘
                                                          │
2. Verify JWT                                             │
   ┌───────────────────────┐                             │
   │  JWT Middleware       │◀────────────────────────────┘
   │  • Decode token       │
   │  • Verify signature   │
   │  • Check expiration   │
   └────────┬──────────────┘
            │
            ▼
3. Extract user info
   ┌───────────────────────────┐
   │  Current User             │
   │  {                        │
   │    username: "admin",     │
   │    roles: ["admin",       │
   │            "legal",       │
   │            "staff"]       │
   │  }                        │
   └────────┬──────────────────┘
            │
            ▼
4. Get effective roles (hierarchy)
   ┌────────────────────────────────────┐
   │  Role Hierarchy                    │
   │  • admin → [admin, legal, staff]   │
   │  • legal → [legal, staff]          │
   │  • staff → [staff]                 │
   └────────┬───────────────────────────┘
            │
            ▼
5. Perform search with roles
   ┌────────────────────────────────────┐
   │  Retrieval Engine                  │
   │  search(query, roles=[admin, ...]) │
   └────────┬───────────────────────────┘
            │
            ▼
6. Filter results by RBAC
   ┌──────────────────────────────────────────────────┐
   │  For each document:                              │
   │  ┌────────────────────────────────────────────┐  │
   │  │  if "restricted" in doc_id:                │  │
   │  │    if user_roles ∩ {legal, admin}:         │  │
   │  │      ✅ ALLOW                               │  │
   │  │    else:                                   │  │
   │  │      ❌ DENY (hidden)                       │  │
   │  │  else:                                     │  │
   │  │    ✅ ALLOW (general document)             │  │
   │  └────────────────────────────────────────────┘  │
   └──────────────────────────────────────────────────┘
            │
            ▼
7. Return filtered results
   ┌──────────┐◀─── {results, accessible_count} ───┐
   │  Browser │                                     │
   └──────────┘                                     │

┌─────────────────────────────────────────────────────────────────────────┐
│                        Role-Based Access Matrix                          │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────┬──────────┬──────────┬───────────────────┐
│  Document     │  Staff   │  Legal   │  Admin            │
├───────────────┼──────────┼──────────┼───────────────────┤
│  General      │    ✅    │    ✅    │      ✅           │
│  Docs         │          │          │                   │
├───────────────┼──────────┼──────────┼───────────────────┤
│  Restricted   │    ❌    │    ✅    │      ✅           │
│  Docs         │          │          │                   │
├───────────────┼──────────┼──────────┼───────────────────┤
│  User         │    ❌    │    ❌    │      ✅           │
│  Management   │          │          │                   │
└───────────────┴──────────┴──────────┴───────────────────┘
```

---

### Search & Retrieval Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Complete Search Pipeline                              │
└─────────────────────────────────────────────────────────────────────────┘

                          User Query
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: Query Preprocessing                                           │
│                                                                          │
│  Input: "ما هو حد مسؤولية المشغل؟"                                      │
│                                                                          │
│  ┌──────────────────┐     ┌──────────────────┐     ┌─────────────────┐ │
│  │  Tokenization    │────▶│  Normalization   │────▶│  Synonym        │ │
│  │  • Split words   │     │  • Remove        │     │  Expansion      │ │
│  │  • Extract terms │     │    diacritics    │     │  • Add 2 syns   │ │
│  └──────────────────┘     │  • Handle Alef   │     │  • From gloss.  │ │
│                           └──────────────────┘     └─────────────────┘ │
│                                                                          │
│  Output: Tokens + Synonyms                                              │
│  • Original: ["ما", "هو", "حد", "مسؤولية", "المشغل"]                   │
│  • Synonyms: ["المسؤولية المدنية", "الالتزام"]                          │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: Multi-Index Search (Parallel Execution)                       │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  PATH A: BM25 Keyword Search                                      │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │  1. Tokenize query                                       │    │  │
│  │  │  2. Calculate TF-IDF scores                              │    │  │
│  │  │  3. Rank documents by BM25Okapi                          │    │  │
│  │  │  4. Return top-50 candidates                             │    │  │
│  │  └──────────────────────────────────────────────────────────┘    │  │
│  │                                                                   │  │
│  │  Results: [(doc_id=3, score=0.85), (doc_id=7, score=0.72), ...]  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  PATH B: mE5 Semantic Search                                      │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │  1. Encode query with mE5 model                          │    │  │
│  │  │     → 768-dimensional vector                             │    │  │
│  │  │  2. Search FAISS index (Inner Product)                   │    │  │
│  │  │  3. Return top-50 candidates with similarity scores      │    │  │
│  │  └──────────────────────────────────────────────────────────┘    │  │
│  │                                                                   │  │
│  │  Results: [(doc_id=5, score=0.92), (doc_id=3, score=0.88), ...]  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  PATH C: AraBERT Semantic Search                                  │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │  1. Encode query with AraBERT model                      │    │  │
│  │  │     → 768-dimensional vector (Arabic-optimized)          │    │  │
│  │  │  2. Search AraBERT FAISS index                           │    │  │
│  │  │  3. Return top-50 candidates with similarity scores      │    │  │
│  │  └──────────────────────────────────────────────────────────┘    │  │
│  │                                                                   │  │
│  │  Results: [(doc_id=5, score=0.89), (doc_id=8, score=0.86), ...]  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: Score Fusion                                                  │
│                                                                          │
│  Method 1: Weighted Fusion                                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  For each unique document:                                       │  │
│  │  1. Get scores from all indices (BM25, mE5, AraBERT)             │  │
│  │  2. Normalize scores to [0, 1]                                   │  │
│  │  3. Apply weighted combination:                                  │  │
│  │     final_score = 0.7 × mE5_score +                             │  │
│  │                  0.3 × AraBERT_score +                          │  │
│  │                  0.0 × BM25_score (optional)                    │  │
│  │  4. Sort by final_score                                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Method 2: Reciprocal Rank Fusion (RRF)                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  For each unique document:                                       │  │
│  │  1. Get rank from each index                                     │  │
│  │  2. Calculate RRF score:                                         │  │
│  │     RRF_score = Σ (1 / (k + rank_i))  where k=60                │  │
│  │  3. Sort by RRF_score                                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Output: Top-50 candidates with fused scores                            │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: BGE Reranking (Quality Booster)                               │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  BAAI/bge-reranker-v2-m3 Cross-Encoder                           │  │
│  │                                                                   │  │
│  │  For each of top-50 candidates:                                  │  │
│  │  1. Create query-document pair:                                  │  │
│  │     ["ما هو حد مسؤولية المشغل؟", document_text]                 │  │
│  │                                                                   │  │
│  │  2. Encode pair jointly with BGE model                           │  │
│  │     → Single relevance score                                     │  │
│  │                                                                   │  │
│  │  3. Combine with original score:                                 │  │
│  │     combined = 0.7 × BGE_score + 0.3 × original_score           │  │
│  │                                                                   │  │
│  │  4. Sort by combined score                                       │  │
│  │                                                                   │  │
│  │  5. Return top-K results (K=5 default)                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Expected improvement: 10-20% better precision                          │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 5: RBAC Filtering                                                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  For each document in results:                                   │  │
│  │                                                                   │  │
│  │  IF doc_id contains "restricted":                                │  │
│  │    IF user_roles ∩ {legal, admin} ≠ ∅:                          │  │
│  │      INCLUDE in results  ✅                                       │  │
│  │    ELSE:                                                         │  │
│  │      EXCLUDE from results  ❌                                     │  │
│  │  ELSE:                                                           │  │
│  │    INCLUDE in results  ✅ (general document)                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Track: total_found vs accessible_results                               │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 6: Result Highlighting                                           │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  For each document excerpt:                                      │  │
│  │                                                                   │  │
│  │  1. Find exact matches (yellow highlighting):                    │  │
│  │     • Query terms: "حد", "مسؤولية", "المشغل"                     │  │
│  │     • Mark with: <mark style="background:yellow">...</mark>     │  │
│  │                                                                   │  │
│  │  2. Find semantic matches (green highlighting):                  │  │
│  │     • Synonym terms: "المسؤولية المدنية", "الالتزام"             │  │
│  │     • Mark with: <mark style="background:lightgreen">...</mark>  │  │
│  │                                                                   │  │
│  │  3. Show actual found words (preserve case and form)             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Example output:                                                         │
│  "يتحمل <mark style='background:yellow'>المشغل</mark>                  │
│   <mark style='background:lightgreen'>المسؤولية المدنية</mark> عن       │
│   <mark style='background:yellow'>الأضرار</mark> النووية..."           │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 7: Response Generation                                           │
│                                                                          │
│  {                                                                       │
│    "answer": "<highlighted excerpt from top result>",                   │
│    "citations": [                                                        │
│      {                                                                   │
│        "rank": 1,                                                        │
│        "doc_id": "Law of Civil Liability for Nuclear Damage",           │
│        "article_no": "Article 5",                                        │
│        "page_start": 12,                                                 │
│        "page_end": 13,                                                   │
│        "score": 0.94,                                                    │
│        "excerpt": "<highlighted text with yellow & green marks>"        │
│      },                                                                  │
│      ...                                                                 │
│    ],                                                                    │
│    "user_roles": ["legal", "staff"],                                    │
│    "total_found": 15,                                                    │
│    "accessible_results": 12                                              │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Quality Boosters Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│              Week-2 Quality Boosters Architecture                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  Booster 1: Synonym Expansion                                           │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Glossary Structure (glossary_ar.json)                           │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │  {                                                          │  │  │
│  │  │    "المسؤولية": [                                           │  │  │
│  │  │      "المسؤولية المدنية",                                   │  │  │
│  │  │      "المسؤولية القانونية",                                 │  │  │
│  │  │      "الالتزام"                                             │  │  │
│  │  │    ],                                                       │  │  │
│  │  │    "النووي": ["النووية", "الذرية", "الإشعاعي"],            │  │  │
│  │  │    ...                                                      │  │  │
│  │  │  }                                                          │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Query Processing:                                                       │
│  Original: "ما هي المسؤولية النووية؟"                                   │
│     │                                                                    │
│     ▼                                                                    │
│  1. Tokenize: ["ما", "هي", "المسؤولية", "النووية"]                     │
│  2. Match tokens to glossary                                            │
│  3. Add max 2 synonyms per term                                         │
│     │                                                                    │
│     ▼                                                                    │
│  Expanded: "ما هي المسؤولية النووية المسؤولية المدنية الالتزام         │
│             النووية الذرية الإشعاعي"                                    │
│                                                                          │
│  Benefits:                                                               │
│  • Avoid missing relevant documents                                     │
│  • Controlled expansion (max 2 synonyms)                                │
│  • Domain-specific glossary (legal + nuclear terms)                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  Booster 2: AraBERT Integration (Second Embedding Index)                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Model: aubmindlab/bert-base-arabertv2                           │  │
│  │  • Arabic-native BERT model                                      │  │
│  │  • Pre-trained on Arabic corpus (70GB+)                          │  │
│  │  • Better Arabic morphology understanding                        │  │
│  │  • 768-dimensional embeddings                                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Dual-Index Architecture:                                               │
│  ┌──────────────────┐              ┌──────────────────┐                │
│  │  mE5 Index       │              │  AraBERT Index   │                │
│  │  • Multilingual  │              │  • Arabic-native │                │
│  │  • 100+ langs    │              │  • Single lang   │                │
│  │  • General       │              │  • Specialized   │                │
│  └────────┬─────────┘              └────────┬─────────┘                │
│           │                                 │                           │
│           │        Query Encoding           │                           │
│           │      ┌──────────────┐           │                           │
│           │      │  "ما هي      │           │                           │
│           └─────▶│  المسؤولية"  │◀──────────┘                           │
│                  └──────┬───────┘                                       │
│                         │                                               │
│                  ┌──────▼───────┐                                       │
│                  │  FAISS Search│                                       │
│                  │  (Parallel)  │                                       │
│                  └──────┬───────┘                                       │
│                         │                                               │
│                  ┌──────▼────────────────────────┐                      │
│                  │  Score Fusion                 │                      │
│                  │  • 0.7 × mE5_score           │                      │
│                  │  • 0.3 × AraBERT_score       │                      │
│                  │  = Combined Score            │                      │
│                  └───────────────────────────────┘                      │
│                                                                          │
│  Benefits:                                                               │
│  • Better Arabic semantic understanding                                 │
│  • Complementary to mE5 (multilingual)                                  │
│  • Optimal weight: 0.7 mE5 / 0.3 AraBERT                               │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  Booster 3: BGE Reranker (BAAI/bge-reranker-v2-m3)                     │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Model Architecture: Cross-Encoder                               │  │
│  │  • Joint encoding of query + document                           │  │
│  │  │  More accurate than bi-encoder (separate encoding)          │  │
│  │  • Multilingual: 100+ languages including Arabic                │  │
│  │  • Fine-tuned on relevance tasks                                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Reranking Pipeline:                                                    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 1: Get Top-50 Candidates                                  │   │
│  │  From hybrid search (BM25 + mE5 + AraBERT)                      │   │
│  └──────────────────┬──────────────────────────────────────────────┘   │
│                     ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 2: Create Query-Document Pairs                            │   │
│  │  [                                                               │   │
│  │    ["query", "doc1_text"],                                       │   │
│  │    ["query", "doc2_text"],                                       │   │
│  │    ...                                                           │   │
│  │    ["query", "doc50_text"]                                       │   │
│  │  ]                                                               │   │
│  └──────────────────┬──────────────────────────────────────────────┘   │
│                     ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 3: BGE Cross-Encoder Scoring                              │   │
│  │  ┌───────────────────────────────────────────────────────────┐  │   │
│  │  │  Input: [CLS] query [SEP] document [SEP]                   │  │   │
│  │  │          ↓                                                  │  │   │
│  │  │  Transformer Layers (joint attention)                      │  │   │
│  │  │          ↓                                                  │  │   │
│  │  │  Relevance Score: 0.0 to 1.0                               │  │   │
│  │  └───────────────────────────────────────────────────────────┘  │   │
│  └──────────────────┬──────────────────────────────────────────────┘   │
│                     ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 4: Score Fusion                                           │   │
│  │  combined_score = 0.7 × BGE_rerank_score +                     │   │
│  │                   0.3 × original_fusion_score                   │   │
│  └──────────────────┬──────────────────────────────────────────────┘   │
│                     ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 5: Sort and Return Top-K                                  │   │
│  │  • Top-K results (K=5 default)                                  │   │
│  │  • 10-20% precision improvement                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Benefits:                                                               │
│  • More accurate relevance scoring                                      │
│  • Better handling of query-document semantics                         │
│  • Significant precision boost (10-20%)                                │
│  • Production-ready performance (<200ms with top-50 candidates)         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Component Details

### 4.1 Core Components

| Component | Technology | Purpose | Location |
|-----------|-----------|---------|----------|
| **Web Server** | FastAPI | REST API & UI serving | `app/run_api.py` |
| **Authentication** | JWT + bcrypt | User auth & session mgmt | `app/auth.py` |
| **Retrieval Engine** | BM25 + FAISS | Hybrid search | `app/retrieval.py` |
| **Enhanced Retrieval** | Multi-stage pipeline | Quality boosters | `app/enhanced_retrieval.py` |
| **Normalization** | Arabic text processing | Text preprocessing | `app/normalize.py` |
| **Chunking** | Sliding window | Document chunking | `app/chunking.py` |

### 4.2 ML/AI Components

| Component | Model | Purpose | Dimensions |
|-----------|-------|---------|------------|
| **mE5 Embeddings** | intfloat/multilingual-e5-base | Semantic search (multilingual) | 768 |
| **AraBERT Embeddings** | aubmindlab/bert-base-arabertv2 | Arabic-native semantic search | 768 |
| **BGE Reranker** | BAAI/bge-reranker-v2-m3 | Relevance reranking | Cross-encoder |
| **BM25** | rank-bm25 | Keyword search | N/A |

### 4.3 Data Components

| Component | Format | Purpose | Size (5-6 PDFs) |
|-----------|--------|---------|-----------------|
| **BM25 Index** | Pickle | Keyword search index | ~5MB |
| **mE5 FAISS** | Binary | Semantic search index | ~50MB |
| **AraBERT FAISS** | Binary | Arabic semantic index | ~50MB |
| **Metadata** | JSON | Document metadata | ~5MB |
| **Glossary** | JSON | Synonym expansion | ~50KB |
| **Raw PDFs** | PDF | Source documents | ~20MB |
| **Processed Chunks** | JSONL | Chunked text | ~2MB |

---

## 5. Deployment Architecture

### 5.1 Docker Deployment

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Docker Deployment                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│  Docker Host                                                              │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Docker Container: nrrc-arabic-pov                                 │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │  Application Layer                                           │ │ │
│  │  │  • FastAPI Server (Port 8000)                               │ │ │
│  │  │  • Python 3.11                                              │ │ │
│  │  │  • All dependencies                                         │ │ │
│  │  └──────────────────────────────────────────────────────────────┘ │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │  ML Models (cached)                                          │ │ │
│  │  │  • mE5 Model                                                │ │ │
│  │  │  • AraBERT Model                                            │ │ │
│  │  │  • BGE Reranker                                             │ │ │
│  │  └──────────────────────────────────────────────────────────────┘ │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │  Mounted Volumes                                             │ │ │
│  │  │  • ./data → /app/data (Persistent)                          │ │ │
│  │  │  • ./conf → /app/conf (Config)                              │ │ │
│  │  └──────────────────────────────────────────────────────────────┘ │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │  Health Check                                                │ │ │
│  │  │  • Endpoint: /health                                        │ │ │
│  │  │  • Interval: 30s                                            │ │ │
│  │  └──────────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                             ▲                                            │
│                             │                                            │
│                   Port Mapping: 8000:8000                                │
└──────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │  External Access   │
                    │  http://host:8000  │
                    └────────────────────┘
```

### 5.2 Standalone Deployment

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Standalone Windows Deployment                       │
└─────────────────────────────────────────────────────────────────────────┘

Windows Machine
├── Python 3.11 Installation
├── Virtual Environment (.venv)
│   ├── Dependencies (requirements.txt)
│   │   ├── FastAPI
│   │   ├── Uvicorn
│   │   ├── Sentence-Transformers
│   │   ├── PyTorch
│   │   ├── FAISS-CPU
│   │   └── ...
│   └── ML Models (cached in ~/.cache/huggingface)
│
├── Project Directory (D:\nrrc_arabic_pov_windows)
│   ├── app/
│   │   ├── run_api.py
│   │   ├── auth.py
│   │   ├── retrieval.py
│   │   ├── enhanced_retrieval.py
│   │   └── ...
│   ├── data/
│   │   ├── raw_pdfs/
│   │   ├── processed/
│   │   └── idx/
│   ├── conf/
│   │   └── glossary_ar.json
│   ├── scripts/
│   └── requirements.txt
│
└── Run Command:
    uvicorn app.run_api:app --host 0.0.0.0 --port 8000 --reload
```

---

## 6. Security Architecture

### 6.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Security Architecture                             │
└─────────────────────────────────────────────────────────────────────────┘

Layer 1: Network Security
├── HTTPS (Production)
├── CORS Configuration
└── Port Restrictions (8000 only)

Layer 2: Authentication
├── JWT Tokens (HS256)
│   ├── Expiration: 30 minutes
│   ├── Secure signing (SECRET_KEY)
│   └── Bearer token in Authorization header
└── Password Hashing (bcrypt)
    ├── Salt rounds: 12
    └── One-way encryption

Layer 3: Authorization (RBAC)
├── Role Hierarchy
│   ├── Admin: Full access
│   ├── Legal: Restricted + General
│   └── Staff: General only
├── Document-Level Control
│   ├── File name detection ("restricted" keyword)
│   └── Role-based filtering
└── API Endpoint Protection
    ├── JWT verification on all endpoints
    └── Role checking with Depends()

Layer 4: Data Security
├── Local Storage Only (No cloud)
├── Offline Operation
├── Encrypted passwords (bcrypt)
└── No sensitive data in logs

Layer 5: Session Security
├── Token expiration (30 min)
├── Logout functionality
├── No persistent sessions
└── Client-side token storage (memory only)
```

### 6.2 RBAC Implementation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     RBAC Implementation Details                          │
└─────────────────────────────────────────────────────────────────────────┘

Users Database:
┌───────────┬────────────────────┬──────────────────────────────────────┐
│ Username  │ Roles              │ Password (bcrypt hash)               │
├───────────┼────────────────────┼──────────────────────────────────────┤
│ admin     │ [admin,legal,staff]│ $2b$12$...                          │
│ legal     │ [legal, staff]     │ $2b$12$...                          │
│ staff     │ [staff]            │ $2b$12$...                          │
└───────────┴────────────────────┴──────────────────────────────────────┘

Document Access Rules:
┌────────────────────────────────────────────────────────────────────────┐
│  Document Filename Check:                                              │
│                                                                        │
│  IF "restricted" in filename.lower():                                 │
│    REQUIRED_ROLES = {legal, admin}                                    │
│    IF user_roles ∩ REQUIRED_ROLES ≠ ∅:                               │
│      ✅ ALLOW ACCESS                                                   │
│    ELSE:                                                              │
│      ❌ DENY ACCESS (document hidden from results)                    │
│  ELSE:                                                                │
│    ✅ ALLOW ACCESS (general document, all roles)                      │
└────────────────────────────────────────────────────────────────────────┘

API Endpoint Security:
┌────────────────────────────────────────────────────────────────────────┐
│  @app.post("/ask")                                                     │
│  async def ask(                                                        │
│      payload: AskPayload,                                             │
│      current_user: User = Depends(get_current_user)  # JWT verify    │
│  ):                                                                    │
│      # User automatically authenticated here                          │
│      # Roles extracted from JWT token                                │
│      ...                                                              │
│                                                                        │
│  @app.get("/users")                                                   │
│  async def list_users(                                                │
│      current_user: User = Depends(require_roles(["admin"]))  # Admin only │
│  ):                                                                    │
│      # Only admin users can access this endpoint                     │
│      ...                                                              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Performance & Scalability

### 7.1 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Indexing Time** | 2-3 minutes | 5-6 PDFs with all indices |
| **Search Latency** | <200ms | With all quality boosters enabled |
| **Memory Usage** | ~1.5GB | mE5 + AraBERT + BGE reranker |
| **Storage** | ~150MB | All indices for 5-6 PDFs |
| **Precision Boost** | 10-20% | With BGE reranker enabled |
| **Throughput** | ~50 req/sec | Single instance (CPU) |

### 7.2 Scalability Considerations

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Scalability Architecture                          │
└─────────────────────────────────────────────────────────────────────────┘

Vertical Scaling:
├── CPU: Multi-core for parallel search
├── RAM: 4GB+ recommended (8GB for large document sets)
├── Storage: SSD recommended for FAISS index access
└── GPU: Optional (for faster embedding & reranking)

Horizontal Scaling:
├── Load Balancer
│   └── Multiple FastAPI instances
├── Shared Storage
│   ├── Network file system for indices
│   └── Read-only access to models
└── Stateless Design
    ├── JWT tokens (no server-side sessions)
    └── Independent request handling

Optimization Strategies:
├── Index Sharding (for very large document sets)
├── Caching
│   ├── Query embedding caching
│   ├── Frequent query results caching
│   └── Model caching
├── Batch Processing
│   ├── Parallel candidate retrieval
│   └── Batch reranking
└── Hardware Acceleration
    ├── GPU for embeddings (if available)
    └── FAISS GPU indices (for large scale)
```

### 7.3 Performance Optimization

**Query Optimization:**
- Cache frequently used query embeddings
- Limit candidate pool (top-50 for reranking)
- Parallel index search (BM25, mE5, AraBERT)

**Index Optimization:**
- Use FAISS IndexIVF for large document sets (>100k docs)
- Quantization for reduced memory footprint
- Index compression for faster disk I/O

**Model Optimization:**
- Use ONNX runtime for faster inference
- Batch prediction for reranking
- Mixed precision (FP16) for GPU inference

---

## Conclusion

This design document provides a comprehensive view of the NRRC Arabic PoV system architecture, covering:

1. **C4 Architecture**: From system context to code-level diagrams
2. **System Design**: Complete pipeline flows and component interactions
3. **Security**: Multi-layer security with RBAC implementation
4. **Performance**: Metrics and optimization strategies
5. **Quality Boosters**: Week-2 enhancements with BGE reranker, AraBERT, and synonym expansion

The system is designed for:
- **Enterprise-grade reliability**: Offline operation, RBAC security
- **High accuracy**: Hybrid search + AI reranking (10-20% boost)
- **Arabic-native support**: AraBERT integration, RTL interface
- **Scalability**: Stateless design, horizontal scaling ready

For implementation details, refer to the source code in the `app/` directory.

---

**End of Document**
