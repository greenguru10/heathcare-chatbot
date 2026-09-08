import { ChatMessage, SourceItem, CategoryItem, DocumentItem } from '../types';

const VITE_API = (import.meta as any).env?.VITE_API_URL;
const API_BASE = (VITE_API ? `${VITE_API}/api/v1` : '/api/v1').replace(/\/+$/, '');

export async function sendChatMessage(message: string, sessionId?: string, locale: string = 'en-IN') {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId, locale })
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || errData.error || `Error ${res.status}`);
  }
  return res.json();
}

export async function fetchSources(): Promise<SourceItem[]> {
  const res = await fetch(`${API_BASE}/sources`);
  if (!res.ok) throw new Error('Failed to load sources');
  return res.json();
}

export async function fetchCategories(): Promise<CategoryItem[]> {
  const res = await fetch(`${API_BASE}/categories`);
  if (!res.ok) throw new Error('Failed to load categories');
  return res.json();
}

export async function fetchDocuments(status?: string, category?: string, page: number = 1): Promise<{ items: DocumentItem[]; total: number }> {
  const params = new URLSearchParams();
  if (status) params.set('status', status);
  if (category) params.set('category', category);
  params.set('page', page.toString());
  
  const res = await fetch(`${API_BASE}/documents?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to load documents');
  return res.json();
}

export async function fetchDocumentDetail(docId: string) {
  const res = await fetch(`${API_BASE}/documents/${docId}`);
  if (!res.ok) throw new Error('Failed to load document detail');
  return res.json();
}

export async function updateDocumentStatus(docId: string, status: string, adminKey: string) {
  const res = await fetch(`${API_BASE}/documents/${docId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': adminKey
    },
    body: JSON.stringify({ status })
  });
  if (!res.ok) throw new Error('Failed to update document status');
  return res.json();
}

export async function triggerReindex(adminKey: string) {
  const res = await fetch(`${API_BASE}/reindex`, {
    method: 'POST',
    headers: { 'X-API-Key': adminKey }
  });
  if (!res.ok) throw new Error('Failed to trigger reindex');
  return res.json();
}

export async function submitFeedback(answerId: string, rating: number, feedbackType: string, comment?: string) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      answer_id: answerId,
      rating,
      feedback_type: feedbackType,
      comment
    })
  });
  if (!res.ok) throw new Error('Failed to submit feedback');
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health');
  return res.json();
}

export async function fetchSessions(): Promise<import('../types').SessionSummary[]> {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error('Failed to fetch chat sessions');
  return res.json();
}

export async function createSession(title?: string): Promise<import('../types').SessionSummary> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
  if (!res.ok) throw new Error('Failed to create chat session');
  return res.json();
}

export async function fetchSessionDetail(sessionId: string): Promise<import('../types').SessionDetail> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) throw new Error('Failed to fetch session detail');
  return res.json();
}

export async function renameSession(sessionId: string, title: string): Promise<import('../types').SessionDetail> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
  if (!res.ok) throw new Error('Failed to rename session');
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete session');
}

export async function deleteAllSessions(): Promise<void> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to clear chat sessions');
}
