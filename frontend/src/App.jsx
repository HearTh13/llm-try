import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, X, MessageSquare, ChevronRight, GraduationCap, Building2, BookOpen, Newspaper, Globe } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// --- Components ---

const Navbar = () => (
  <nav className="container" style={{ padding: '1.5rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <div style={{ fontWeight: 700, fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <div style={{ width: 40, height: 40, backgroundColor: 'var(--primary)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
        <Globe size={24} />
      </div>
      <span>USD</span>
    </div>
    <div style={{ display: 'flex', gap: '2rem', fontWeight: 500 }}>
      {['Beranda', 'Fakultas', 'Prodi', 'Gedung', 'Berita'].map(item => (
        <a key={item} href={`#${item.toLowerCase()}`} style={{ textDecoration: 'none', color: 'var(--text)', opacity: 0.7 }}>{item}</a>
      ))}
    </div>
    <button className="btn btn-primary">Pendaftaran</button>
  </nav>
);

const Hero = () => (
  <section id="beranda" style={{ padding: '8rem 0 4rem' }}>
    <div className="container">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <span style={{ color: 'var(--primary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em' }}>Selamat Datang di Portal</span>
        <h1>Universitas <br />Sanata Dharma</h1>
        <p style={{ maxWidth: '600px', fontSize: '1.25rem' }}>
          Mencetak generasi yang Cerdas dan Humanis dan AMBATUKAAAAMMMMMM.
        </p>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '3rem' }}>
          <button className="btn btn-primary" style={{ padding: '1rem 2.5rem' }}>Lihat Program Studi</button>
          <button className="btn" style={{ padding: '1rem 2.5rem', backgroundColor: 'white', color: 'var(--text)', border: '1px solid #e2e8f0' }}>Pelajari Sejarah</button>
        </div>
      </motion.div>
    </div>
  </section>
);

const DataSection = ({ title, id, type, data }) => (
  <section id={id} style={{ padding: '4rem 0' }}>
    <div className="container">
      <h2 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {type === 'faculty' && <GraduationCap size={32} color="var(--primary)" />}
        {type === 'program' && <BookOpen size={32} color="var(--primary)" />}
        {type === 'building' && <Building2 size={32} color="var(--primary)" />}
        {title}
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '2rem' }}>
        {data.map((item, idx) => (
          <motion.div 
            key={idx}
            className="glass"
            whileHover={{ y: -10, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)' }}
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            style={{ padding: '2rem' }}
          >
            <h3 style={{ marginBottom: '1rem' }}>{item.name || item.title}</h3>
            <p style={{ fontSize: '0.95rem', marginBottom: '1.5rem' }}>{item.description || item.content || 'Informasi selengkapnya mengenai unit ini.'}</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary)', textTransform: 'uppercase' }}>
                {item.degree ? `${item.degree} - ${item.accreditation}` : item.category || 'USD'}
              </span>
              <ChevronRight size={20} color="var(--text-muted)" />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Halo! Saya CxR Mas Owok. Ada yang bisa saya bantu tentang Universitas Sanata Dharma?' }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    
    setIsTyping(true);
    try {
      const res = await axios.post(`${API_BASE}/chat/ask`, { prompt: userMsg });
      setMessages(prev => [...prev, { role: 'ai', text: res.data.jawaban_ai }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'ai', text: 'Waduh, koneksiku lagi terganggu nih. Coba tanya lagi ya!' }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <>
      <motion.div 
        className="chatbot-trigger"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <img src="/jokowiBot.jpg" alt="Mas Owok" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </motion.div>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            className="chatbot-popup glass"
            initial={{ opacity: 0, y: 50, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.8 }}
          >
            <div style={{ backgroundColor: 'var(--primary)', color: 'white', padding: '1.5rem', borderTopLeftRadius: 'var(--radius)', borderTopRightRadius: 'var(--radius)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: 40, height: 40, borderRadius: '50%', backgroundColor: 'white', overflow: 'hidden' }}>
                  <img src="/mas-owok.png" alt="Mas Owok" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                </div>
                <div>
                  <div style={{ fontWeight: 600 }}>CxR Mas Owok</div>
                  <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Virtual Assistant USD</div>
                </div>
              </div>
              <X style={{ cursor: 'pointer' }} onClick={() => setIsOpen(false)} />
            </div>

            <div style={{ flex: 1, padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {messages.map((m, i) => (
                <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '80%' }}>
                  <div style={{ 
                    padding: '1rem', 
                    borderRadius: '1.25rem', 
                    backgroundColor: m.role === 'user' ? 'var(--primary)' : 'white',
                    color: m.role === 'user' ? 'white' : 'var(--text)',
                    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
                    border: m.role === 'user' ? 'none' : '1px solid #e2e8f0',
                    borderBottomRightRadius: m.role === 'user' ? '0.25rem' : '1.25rem',
                    borderBottomLeftRadius: m.role === 'user' ? '1.25rem' : '0.25rem'
                  }}>
                    {m.text}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div style={{ padding: '1rem', backgroundColor: 'white', borderRadius: '1.25rem', alignSelf: 'flex-start', display: 'flex', gap: '4px' }}>
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1 }} style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: 'var(--text-muted)' }} />
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: 'var(--text-muted)' }} />
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: 'var(--text-muted)' }} />
                </div>
              )}
              <div ref={endRef} />
            </div>

            <div style={{ padding: '1.25rem', borderTop: '1px solid #e2e8f0', display: 'flex', gap: '0.75rem' }}>
              <input 
                type="text" 
                placeholder="Tanya Mas Owok..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                style={{ flex: 1, padding: '0.75rem 1.25rem', borderRadius: '999px', border: '1px solid #e2e8f0', outline: 'none', backgroundColor: '#f1f5f9' }}
              />
              <button onClick={handleSend} style={{ width: 45, height: 45, borderRadius: '50%', backgroundColor: 'var(--primary)', color: 'white', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Send size={18} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

// --- App ---

function App() {
  const [data, setData] = useState({ faculties: [], programs: [], buildings: [], news: [] });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [fac, prg, bld, nws] = await Promise.all([
          axios.get(`${API_BASE}/faculties`),
          axios.get(`${API_BASE}/study-programs`),
          axios.get(`${API_BASE}/buildings`),
          axios.get(`${API_BASE}/news`)
        ]);
        setData({ faculties: fac.data, programs: prg.data, buildings: bld.data, news: nws.data });
      } catch (e) {
        console.error("Data fetch failed", e);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="App">
      <div className="pixel-bg" />
      <Navbar />
      <Hero />
      <DataSection title="Fakultas Pilihan" id="fakultas" type="faculty" data={data.faculties} />
      <DataSection title="Program Studi" id="prodi" type="program" data={data.programs} />
      <DataSection title="Kampus & Gedung" id="gedung" type="building" data={data.buildings} />
      
      <footer style={{ padding: '8rem 0 4rem', textAlign: 'center', opacity: 0.6 }}>
        <p>© 2026 CxR Mas Owok.</p>
      </footer>

      <ChatWidget />
    </div>
  );
}

export default App;
