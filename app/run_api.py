from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, Response
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import os, json
from .retrieval import load_bm25, load_faiss, load_meta, load_model, Indices, search
from .auth import (
    User, UserCreate, UserLogin, Token, authenticate_user, create_access_token,
    get_current_user, require_roles, check_file_access, filter_documents_by_access,
    get_effective_roles, ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

# ---- Paths ----
BM25_PATH = "data/idx/bm25.pkl"
FAISS_PATH = "data/idx/mE5.faiss"
META_PATH = "data/idx/meta.json"
MODEL_NAME = "intfloat/multilingual-e5-base"

app = FastAPI(title="Arabic Legal Q&A")

indices: Indices | None = None


class AskPayload(BaseModel):
    query: str
    topk: int = 5

class LoginRequest(BaseModel):
    username: str
    password: str


@app.on_event("startup")
def load_all():
    global indices
    print("[Loading BM25 + FAISS + model...]")
    bm25 = load_bm25(BM25_PATH)
    faiss_index = load_faiss(FAISS_PATH)
    meta = load_meta(META_PATH)
    model = load_model(MODEL_NAME)
    indices = Indices(bm25=bm25, faiss_index=faiss_index, meta=meta, model=model)
    print("[OK] System ready")


@app.get("/health")
def health_check():
    """Health check endpoint for Docker"""
    if indices is None:
        return {"status": "loading", "message": "System is still loading"}
    return {"status": "healthy", "message": "System is ready"}


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🔍 تكستسكوب للذكاء الاصطناعي – بحث ذكي عن المستندات في مختلف المجالات ⚖️</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --primary-color: #1e40af;
  --primary-hover: #1d4ed8;
  --secondary-color: #64748b;
  --success-color: #059669;
  --warning-color: #d97706;
  --error-color: #dc2626;
  --background: #f8fafc;
  --card-bg: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Noto Sans Arabic', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: var(--background);
  color: var(--text-primary);
  direction: rtl;
  text-align: right;
  line-height: 1.6;
  min-height: 100vh;
}

.header {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  padding: 2rem 0;
  text-align: center;
  box-shadow: var(--shadow-lg);
  position: relative;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.header p {
  font-size: 1.1rem;
  opacity: 0.9;
  font-weight: 300;
}

.user-info {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  backdrop-filter: blur(10px);
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  cursor: pointer;
  margin-right: 0.5rem;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.container {
  max-width: 1200px;
  margin: -2rem auto 2rem;
  background: var(--card-bg);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  position: relative;
  z-index: 1;
}

.login-container {
  max-width: 400px;
  margin: 2rem auto;
  background: var(--card-bg);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: var(--shadow-lg);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-primary);
}

.form-group input {
  padding: 0.75rem 1rem;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

.login-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
}

.search-box {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: stretch;
}

#query {
  flex: 1;
  padding: 1rem 1.5rem;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  font-size: 1.1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  background: #fafbfc;
}

#query:focus {
  outline: none;
  border-color: var(--primary-color);
  background: white;
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

#searchBtn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: 120px;
}

#searchBtn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
}

#searchBtn:active {
  transform: translateY(0);
}

.loading {
  display: none;
  text-align: center;
  padding: 1.5rem;
  color: var(--primary-color);
  font-size: 1.1rem;
  font-weight: 500;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-left: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.results-section {
  margin-top: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--border-color);
}

#answer {
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  padding: 1.5rem;
  border-radius: 12px;
  border-right: 4px solid var(--primary-color);
  margin-bottom: 2rem;
  line-height: 1.8;
  font-size: 1.1rem;
  box-shadow: var(--shadow);
}

.citation-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
  position: relative;
}

.citation-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.citation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.doc-title {
  font-weight: 600;
  color: var(--primary-color);
  font-size: 1.1rem;
}

.doc-info {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.doc-info span {
  background: #f1f5f9;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  white-space: nowrap;
}

.citation-content {
  line-height: 1.8;
  font-size: 1.05rem;
}

/* Highlighting Styles */
mark {
  padding: 2px 6px;
  border-radius: 6px;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  position: relative;
}

mark[style*="yellow"] {
  background: linear-gradient(135deg, #fef08a, #fde047);
  color: #854d0e;
  border: 1px solid #eab308;
}

mark[style*="lightgreen"] {
  background: linear-gradient(135deg, #bbf7d0, #86efac);
  color: #14532d;
  border: 1px solid #22c55e;
}

.highlight-legend {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 0.9rem;
  justify-content: center;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid rgba(0,0,0,0.1);
}

.legend-yellow {
  background: linear-gradient(135deg, #fef08a, #fde047);
}

.legend-green {
  background: linear-gradient(135deg, #bbf7d0, #86efac);
}

.access-info {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #92400e;
}

@media (max-width: 768px) {
  .container {
    margin: -1rem 1rem 1rem;
    padding: 1.5rem;
  }
  
  .search-box {
    flex-direction: column;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .user-info {
    position: static;
    margin-bottom: 1rem;
  }
  
  .citation-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .doc-info {
    flex-wrap: wrap;
  }
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--text-secondary);
}

.empty-state .icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.examples-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.example-tags {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}

.example-tag {
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  color: #3730a3;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #c7d2fe;
  white-space: nowrap;
  user-select: none;
}

.example-tag:hover {
  background: linear-gradient(135deg, #c7d2fe, #a5b4fc);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.example-tag:active {
  transform: translateY(0);
}

.hidden {
  display: none !important;
}
</style>
</head>
<body>
<div class="header">
  <h1>🔍 تكست سكوب للذكاء الاصطناعي</h1>
  <p>البحث الذكي عن المستندات عبر المجالات</p>
  <div id="userInfo" class="user-info hidden">
    <span id="userName"></span>
    <span id="userRoles"></span>
    <button class="logout-btn" onclick="logout()">تسجيل الخروج</button>
  </div>
</div>

<div id="loginContainer" class="login-container">
  <h2 style="text-align: center; margin-bottom: 1.5rem; color: var(--primary-color);">تسجيل الدخول</h2>
  <form class="login-form" onsubmit="login(event)">
    <div class="form-group">
      <label for="username">اسم المستخدم:</label>
      <input type="text" id="username" required>
    </div>
    <div class="form-group">
      <label for="password">كلمة المرور:</label>
      <input type="password" id="password" required>
    </div>
    <button type="submit" class="login-btn">تسجيل الدخول</button>
  </form>
  <div style="margin-top: 1rem; padding: 1rem; background: #f8fafc; border-radius: 8px; font-size: 0.9rem;">
    <strong>حسابات تجريبية:</strong><br>
    • admin / admin123 (مدير النظام)<br>
    • legal / legal123 (مستشار قانوني)<br>
    • staff / staff123 (موظف عام)
  </div>
</div>

<div id="mainContainer" class="container hidden">
  <div class="search-box">
    <input id="query" type="text" placeholder="ابحث في الوثائق... مثال: ما هي الاتفاقيات النووية؟" autocomplete="off">
    <button id="searchBtn" onclick="askQuestion()">🔍 بحث</button>
  </div>
  
  <div id="accessInfo" class="access-info hidden">
    <strong>معلومات الصلاحيات:</strong> <span id="accessDetails"></span>
  </div>
  
  <div class="highlight-legend">
    <div class="legend-item">
      <div class="legend-color legend-yellow"></div>
      <span>تطابق مباشر في النص - عرض الكلمة الفعلية الموجودة</span>
    </div>
    <div class="legend-item">
      <div class="legend-color legend-green"></div>
      <span>مصطلحات ذات علاقة دلالية - مرادفات ومفاهيم مترابطة</span>
    </div>
  </div>
  
  <div class="examples-section">
    <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.75rem;">أمثلة للبحث:</h3>
    <div class="example-tags">
      <span class="example-tag" onclick="setQuery('obligations')">🔍 obligations</span>
      <span class="example-tag" onclick="setQuery('اتفاقية')">🔍 اتفاقية</span>
      <span class="example-tag" onclick="setQuery('الطاقة النووية')">🔍 الطاقة النووية</span>
      <span class="example-tag" onclick="setQuery('تعويض')">🔍 تعويض</span>
      <span class="example-tag" onclick="setQuery('ترخيص')">🔍 ترخيص</span>
    </div>
  </div>
  
  <div id="loading" class="loading">
    <span>جارٍ البحث في الوثائق</span>
    <div class="spinner"></div>
  </div>
  
  <div class="results-section">
    <h2 class="section-title" id="answerTitle" style="display:none;">📄 الإجابة الأساسية</h2>
    <div id="answer"></div>
    
    <h2 class="section-title" id="citationsTitle" style="display:none;">📚 المراجع والمصادر</h2>
    <div id="citations"></div>
  </div>
</div>

<script>
// Global variables
let currentUser = null;
let authToken = null;

// Authentication functions
async function login(event) {
  event.preventDefault();
  
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  try {
    const response = await fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'فشل تسجيل الدخول');
    }
    
    const data = await response.json();
    authToken = data.access_token;
    
    // Get user info
    const userResponse = await fetch('/me', {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });
    
    if (userResponse.ok) {
      currentUser = await userResponse.json();
      showMainInterface();
    } else {
      throw new Error('فشل في الحصول على معلومات المستخدم');
    }
    
  } catch (error) {
    showNotification(error.message, 'error');
  }
}

function logout() {
  currentUser = null;
  authToken = null;
  showLoginInterface();
  showNotification('تم تسجيل الخروج بنجاح', 'success');
}

function showLoginInterface() {
  document.getElementById('loginContainer').classList.remove('hidden');
  document.getElementById('mainContainer').classList.add('hidden');
  document.getElementById('userInfo').classList.add('hidden');
}

function showMainInterface() {
  document.getElementById('loginContainer').classList.add('hidden');
  document.getElementById('mainContainer').classList.remove('hidden');
  document.getElementById('userInfo').classList.remove('hidden');
  
  // Update user info display
  document.getElementById('userName').textContent = `مرحباً ${currentUser.full_name}`;
  document.getElementById('userRoles').textContent = `(${currentUser.roles.join(', ')})`;
  
  // Update access info
  const accessInfo = document.getElementById('accessInfo');
  const accessDetails = document.getElementById('accessDetails');
  
  if (currentUser.roles.includes('admin')) {
    accessDetails.textContent = 'لديك صلاحية الوصول لجميع الوثائق بما في ذلك الوثائق المقيدة';
    accessInfo.classList.remove('hidden');
  } else if (currentUser.roles.includes('legal')) {
    accessDetails.textContent = 'لديك صلاحية الوصول للوثائق العامة والوثائق المقيدة';
    accessInfo.classList.remove('hidden');
  } else {
    accessDetails.textContent = 'لديك صلاحية الوصول للوثائق العامة فقط';
    accessInfo.classList.remove('hidden');
  }
}

// Search functionality with authentication
async function askQuestion() {
  const query = document.getElementById("query").value.trim();
  const ans = document.getElementById("answer");
  const cites = document.getElementById("citations");
  const loading = document.getElementById("loading");
  const searchBtn = document.getElementById("searchBtn");
  const answerTitle = document.getElementById("answerTitle");
  const citationsTitle = document.getElementById("citationsTitle");

  if (!query) { 
    showNotification("يرجى إدخال سؤال أولاً", "warning");
    return; 
  }

  if (!authToken) {
    showNotification("يرجى تسجيل الدخول أولاً", "error");
    return;
  }

  // Reset UI state
  ans.innerHTML = "";
  cites.innerHTML = "";
  answerTitle.style.display = "none";
  citationsTitle.style.display = "none";
  
  // Show loading state
  loading.style.display = "block";
  searchBtn.disabled = true;
  searchBtn.innerHTML = "⏳ جاري البحث...";

  const payload = { query: query, topk: 8 };

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      if (res.status === 401) {
        showNotification("انتهت صلاحية الجلسة، يرجى تسجيل الدخول مرة أخرى", "error");
        logout();
        return;
      }
      throw new Error(`خطأ في الخادم: ${res.status}`);
    }

    const text = await res.text();
    const data = JSON.parse(text);

    // Hide loading
    loading.style.display = "none";
    searchBtn.disabled = false;
    searchBtn.innerHTML = "🔍 بحث";

    // Display answer
    if (data.answer && data.answer.trim()) {
      answerTitle.style.display = "block";
      ans.innerHTML = data.answer;
      
      // Add scroll to answer
      setTimeout(() => {
        ans.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 300);
    } else {
      ans.innerHTML = `
        <div class="empty-state">
          <div class="icon">🔍</div>
          <p>لم يتم العثور على نتائج مطابقة لاستعلامك.</p>
          <p style="font-size: 0.9rem; margin-top: 0.5rem;">جرب استخدام كلمات مختلفة أو أكثر تحديداً.</p>
        </div>
      `;
    }

    // Display citations with enhanced styling
    if (data.citations && data.citations.length > 0) {
      citationsTitle.style.display = "block";
      
      data.citations.forEach((c, index) => {
        const card = document.createElement("div");
        card.className = "citation-card";
        
        const header = document.createElement("div");
        header.className = "citation-header";
        
        const title = document.createElement("div");
        title.className = "doc-title";
        title.innerHTML = `📘 ${c.doc_id}`;
        
        const info = document.createElement("div");
        info.className = "doc-info";
        
        const articleSpan = document.createElement("span");
        articleSpan.innerHTML = `المادة: ${c.article_no || "غير محدد"}`;
        
        const pageSpan = document.createElement("span");
        pageSpan.innerHTML = `الصفحة: ${c.page_start || "?"}-${c.page_end || "?"}`;
        
        const scoreSpan = document.createElement("span");
        scoreSpan.innerHTML = `التطابق: ${Math.round((c.score || 0) * 100)}%`;
        scoreSpan.style.background = c.score > 0.7 ? "#dcfce7" : c.score > 0.4 ? "#fef3c7" : "#fee2e2";
        
        info.appendChild(articleSpan);
        info.appendChild(pageSpan);
        info.appendChild(scoreSpan);
        
        header.appendChild(title);
        header.appendChild(info);
        
        const content = document.createElement("div");
        content.className = "citation-content";
        content.innerHTML = c.excerpt || "لا يوجد محتوى متاح";
        
        card.appendChild(header);
        card.appendChild(content);
        
        // Add animation delay
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        cites.appendChild(card);
        
        setTimeout(() => {
          card.style.transition = "all 0.5s ease";
          card.style.opacity = "1";
          card.style.transform = "translateY(0)";
        }, index * 100);
      });
      
      let notificationText = `تم العثور على ${data.citations.length} نتيجة مطابقة`;
      if (data.total_found && data.total_found > data.accessible_results) {
        notificationText += ` (${data.total_found - data.accessible_results} نتيجة مقيدة)`;
      }
      showNotification(notificationText, "success");
    }
    
  } catch (err) {
    console.error('Search error:', err);
    loading.style.display = "none";
    searchBtn.disabled = false;
    searchBtn.innerHTML = "🔍 بحث";
    
    ans.innerHTML = `
      <div class="empty-state">
        <div class="icon">⚠️</div>
        <p>حدث خطأ أثناء البحث</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">${err.message}</p>
      </div>
    `;
    
    showNotification("حدث خطأ أثناء البحث. يرجى المحاولة مرة أخرى.", "error");
  }
}

// Enhanced notification system
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 1000;
    max-width: 300px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transform: translateX(100%);
    transition: transform 0.3s ease;
  `;
  
  const colors = {
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626',
    info: '#0284c7'
  };
  
  notification.style.background = colors[type] || colors.info;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Slide in
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 100);
  
  // Slide out and remove
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

// Enhanced keyboard support
document.addEventListener('DOMContentLoaded', function() {
  // Auto-focus on username input
  document.getElementById("username").focus();
});

document.getElementById("query").addEventListener("keypress", function(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    askQuestion();
  }
});

// Clear search results when input changes significantly
let lastQuery = "";
document.getElementById("query").addEventListener("input", function(e) {
  const currentQuery = e.target.value.trim();
  if (lastQuery && currentQuery.length < lastQuery.length * 0.5) {
    // If user deleted significant portion, clear results
    document.getElementById("answer").innerHTML = "";
    document.getElementById("citations").innerHTML = "";
    document.getElementById("answerTitle").style.display = "none";
    document.getElementById("citationsTitle").style.display = "none";
  }
  lastQuery = currentQuery;
});

// Set example query and search
function setQuery(exampleQuery) {
  const queryInput = document.getElementById("query");
  queryInput.value = exampleQuery;
  queryInput.focus();
  
  // Add a small animation to show the query was set
  queryInput.style.background = "#dbeafe";
  setTimeout(() => {
    queryInput.style.background = "#fafbfc";
  }, 500);
  
  // Auto-search after setting the query
  setTimeout(() => {
    askQuestion();
  }, 200);
}
</script>
</body></html>
""")


# Authentication endpoints
@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login endpoint to get access token"""
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/users", response_model=list[User])
async def list_users(current_user: User = Depends(require_roles(["admin"]))):
    """List all users (admin only)"""
    from .auth import USERS_DB
    users = []
    for user_data in USERS_DB.values():
        users.append(User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            roles=user_data["roles"],
            is_active=user_data["is_active"]
        ))
    return users

@app.post("/ask", response_class=Response)
async def ask(payload: AskPayload, current_user: User = Depends(get_current_user)):
    """
    Search endpoint with RBAC - Return manual JSON string (NOT auto-escaped).
    """
    # Get effective roles for the user
    effective_roles = get_effective_roles(current_user.roles)
    
    # Perform search with user's roles
    out = search(indices, payload.query, effective_roles, topk=payload.topk)
    
    # Filter results based on file access restrictions
    filtered_results = filter_documents_by_access(current_user.roles, out["results"])
    
    # Update the answer if no results remain after filtering
    if not filtered_results and out["results"]:
        answer_html = "لم يتم العثور على نتائج متاحة بناءً على صلاحياتك الحالية."
    else:
        answer_html = out["answer"]
    
    raw_json = json.dumps({
        "answer": answer_html, 
        "citations": filtered_results,
        "user_roles": current_user.roles,
        "total_found": len(out["results"]),
        "accessible_results": len(filtered_results)
    }, ensure_ascii=False)
    
    # ✅ return as plain response so <mark> isn't escaped
    return Response(content=raw_json, media_type="application/json")
