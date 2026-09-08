import React, { useState, useEffect } from 'react';
import { DocumentItem, SourceItem, CategoryItem } from '../types';
import {
  fetchDocuments,
  fetchDocumentDetail,
  updateDocumentStatus,
  triggerReindex,
  fetchSources,
  fetchCategories
} from '../api/client';
import {
  ShieldCheck,
  Upload,
  RefreshCw,
  FileText,
  CheckCircle,
  AlertTriangle,
  Layers,
  Search,
  Eye,
  X,
  Play
} from 'lucide-react';

export const AdminPage: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [adminKey, setAdminKey] = useState('health_rag_admin_secret_key_2026');

  // Selected document detail modal
  const [selectedDoc, setSelectedDoc] = useState<any | null>(null);
  const [inspectModalOpen, setInspectModalOpen] = useState(false);

  // Upload modal state
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadSourceId, setUploadSourceId] = useState('');
  const [uploadCategoryId, setUploadCategoryId] = useState<number>(1);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploading, setUploading] = useState(false);

  // Retrieval tester state
  const [testQuery, setTestQuery] = useState('What is blood pressure?');
  const [testResults, setTestResults] = useState<any | null>(null);
  const [testingRetrieval, setTestingRetrieval] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [docsResp, srcs, cats] = await Promise.all([
        fetchDocuments(),
        fetchSources(),
        fetchCategories()
      ]);
      setDocuments(docsResp.items);
      setSources(srcs);
      setCategories(cats);
      if (srcs.length > 0) setUploadSourceId(srcs[0].id);
      if (cats.length > 0) setUploadCategoryId(cats[0].id);
    } catch (err) {
      console.error('Failed to load admin data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStatusChange = async (docId: string, newStatus: string) => {
    try {
      await updateDocumentStatus(docId, newStatus, adminKey);
      await loadData();
    } catch (err: any) {
      alert(`Error updating document status: ${err.message}`);
    }
  };

  const handleReindex = async () => {
    try {
      const res = await triggerReindex(adminKey);
      alert(`Reindexing successful! ${res.active_chunks_indexed} active chunks indexed.`);
    } catch (err: any) {
      alert(`Reindexing failed: ${err.message}`);
    }
  };

  const handleInspect = async (docId: string) => {
    try {
      const detail = await fetchDocumentDetail(docId);
      setSelectedDoc(detail);
      setInspectModalOpen(true);
    } catch (err) {
      alert('Failed to load document details');
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('source_id', uploadSourceId);
    formData.append('category_id', uploadCategoryId.toString());
    if (uploadTitle) formData.append('title', uploadTitle);

    try {
      const res = await fetch('/api/v1/documents', {
        method: 'POST',
        headers: { 'X-API-Key': adminKey },
        body: formData
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }
      setUploadModalOpen(false);
      setUploadFile(null);
      setUploadTitle('');
      await loadData();
      alert('Document uploaded and ingested successfully!');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setUploading(false);
    }
  };

  const runTestQuery = async () => {
    if (!testQuery.trim()) return;
    setTestingRetrieval(true);
    try {
      const res = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: testQuery, locale: 'en-IN' })
      });
      const data = await res.json();
      setTestResults(data);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setTestingRetrieval(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2.5 text-teal-800">
            <div className="p-2 bg-teal-100 text-teal-800 rounded-xl shadow-2xs">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight font-display">
              Clinical Governance & Document Lifecycle
            </h1>
          </div>
          <p className="text-xs text-slate-600 mt-1">
            Manage approved medical knowledge sources, inspect parsed chunks, and test hybrid retrieval.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setUploadModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold rounded-xl shadow-xs transition-all active:scale-95"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Document</span>
          </button>
          <button
            onClick={handleReindex}
            className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-semibold rounded-xl shadow-2xs transition-all hover:border-teal-400"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Rebuild Index</span>
          </button>
        </div>
      </div>

      {/* Document Registry Table */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900 font-display">
            Ingested Medical Literature ({documents.length})
          </h2>
          <span className="text-xs text-teal-800 font-medium">Automatic deduplication & chunking</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
            <div className="w-4 h-4 border-2 border-teal-600 border-t-transparent rounded-full animate-spin" />
            <span>Loading registry...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase tracking-wider text-[10px]">
                  <th className="py-3 px-4">Title & Publisher</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Chunks</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-900">{doc.title}</div>
                      <div className="text-[11px] text-teal-700">{doc.source_name}</div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-600">{doc.category_slug}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 bg-slate-100 text-slate-800 font-bold rounded-md">
                        {doc.chunk_count} chunks
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <select
                        value={doc.status}
                        onChange={(e) => handleStatusChange(doc.id, e.target.value)}
                        className={`text-[11px] font-bold px-2 py-1 rounded-lg border focus:outline-none ${
                          doc.status === 'active'
                            ? 'bg-teal-50 text-teal-800 border-teal-200'
                            : doc.status === 'superseded'
                            ? 'bg-amber-50 text-amber-800 border-amber-200'
                            : 'bg-slate-100 text-slate-600 border-slate-200'
                        }`}
                      >
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="superseded">Superseded</option>
                      </select>
                    </td>
                    <td className="py-3.5 px-4">
                      <button
                        onClick={() => handleInspect(doc.id)}
                        className="flex items-center gap-1 text-teal-700 hover:text-teal-900 font-semibold p-1.5 hover:bg-teal-50 rounded-lg transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                        <span>Inspect Chunks</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Retrieval Debug Console */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 text-slate-900 font-bold text-base font-display">
          <Layers className="w-5 h-5 text-teal-700" />
          <h2>Hybrid Retrieval Diagnostics Console</h2>
        </div>
        <p className="text-xs text-slate-600">
          Simulate hybrid queries to test BM25 lexical matches, dense embeddings, Reciprocal Rank Fusion, and evidence selection.
        </p>

        <div className="flex items-center gap-2">
          <input
            type="text"
            value={testQuery}
            onChange={(e) => setTestQuery(e.target.value)}
            placeholder="Enter test health query..."
            className="flex-1 text-xs bg-slate-50 border border-slate-300 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:border-teal-600 transition-colors shadow-2xs"
          />
          <button
            onClick={runTestQuery}
            disabled={testingRetrieval}
            className="px-4 py-2.5 bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold rounded-xl shadow-xs transition-all flex items-center gap-1.5"
          >
            {testingRetrieval ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5" />
            )}
            <span>{testingRetrieval ? 'Testing...' : 'Test Retrieval'}</span>
          </button>
        </div>

        {testResults && (
          <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3 text-xs">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <span className="font-bold text-slate-700">
                Response Mode: <span className="text-teal-800">{testResults.response_mode}</span>
              </span>
              <span className="font-bold text-teal-800">
                Confidence: {testResults.confidence?.score} ({testResults.confidence?.label})
              </span>
            </div>
            <div>
              <strong className="block text-slate-600 mb-1">Synthesized Grounded Answer:</strong>
              <p className="text-slate-800 leading-relaxed bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
                {testResults.answer}
              </p>
            </div>
            <div>
              <strong className="block text-slate-600 mb-1">
                Retrieved Sources ({testResults.sources?.length}):
              </strong>
              <div className="space-y-1.5">
                {testResults.sources?.map((s: any, idx: number) => (
                  <div key={idx} className="bg-white p-2.5 rounded-lg border border-slate-200 text-slate-700 shadow-2xs">
                    <span className="font-bold text-teal-800">
                      [{s.citation_key}] {s.title}
                    </span>{' '}
                    <span className="text-slate-500">({s.source_name})</span>
                    <p className="text-[11px] text-slate-600 mt-0.5 italic">"{s.excerpt}"</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Chunk Inspector Modal */}
      {inspectModalOpen && selectedDoc && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-2xl border border-slate-200 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div>
                <h3 className="font-bold text-slate-900 text-base font-display">{selectedDoc.title}</h3>
                <p className="text-xs text-teal-700">
                  {selectedDoc.source_name} &bull; {selectedDoc.chunks?.length} Chunks
                </p>
              </div>
              <button
                onClick={() => setInspectModalOpen(false)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto py-4 space-y-3">
              {selectedDoc.chunks?.map((chunk: any) => (
                <div
                  key={chunk.id}
                  className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1.5"
                >
                  <div className="flex items-center justify-between font-bold text-teal-800">
                    <span>
                      Chunk #{chunk.chunk_sequence}: {chunk.section || 'General'}
                    </span>
                    <span className="text-[11px] text-slate-500">{chunk.token_count} tokens</span>
                  </div>
                  <p className="text-slate-700 whitespace-pre-line leading-relaxed">{chunk.raw_text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <h3 className="font-bold text-slate-900 text-base font-display">Upload & Ingest Document</h3>
              <button
                onClick={() => setUploadModalOpen(false)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpload} className="mt-4 space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Select File (.md, .txt, .html, .pdf)
                </label>
                <input
                  type="file"
                  required
                  accept=".md,.markdown,.txt,.html,.htm,.pdf"
                  onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
                  className="w-full text-xs text-slate-700 file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Publisher Source</label>
                <select
                  value={uploadSourceId}
                  onChange={(e) => setUploadSourceId(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl p-2.5 text-slate-800"
                >
                  {sources.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} (Tier {s.authority_tier})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Category</label>
                <select
                  value={uploadCategoryId}
                  onChange={(e) => setUploadCategoryId(Number(e.target.value))}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl p-2.5 text-slate-800"
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.display_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Document Title (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. WHO Guidelines on Salt Intake"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl p-2.5 text-slate-800"
                />
              </div>

              <div className="flex justify-end gap-2.5 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setUploadModalOpen(false)}
                  className="px-4 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 text-white bg-teal-700 hover:bg-teal-800 font-semibold rounded-xl shadow-xs"
                >
                  {uploading ? 'Ingesting...' : 'Ingest Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
