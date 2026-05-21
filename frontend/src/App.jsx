import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Settings, 
  GraduationCap,
  MessageSquare,
  Bell,
  Compass,
  Library,
  Activity,
  Globe,
  ShieldCheck,
  Calendar,
  LayoutDashboard,
  RefreshCw,
  Plus,
  Trash2,
  Edit,
  Database,
  X,
  Search,
  BookOpen,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  MapPin,
  Sparkles,
  Info
} from 'lucide-react';

const MODEL_NAME = "Campus-AI-Core";


// Schema map representing exact database validation structures (Only Mahasiswa matches your FastAPI API)
const schemaMap = {
  mahasiswa: [
    { name: 'nim', type: 'text', label: 'NIM (Nomor Induk)', required: true, placeholder: 'Contoh: 2212400012' },
    { name: 'nama', type: 'text', label: 'Nama Lengkap', required: true, placeholder: 'Contoh: Ahmad Subardjo' },
    { name: 'jurusan', type: 'text', label: 'Jurusan / Program Studi', required: true, placeholder: 'Contoh: Teknik Informatika' },
    { name: 'semester', type: 'number', label: 'Semester Aktif', required: true, placeholder: 'Contoh: 4' }
  ]
};

const App = () => {
  const [activeTab, setActiveTab] = useState('admin'); // Default tab set to Admin to showcase the connection
  const [isApiMode, setIsApiMode] = useState(true); // Connected to your real FastAPI backend by default
  const [apiBaseUrl, setApiBaseUrl] = useState("http://localhost:8002/api/v1"); // Dynamic API URL to prevent 404
  const [showApiSettings, setShowApiSettings] = useState(false);
  const scrollRef = useRef(null);

  // Custom alert/confirm structures
  const [toasts, setToasts] = useState([]);
  const [confirmDialog, setConfirmDialog] = useState({ isOpen: false, title: '', message: '', onConfirm: null });

  // Sandbox data backup in case backend is offline
  const [sandboxDb, setSandboxDb] = useState({
    mahasiswa: [
      { id: 1, nim: '22120001', nama: 'Farhan Rizky', jurusan: 'Informatika', semester: 4 },
      { id: 2, nim: '22120002', nama: 'Siti Aminah', jurusan: 'Sistem Informasi', semester: 6 },
      { id: 3, nim: '22120003', nama: 'Budi Santoso', jurusan: 'Teknik Elektro', semester: 2 }
    ],
    dosen: [
      { id: 1, nidn: '0412098201', nama: 'Dr. Ir. Hermawan, M.T.', keahlian: 'Data Science & AI' },
      { id: 2, nidn: '0415117902', nama: 'Riana Safitri, M.Kom.', keahlian: 'Rekayasa Perangkat Lunak' }
    ],
    mata_kuliah: [
      { id: 1, kode: 'IF-302', nama: 'Kecerdasan Buatan', sks: 3 },
      { id: 2, kode: 'IF-101', nama: 'Algoritma & Pemrograman', sks: 4 }
    ]
  });

  const [announcements, setAnnouncements] = useState([
    { time: '08:00', msg: 'Pendaftaran Semester Genap resmi disinkronkan ke FastAPI database.', type: 'success' },
    { time: '09:30', msg: 'Semua request POST, PUT, dan DELETE akan langsung merubah relasi database.', type: 'info' }
  ]);

  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Halo! Saya adalah Smart Campus AI Assistant. Saya siap memandu Anda mengelola data mahasiswa, dosen, serta registrasi KRS.' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Student services subtabs
  const [activePortalTab, setActivePortalTab] = useState('krs');
  const [krsCart, setKrsCart] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [searchBook, setSearchBook] = useState('');
  const [borrowedBooks, setBorrowedBooks] = useState([]);

  // Admin section states
  const [adminSubTab, setAdminSubTab] = useState('mahasiswa');
  const [adminData, setAdminData] = useState({ mahasiswa: [], dosen: [], mata_kuliah: [] });
  const [adminLoading, setAdminLoading] = useState(false);

  // Modals
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({});
  const [editingItem, setEditingItem] = useState(null); // Holds the record during PUT
  const [isSubmitting, setIsSubmitting] = useState(false);

  const addToast = (message, type = 'info') => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  const addAnnouncement = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' });
    setAnnouncements(prev => [{ time, msg, type }, ...prev]);
  };

  useEffect(() => {
    if (activeTab === 'admin') {
      fetchAdminData(adminSubTab);
    }
  }, [activeTab, adminSubTab, isApiMode, sandboxDb, apiBaseUrl]);


  const fetchAdminData = async (endpoint) => {
    setAdminLoading(true);
    if (!isApiMode) {
      setTimeout(() => {
        setAdminData(prev => ({ ...prev, [endpoint]: sandboxDb[endpoint] || [] }));
        setAdminLoading(false);
      }, 250);
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/${endpoint}`);
      if (response.status === 404) {
        throw new Error(`404: Endpoint /${endpoint} tidak ditemukan. Jika Anda belum mengimplementasikannya di FastAPI, gunakan tab 'Mahasiswa' atau alihkan ke mode 'Sandbox'.`);
      }
      if (!response.ok) throw new Error(`HTTP Error Status: ${response.status}`);
      const result = await response.json();
      
      // Handle wrapped or direct lists from FastAPI
      const listData = Array.isArray(result) ? result : (result && Array.isArray(result.data) ? result.data : []);
      
      setAdminData(prev => ({
        ...prev,
        [endpoint]: listData
      }));
    } catch (error) {
      console.warn("FastAPI offline or failed to fetch. Falling back to sandbox.", error);
      
      let errorMsg = error.message;
      if (errorMsg.includes("404")) {
        addToast(`Gagal: ${errorMsg}`, 'error');
      } else {
        addToast(`Gagal menyambungkan ke ${apiBaseUrl}/${endpoint}. Menampilkan data simulasi Sandbox.`, 'warning');
      }

      setAdminData(prev => ({
        ...prev,
        [endpoint]: sandboxDb[endpoint] || []
      }));
    } finally {
      setAdminLoading(false);
    }
  };

  const handleOpenModal = (item = null) => {
    if (item) {
      // mode PUT (Update)
      setEditingItem(item);
      setFormData({ ...item });
    } else {
      // mode POST (Create)
      setEditingItem(null);
      setFormData({});
    }
    setIsModalOpen(true);
  };

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' && value !== '' ? Number(value) : value
    }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const isEditMode = !!editingItem;
    const targetEndpoint = adminSubTab; 
    
    // Check if we are handling 'mahasiswa' to match your exact backend scheme
    const isMahasiswa = targetEndpoint === 'mahasiswa';

    // Strictly sanitize payload keys according to MahasiswaRequest schemas to avoid 422 errors
    const payload = isMahasiswa 
      ? {
          nim: String(formData.nim || ''),
          nama: String(formData.nama || ''),
          jurusan: String(formData.jurusan || ''),
          semester: Number(formData.semester || 1)
        }
      : { ...formData };

    if (!isApiMode) {
      // Simulator mode logic
      setTimeout(() => {
        setSandboxDb(prev => {
          const currentList = prev[targetEndpoint] || [];
          let updatedList;

          if (isEditMode) {
            updatedList = currentList.map(item => 
              item.id === editingItem.id ? { ...item, ...payload } : item
            );
            addToast(`[Simulasi PUT] Sukses mengubah data di Sandbox.`, 'success');
          } else {
            const newRecord = {
              id: Date.now(),
              ...payload
            };
            updatedList = [...currentList, newRecord];
            addToast(`[Simulasi POST] Berhasil merekam entri baru.`, 'success');
          }
          return { ...prev, [targetEndpoint]: updatedList };
        });
        setIsModalOpen(false);
        setIsSubmitting(false);
      }, 400);
      return;
    }

    try {
      const url = isEditMode 
        ? `${apiBaseUrl}/${targetEndpoint}/${editingItem.id}` 
        : `${apiBaseUrl}/${targetEndpoint}`;
      
      const method = isEditMode ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.status === 404) {
        throw new Error(`404: Endpoint '${method} /${targetEndpoint}' tidak ditemukan. Silakan periksa konfigurasi router FastAPI Anda.`);
      }

      if (!response.ok) {
        const errDetails = await response.json();
        throw new Error(errDetails.detail || `Server Error ${response.status}`);
      }

      addToast(`Berhasil ${isEditMode ? 'memperbarui (PUT)' : 'menyimpan (POST)'} data ke FastAPI!`, 'success');
      addAnnouncement(`Operasi database ${method} sukses pada endpoint ${targetEndpoint}.`, 'success');
      setIsModalOpen(false);
      fetchAdminData(targetEndpoint);
    } catch (error) {
      console.error("FastAPI call failed:", error);
      addToast(`Panggilan API Gagal: ${error.message}`, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = (item) => {
    const targetEndpoint = adminSubTab;
    const itemId = item.id;
    const itemName = item.nama || item.nim || 'data';

    setConfirmDialog({
      isOpen: true,
      title: 'Konfirmasi Penghapusan',
      message: `Apakah Anda yakin ingin menghapus "${itemName}"? Tindakan ini akan mengirimkan permintaan DELETE ke FastAPI.`,
      onConfirm: async () => {
        setConfirmDialog(prev => ({ ...prev, isOpen: false }));
        
        if (!isApiMode) {
          setSandboxDb(prev => {
            const updated = (prev[targetEndpoint] || []).filter(row => row.id !== itemId);
            return { ...prev, [targetEndpoint]: updated };
          });
          addToast(`[Simulasi DELETE] Data berhasil disingkirkan dari Sandbox.`, 'info');
          return;
        }

        try {
          const response = await fetch(`${apiBaseUrl}/${targetEndpoint}/${itemId}`, {
            method: 'DELETE',
          });

          if (response.status === 404) {
            throw new Error(`404: Endpoint 'DELETE /${targetEndpoint}/${itemId}' tidak ditemukan.`);
          }

          if (!response.ok) {
            const errDetails = await response.json();
            throw new Error(errDetails.detail || `Server Error ${response.status}`);
          }

          addToast(`Data berhasil terhapus (DELETE) dari FastAPI!`, 'success');
          addAnnouncement(`Penghapusan sukses pada ${targetEndpoint} ID: ${itemId}.`, 'warning');
          fetchAdminData(targetEndpoint);
        } catch (error) {
          console.error("Delete failed:", error);
          addToast(`Gagal menghapus via API: ${error.message}`, 'error');
        }
      }
    });
  };

  const toggleKrsCourse = (course) => {
    if (krsCart.some(c => c.id === course.id)) {
      setKrsCart(prev => prev.filter(c => c.id !== course.id));
      addToast(`Dihapus dari draf KRS: ${course.nama}`, 'info');
    } else {
      const currentSks = krsCart.reduce((acc, curr) => acc + curr.sks, 0);
      if (currentSks + course.sks > 24) {
        addToast("Batas maksimal SKS per semester adalah 24 SKS!", "error");
        return;
      }
      setKrsCart(prev => [...prev, course]);
      addToast(`Ditambahkan ke draf KRS: ${course.nama}`, 'success');
    }
  };

  const submitKrs = () => {
    if (krsCart.length === 0) {
      addToast("Silakan pilih minimal 1 Mata Kuliah terlebih dahulu!", "warning");
      return;
    }
    const totalSks = krsCart.reduce((acc, curr) => acc + curr.sks, 0);
    addToast(`KRS berhasil diajukan! Mengambil ${krsCart.length} matakuliah (${totalSks} SKS). Menunggu validasi dosen wali.`, 'success');
    setKrsCart([]);
  };

  const booksData = [
    { id: 1, title: 'Kecerdasan Buatan Terapan', author: 'Dr. Hermawan', copies: 3, cat: 'Sains' },
    { id: 2, title: 'Prinsip Rekayasa Perangkat Lunak', author: 'Riana Safitri', copies: 5, cat: 'Komputer' },
    { id: 3, title: 'Pemrograman Python Modern', author: 'Yusuf W.', copies: 1, cat: 'Komputer' }
  ];

  const handleBorrowBook = (book) => {
    if (book.copies === 0) {
      addToast("Buku sedang tidak tersedia di perpustakaan.", "error");
      return;
    }
    if (borrowedBooks.includes(book.id)) {
      addToast("Anda sudah meminjam buku ini!", "warning");
      return;
    }
    setBorrowedBooks(prev => [...prev, book.id]);
    addToast(`Peminjaman "${book.title}" berhasil diajukan!`, "success");
  };

  const callAIAssistant = async (userQuery) => {
    setIsTyping(true);
    addAnnouncement(`Memproses analisis asisten AI untuk query Anda...`, 'info');

    if (!isApiMode) {
      // Simulator mode fallback
      setTimeout(() => {
        const q = userQuery.toLowerCase();
        let reply = `Terima kasih atas pertanyaan Anda tentang "${userQuery}". `;
        
        if (q.includes('mahasiswa') || q.includes('daftar')) {
          const mList = (adminData.mahasiswa.length > 0 ? adminData.mahasiswa : sandboxDb.mahasiswa)
            .map(m => `- ${m.nama} (NIM: ${m.nim}) Jurusan ${m.jurusan}`).join('\n');
          reply += `Berikut adalah daftar mahasiswa terdaftar aktif yang saya temukan di sistem saat ini:\n\n${mList}`;
        } else {
          reply += `Semua registrasi serta manajemen CRUD (POST/PUT/DELETE) mahasiswa sudah terintegrasi real-time dengan server FastAPI di ${apiBaseUrl}.`;
        }

        setMessages(prev => [...prev, { role: 'assistant', text: reply }]);
        setIsTyping(false);
        addToast("Asisten AI membalas (Sandbox).", "success");
      }, 1000);
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userQuery })
      });

      if (response.status === 404) {
        throw new Error(`404: Endpoint 'POST /chat' tidak ditemukan. Pastikan APIRouter chat sudah diregistrasikan di file main.py FastAPI Anda.`);
      }

      if (!response.ok) {
        const errDetails = await response.json();
        throw new Error(errDetails.detail || `Server Error ${response.status}`);
      }

      const result = await response.json();
      const aiReply = result.response || "Maaf, saya tidak menerima respons yang valid dari server.";

      setMessages(prev => [...prev, { role: 'assistant', text: aiReply }]);
      addToast("Asisten AI membalas.", "success");
      addAnnouncement(`Respons obrolan berhasil diterima dari FastAPI.`, 'success');
    } catch (error) {
      console.error("AI Chat call failed:", error);
      addToast(`Gagal menghubungi AI: ${error.message}`, 'error');
      
      // Auto fallback to sandbox response with error context
      const fallbackReply = `⚠️ **Gagal Terhubung ke FastAPI**\n\nDetail Error: \`${error.message}\`\n\nPastikan server FastAPI Anda berjalan di \`${apiBaseUrl}\` dan endpoint \`POST /chat\` telah dideklarasikan dengan benar seperti kode Pydantic BaseModel Anda.`;
      setMessages(prev => [...prev, { role: 'assistant', text: fallbackReply }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = () => {
    if (!input.trim() || isTyping) return;
    const query = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setInput('');
    callAIAssistant(query);
  };

  const adminTabs = [
    { id: 'mahasiswa', label: 'Mahasiswa (Full CRUD)' }
  ];

  return (
    <div className="flex h-screen bg-[#020617] text-slate-100 font-sans overflow-hidden relative selection:bg-blue-500/30 selection:text-blue-200">
      
      {/* Dynamic Toast Notifications Layer */}
      <div className="absolute top-4 right-4 z-50 flex flex-col gap-2 max-w-sm pointer-events-none">
        {toasts.map(toast => (
          <div 
            key={toast.id} 
            className={`p-3.5 rounded-xl shadow-xl border backdrop-blur-md flex items-start gap-3 animate-in slide-in-from-right-4 duration-300 pointer-events-auto ${
              toast.type === 'error' ? 'bg-red-950/90 border-red-800 text-red-200' :
              toast.type === 'success' ? 'bg-emerald-950/90 border-emerald-800 text-emerald-200' :
              toast.type === 'warning' ? 'bg-amber-950/90 border-amber-800 text-amber-200' :
              'bg-slate-900/95 border-slate-700 text-slate-200'
            }`}
          >
            {toast.type === 'error' && <AlertTriangle className="shrink-0 text-red-400" size={18} />}
            {toast.type === 'success' && <CheckCircle2 className="shrink-0 text-emerald-400" size={18} />}
            {toast.type === 'warning' && <AlertTriangle className="shrink-0 text-amber-400" size={18} />}
            {toast.type === 'info' && <Info className="shrink-0 text-blue-400" size={18} />}
            <span className="text-xs font-medium leading-relaxed">{toast.message}</span>
          </div>
        ))}
      </div>

      {/* Navigation Sidebar */}
      <div className="w-16 md:w-64 bg-slate-950 border-r border-slate-900 flex flex-col items-center py-6 gap-8 shadow-2xl z-20 shrink-0">
        <div className="flex items-center gap-3 px-4 w-full justify-center md:justify-start">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg shadow-blue-500/20">
            <GraduationCap size={24} className="text-white" />
          </div>
          <span className="hidden md:block font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">Smart Campus</span>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 w-full px-3 space-y-2">
          {[
            { id: 'admin', icon: <LayoutDashboard size={20} />, label: 'Admin Dashboard' },
            { id: 'chat', icon: <MessageSquare size={20} />, label: 'Campus Assistant' },
            { id: 'announcements', icon: <Bell size={20} />, label: 'Announcements' },
            { id: 'services', icon: <Compass size={20} />, label: 'Student Services' },
            { id: 'library', icon: <Library size={20} />, label: 'Library Resource' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-center md:justify-start gap-3 p-3 rounded-xl transition-all duration-300 ${
                activeTab === item.id 
                  ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.15)]' 
                  : 'hover:bg-slate-900/80 hover:text-slate-200 text-slate-400 border border-transparent'
              }`}
            >
              {item.icon}
              <span className="hidden md:block font-medium text-sm">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Database Mode & API Configurator */}
        <div className="px-3 w-full space-y-3">
          <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800 hidden md:block">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Database Mode</span>
              <span className={`w-1.5 h-1.5 rounded-full animate-ping ${isApiMode ? 'bg-indigo-400' : 'bg-emerald-400'}`}></span>
            </div>
            
            <div 
              onClick={() => {
                setIsApiMode(!isApiMode);
                addToast(`Sumber database dialihkan ke: ${!isApiMode ? 'Live API' : 'Sandbox Terisolasi'}`, 'info');
              }}
              className="relative w-full h-8 bg-slate-950 rounded-lg p-1 flex items-center cursor-pointer border border-slate-800 shadow-inner"
            >
              <div 
                className={`absolute top-1 bottom-1 rounded-md bg-gradient-to-r from-blue-600 to-indigo-600 transition-all duration-300 shadow-md ${
                  isApiMode ? 'left-[50%] right-1' : 'left-1 right-[50%]'
                }`}
              />
              <span className="z-10 text-[9px] w-1/2 text-center font-bold text-white leading-none">Sandbox</span>
              <span className="z-10 text-[9px] w-1/2 text-center font-bold text-white leading-none">FastAPI</span>
            </div>
            
            {/* Interactive API Settings Widget */}
            {isApiMode && (
              <div className="mt-3 pt-3 border-t border-slate-850">
                <button 
                  onClick={() => setShowApiSettings(!showApiSettings)}
                  className="w-full text-left text-[10px] text-blue-400 hover:text-blue-300 font-semibold flex justify-between items-center"
                >
                  <span>⚙️ Konfigurasi URL API</span>
                  <span>{showApiSettings ? 'Tutup' : 'Ubah'}</span>
                </button>
                
                {showApiSettings && (
                  <div className="mt-2 space-y-2 animate-in fade-in duration-200">
                    <input 
                      type="text" 
                      value={apiBaseUrl} 
                      onChange={(e) => setApiBaseUrl(e.target.value)}
                      placeholder="Contoh: http://localhost:8001/api/v1"
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-[10px] text-slate-300 focus:outline-none focus:border-blue-500 font-mono"
                    />
                    <p className="text-[9px] text-slate-500 leading-tight">
                      Sesuaikan jika router Anda menggunakan prefix seperti <code className="text-slate-400">/api/v1</code>.
                    </p>
                  </div>
                )}
              </div>
            )}
            
            <p className="text-[9px] text-slate-500 mt-2 text-center leading-normal">
              {isApiMode ? `Target: ${apiBaseUrl}` : "Mode Offline Sandbox"}
            </p>
          </div>
        </div>
      </div>

      {/* Main Workspace Frame */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-slate-950">
        
        {/* Header Bar */}
        <header className="h-16 border-b border-slate-900 flex items-center justify-between px-6 bg-slate-950 z-10 sticky top-0">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
              {activeTab === 'chat' && 'Interactive AI Assistant'}
              {activeTab === 'announcements' && 'Campus Information Hub'}
              {activeTab === 'services' && 'Portal Layanan Terpadu'}
              {activeTab === 'library' && 'Digital Library'}
              {activeTab === 'admin' && 'Central Master Administrator'}
            </h2>
            <div className="flex items-center gap-1.5 bg-slate-900/60 px-2.5 py-1 rounded-full border border-slate-800/80">
              <div className={`w-2 h-2 rounded-full ${isApiMode ? 'bg-indigo-400' : 'bg-emerald-400'}`}></div>
              <span className="text-[9px] font-bold text-slate-300 tracking-widest">
                {isApiMode ? 'LIVE API-MODE' : 'SANDBOX-SIMULASI'}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <div className="text-[11px] text-right hidden sm:block">
              <p className="text-slate-300 font-medium">Administrator Akademik</p>
              <p className="text-slate-500 text-[10px]">Pusat Integrasi Database</p>
            </div>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-500 to-indigo-600 border border-slate-800 shadow-md flex items-center justify-center font-bold text-white text-sm">
              DB
            </div>
          </div>
        </header>

        {/* Content Workspace Panel */}
        <div className="flex-1 overflow-hidden relative">
          
          {activeTab === 'admin' && (
            <div className="h-full flex flex-col p-6 font-sans">
              
              {/* Table selection */}
              <div className="flex items-center gap-2 mb-6 border-b border-slate-900 pb-4 overflow-x-auto custom-scrollbar">
                {adminTabs.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setAdminSubTab(tab.id)}
                    className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                      adminSubTab === tab.id 
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' 
                        : 'bg-slate-900/60 text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-slate-850'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Central Admin Master Data Table */}
              <div className="flex-1 bg-slate-900/60 backdrop-blur-xl border border-slate-900 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
                <div className="flex justify-between items-center px-6 py-4 border-b border-slate-900/80 bg-slate-950">
                  <div>
                    <h3 className="font-bold text-xs text-slate-300 uppercase tracking-widest inline-block mr-2">
                      Kelola Database {adminSubTab.replace('_', ' ')}
                    </h3>
                    {isApiMode && (
                      <span className="text-[10px] text-slate-500 font-mono">
                        ({apiBaseUrl}/{adminSubTab})
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <button 
                      onClick={() => fetchAdminData(adminSubTab)}
                      disabled={adminLoading}
                      className="p-2 bg-slate-900 hover:bg-slate-850 rounded-lg text-slate-300 transition-colors border border-slate-850"
                      title="Refresh Data"
                    >
                      <RefreshCw size={14} className={adminLoading ? 'animate-spin' : ''} />
                    </button>
                    <button 
                      onClick={() => handleOpenModal()}
                      className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-semibold transition-colors shadow-lg shadow-emerald-600/10"
                    >
                      <Plus size={14} />
                      <span>Tambah Baru</span>
                    </button>
                  </div>
                </div>

                {/* Table Data list */}
                <div className="flex-1 overflow-auto custom-scrollbar">
                  {adminLoading ? (
                    <div className="flex items-center justify-center h-full">
                      <div className="flex flex-col items-center gap-4 text-slate-400">
                        <RefreshCw size={28} className="animate-spin text-blue-500" />
                        <p className="text-xs">Sinkronisasi repositori database...</p>
                      </div>
                    </div>
                  ) : adminData[adminSubTab] && adminData[adminSubTab].length > 0 ? (
                    <table className="w-full text-left text-xs text-slate-300">
                      <thead className="text-[10px] text-slate-400 uppercase bg-slate-950 sticky top-0 z-10">
                        <tr>
                          {Object.keys(adminData[adminSubTab][0]).map(key => (
                            <th key={key} className="px-6 py-3.5 font-bold border-b border-slate-900">
                              {key.replace('_', ' ')}
                            </th>
                          ))}
                          <th className="px-6 py-3.5 font-bold border-b border-slate-900 text-right">Aksi</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-900">
                        {adminData[adminSubTab].map((item, idx) => (
                          <tr key={item.id || idx} className="hover:bg-slate-900/30 transition-colors">
                            {Object.entries(item).map(([key, val]) => (
                              <td key={key} className="px-6 py-3.5 whitespace-nowrap overflow-hidden text-ellipsis max-w-xs text-slate-300 font-medium">
                                {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                              </td>
                            ))}
                            <td className="px-6 py-3.5 text-right whitespace-nowrap">
                              <div className="flex justify-end gap-1.5">
                                <button 
                                  onClick={() => handleOpenModal(item)}
                                  className="p-1.5 text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors border border-transparent hover:border-blue-500/20" 
                                  title="Ubah Data (PUT)"
                                >
                                  <Edit size={14} />
                                </button>
                                <button 
                                  onClick={() => handleDelete(item)}
                                  className="p-1.5 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors border border-transparent hover:border-red-500/20" 
                                  title="Hapus Data (DELETE)"
                                >
                                  <Trash2 size={14} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500 p-8 text-center">
                      <Database size={40} className="mb-3 text-slate-600 opacity-40 animate-pulse" />
                      <p className="text-sm font-semibold mb-1">Data Tidak Tersedia (404 / Kosong)</p>
                      <p className="text-xs text-slate-600 max-w-sm mb-4">
                        Endpoint <code className="text-red-400 font-mono">{apiBaseUrl}/{adminSubTab}</code> tidak mengembalikan data.
                      </p>
                      <div className="text-xs bg-slate-950 p-4 rounded-xl text-left border border-slate-850 max-w-md leading-relaxed text-slate-400">
                        <p className="font-bold text-slate-300 mb-1">💡 Tips Solusi:</p>
                        <ul className="list-disc list-inside space-y-1">
                          <li>Jika endpoint ini belum dibuat di FastAPI Anda, silakan beralih ke mode <strong>Sandbox</strong> di navigasi kiri.</li>
                          <li>Jika FastAPI Anda menggunakan prefix router, ubah URL API Anda (misal: tambah <code className="text-blue-400">/api/v1</code>) melalui widget konfigurasi di navigasi kiri.</li>
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="h-full flex flex-col max-w-4xl mx-auto w-full px-6 pt-6 pb-4">
              <div className="flex-1 overflow-y-auto pr-2 space-y-6 custom-scrollbar" ref={scrollRef}>
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in duration-200`}>
                    {msg.role === 'assistant' && (
                      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/10">
                        <Bot size={20} className="text-white" />
                      </div>
                    )}
                    <div className={`max-w-[80%] p-4 rounded-2xl shadow-md ${
                      msg.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-tr-sm shadow-blue-950/20' 
                      : 'bg-slate-900 text-slate-200 border border-slate-850 rounded-tl-sm'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                    </div>
                    {msg.role === 'user' && (
                      <div className="w-9 h-9 rounded-xl bg-slate-800 flex items-center justify-center shrink-0 border border-slate-700">
                        <User size={20} className="text-slate-300" />
                      </div>
                    )}
                  </div>
                ))}
                {isTyping && (
                  <div className="flex gap-4 justify-start animate-pulse">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shrink-0">
                      <Bot size={20} className="text-white" />
                    </div>
                    <div className="bg-slate-900 p-4 rounded-2xl rounded-tl-sm border border-slate-850 flex gap-1.5 items-center">
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></span>
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:0.15s]"></span>
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:0.3s]"></span>
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-4 mt-auto">
                <div className="relative">
                  <div className="flex items-center bg-slate-900 border border-slate-850 rounded-2xl p-2 pl-4 shadow-xl focus-within:border-blue-500 transition-colors">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                      placeholder="Tanyakan detail mahasiswa, pendaftaran, mata kuliah..."
                      className="flex-1 bg-transparent border-none outline-none text-slate-200 placeholder-slate-500 text-sm"
                    />
                    <button 
                      onClick={handleSend}
                      disabled={isTyping || !input.trim()}
                      className="p-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl transition-all shadow-lg shadow-blue-500/10 ml-2"
                    >
                      <Send size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'announcements' && (
            <div className="h-full p-6 md:p-8 max-w-5xl mx-auto w-full overflow-y-auto custom-scrollbar">
              <div className="bg-slate-900/30 border border-slate-900 rounded-2xl p-6 shadow-xl">
                <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-amber-500/10 rounded-xl border border-amber-500/20">
                      <Bell size={20} className="text-amber-400" />
                    </div>
                    <div>
                      <h3 className="text-slate-100 font-bold text-lg">Buletin Kampus</h3>
                      <p className="text-xs text-slate-500">Kanal penyiaran informasi terpadu</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  {announcements.map((ann, i) => (
                    <div key={i} className="flex gap-4 bg-slate-900/40 p-4 rounded-xl border border-slate-900 hover:border-slate-800 transition-all">
                      <div className="shrink-0 flex flex-col items-center justify-center w-16">
                        <span className="text-xs font-semibold text-slate-400">{ann.time}</span>
                      </div>
                      <div className="w-px bg-slate-800"></div>
                      <div className="flex-1">
                        <span className="text-[9px] px-2 py-0.5 rounded-full font-extrabold uppercase bg-blue-950 text-blue-400 border border-blue-900/30">
                          {ann.type}
                        </span>
                        <p className="text-slate-300 text-sm mt-2 leading-relaxed">{ann.msg}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'services' && (
            <div className="h-full flex flex-col p-6 max-w-6xl mx-auto w-full">
              <div className="flex border-b border-slate-900 mb-6 gap-6">
                <button onClick={() => setActivePortalTab('krs')} className={`flex items-center gap-2 pb-3 text-sm font-semibold relative transition-colors ${activePortalTab === 'krs' ? 'text-blue-400' : 'text-slate-400'}`}>
                  <Calendar size={16} /> KRS Online
                  {activePortalTab === 'krs' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />}
                </button>
                <button onClick={() => setActivePortalTab('map')} className={`flex items-center gap-2 pb-3 text-sm font-semibold relative transition-colors ${activePortalTab === 'map' ? 'text-blue-400' : 'text-slate-400'}`}>
                  <Compass size={16} /> Kampus Peta
                  {activePortalTab === 'map' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />}
                </button>
              </div>

              <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                {activePortalTab === 'krs' && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-2 space-y-4">
                      <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Matakuliah Semester Ini</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {sandboxDb.mata_kuliah.map(course => {
                          const isSelected = krsCart.some(c => c.id === course.id);
                          return (
                            <div key={course.id} className={`p-4 rounded-xl border transition-all flex flex-col justify-between ${isSelected ? 'bg-blue-950/20 border-blue-500/50 shadow-md' : 'bg-slate-900 border-slate-850'}`}>
                              <div>
                                <h5 className="font-bold text-slate-200 text-sm">{course.nama}</h5>
                                <p className="text-xs text-slate-500 mt-1">{course.kode} &bull; {course.sks} SKS</p>
                              </div>
                              <button onClick={() => toggleKrsCourse(course)} className="w-full mt-4 py-2 text-xs font-semibold rounded-lg bg-slate-850 hover:bg-blue-600 text-slate-200 hover:text-white transition-colors">
                                {isSelected ? 'Batalkan' : 'Pilih Matakuliah'}
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="bg-slate-900 border border-slate-850 rounded-2xl p-5 h-fit flex flex-col gap-4">
                      <h4 className="font-bold text-sm text-slate-300 flex items-center gap-2">
                        <BookOpen size={16} className="text-blue-400" />
                        Draf KRS
                      </h4>
                      {krsCart.length === 0 ? (
                        <p className="text-xs text-slate-500 text-center py-6">Belum ada matakuliah dipilih.</p>
                      ) : (
                        <div className="space-y-2">
                          {krsCart.map(c => (
                            <div key={c.id} className="flex justify-between items-center text-xs p-2 bg-slate-950 rounded-lg">
                              <span className="truncate pr-2">{c.nama}</span>
                              <span className="font-bold text-blue-400">{c.sks} SKS</span>
                            </div>
                          ))}
                          <button onClick={submitKrs} className="w-full mt-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl text-xs font-bold">
                            Ajukan KRS Sekarang
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {activePortalTab === 'map' && (
                  <div className="bg-slate-900 border border-slate-850 rounded-2xl p-6">
                    <h4 className="font-bold text-sm text-slate-200 mb-4 flex items-center gap-2">
                      <MapPin size={16} className="text-emerald-400" />
                      Denah Lokasi Kampus
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                      <div className="space-y-2">
                        {[
                          { id: 'b-reks', name: 'Gedung Rektorat (A)', desc: 'Layanan administrasi, keuangan & kemahasiswaan' },
                          { id: 'b-labs', name: 'Gedung Lab Sentral (B)', desc: 'Laboratorium riset komputer, fisika, & elektro' }
                        ].map(loc => (
                          <div key={loc.id} onClick={() => setSelectedLocation(loc)} className="p-3 rounded-xl bg-slate-950 border border-slate-850 cursor-pointer">
                            <h5 className="font-bold text-xs text-slate-300">{loc.name}</h5>
                            <p className="text-[10px] text-slate-500 mt-0.5">{loc.desc}</p>
                          </div>
                        ))}
                      </div>
                      <div className="md:col-span-3 bg-slate-950 rounded-xl border border-slate-850 p-4 min-h-[250px] flex flex-col justify-between">
                        <div className="flex-1 flex items-center justify-center border border-dashed border-slate-800 rounded-lg">
                          <p className="text-xs text-slate-600 font-mono">Peta Kampus Interaktif</p>
                        </div>
                        {selectedLocation && (
                          <div className="mt-4 p-3 bg-slate-900 rounded-lg border border-emerald-500/20">
                            <h5 className="font-bold text-xs text-emerald-400">{selectedLocation.name}</h5>
                            <p className="text-xs text-slate-300 mt-1">{selectedLocation.desc}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'library' && (
            <div className="h-full p-6 max-w-5xl mx-auto w-full flex flex-col">
              <div className="flex gap-3 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3.5 top-3 text-slate-500" size={18} />
                  <input 
                    type="text" 
                    placeholder="Cari judul buku atau pengarang..." 
                    value={searchBook}
                    onChange={(e) => setSearchBook(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-850 rounded-xl py-2.5 pl-11 pr-4 text-xs text-slate-300 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {booksData
                  .filter(book => book.title.toLowerCase().includes(searchBook.toLowerCase()))
                  .map(book => {
                    const isBorrowed = borrowedBooks.includes(book.id);
                    return (
                      <div key={book.id} className="p-4 bg-slate-900 rounded-xl border border-slate-850 flex items-start gap-4">
                        <BookOpen size={24} className="text-blue-400 shrink-0 mt-1" />
                        <div className="flex-1 min-w-0">
                          <h5 className="font-bold text-slate-200 text-sm truncate">{book.title}</h5>
                          <p className="text-xs text-slate-400 mt-1">{book.author}</p>
                          <button onClick={() => handleBorrowBook(book)} disabled={isBorrowed} className="mt-3 px-3 py-1.5 rounded-lg text-[10px] font-bold bg-blue-600 text-white">
                            {isBorrowed ? 'Sudah Diajukan' : 'Ajukan Pinjam'}
                          </button>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

        </div>
      </main>

      {/* --- FORM MODAL FOR CREATE (POST) & UPDATE (PUT) --- */}
      {isModalOpen && (
        <div className="absolute inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-850 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col">
            <div className="flex justify-between items-center px-6 py-4 border-b border-slate-850 bg-slate-950">
              <div className="flex items-center gap-2">
                <Sparkles size={16} className="text-blue-400" />
                <h3 className="font-bold text-sm text-slate-200 capitalize">
                  {editingItem ? 'Perbarui Data (PUT)' : 'Tambah Baru (POST)'} {adminSubTab.replace('_', ' ')}
                </h3>
              </div>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white transition-colors p-1">
                <X size={18} />
              </button>
            </div>
            
            <form onSubmit={handleFormSubmit} className="p-6 space-y-4 max-h-[60vh] overflow-y-auto custom-scrollbar">
              {schemaMap[adminSubTab] && schemaMap[adminSubTab].map((field) => (
                <div key={field.name} className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    {field.label} {field.required && <span className="text-red-500">*</span>}
                  </label>
                  <input
                    type={field.type}
                    name={field.name}
                    value={formData[field.name] || ''}
                    onChange={handleInputChange}
                    required={field.required}
                    placeholder={field.placeholder}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 placeholder-slate-600 outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
              ))}
            </form>
            
            <div className="px-6 py-4 border-t border-slate-850 bg-slate-950 flex justify-end gap-3">
              <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-900">
                Batal
              </button>
              <button onClick={handleFormSubmit} disabled={isSubmitting} className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 flex items-center gap-2">
                {isSubmitting ? <RefreshCw size={14} className="animate-spin" /> : 'Simpan Data'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- CUSTOM CONFIRMATION DIALOG (Avoids window.confirm) --- */}
      {confirmDialog.isOpen && (
        <div className="absolute inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-850 rounded-2xl w-full max-w-sm shadow-2xl p-5 flex flex-col gap-4">
            <div className="flex items-center gap-3 text-red-400">
              <AlertTriangle size={24} className="shrink-0" />
              <h3 className="font-bold text-sm text-slate-200">{confirmDialog.title}</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">{confirmDialog.message}</p>
            <div className="flex justify-end gap-2.5 mt-2">
              <button onClick={() => setConfirmDialog(prev => ({ ...prev, isOpen: false }))} className="px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-950 transition-colors">
                Batal
              </button>
              <button onClick={confirmDialog.onConfirm} className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-xs font-bold transition-colors">
                Ya, Hapus Data
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 5px; height: 5px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(51, 65, 85, 0.4); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(59, 130, 246, 0.6); }
      `}</style>
    </div>
  );
};

export default App;