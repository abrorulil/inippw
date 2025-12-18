import streamlit as st
from io import BytesIO
import PyPDF2
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import networkx as nx
from collections import Counter
from pyvis.network import Network
import tempfile
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# --- Setup & Config ---
st.set_page_config(page_title="Word Graph & PageRank Explorer", layout="wide")

@st.cache_data
def ensure_nltk():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords")

def read_pdf_bytes(file_bytes):
    reader = PyPDF2.PdfReader(file_bytes)
    pages = []
    for p in reader.pages:
        t = p.extract_text()
        if t:
            pages.append(t)
    return "\n".join(pages)

def clean_text(text: str):
    # Hapus bagian referensi/daftar pustaka umum
    cut = re.search(r"(DAFTAR PUSTAKA|REFERENSI|References|Bibliographie)", text, re.IGNORECASE)
    if cut:
        text = text[: cut.start()]
    # Hapus karakter non-alfabet dan spasi berlebih
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize_words(text: str, language="english", custom_stopwords=""):
    """Tokenize text into words safely with fallbacks.

    Uses NLTK's word_tokenize when available; if NLTK data (punkt) is missing
    it falls back to a simple regex-based tokenizer. Stopword loading is
    also guarded and will attempt to download missing data once.
    """
    text_lower = text.lower()

    # Try NLTK tokenizer, but fall back to a regex-based tokenizer if NLTK data is missing
    try:
        toks = word_tokenize(text_lower)
    except LookupError:
        # punkt not available; fallback and warn user
        st.warning("NLTK tokenizer data not found — falling back to a simple tokenizer. Install 'punkt' for better results.")
        toks = re.findall(r"[a-zA-Z]+", text_lower)
    except Exception:
        toks = re.findall(r"[a-zA-Z]+", text_lower)

    # Hanya ambil huruf
    words = [re.sub(r"[^a-zA-Z]", "", w) for w in toks]
    words = [w for w in words if len(w) > 1]  # Hapus kata 1 huruf

    # Setup stopwords (guard against missing corpus)
    sw = set()
    if language in ["english", "indonesian"]:
        try:
            sw = set(stopwords.words(language))
        except LookupError:
            # Attempt to download stopwords once then reload
            try:
                nltk.download("stopwords")
                sw = set(stopwords.words(language))
            except Exception:
                st.warning("NLTK stopwords not available — proceeding without stopword filtering.")
                sw = set()

    # Tambahkan custom stopwords dari input user
    if custom_stopwords:
        extras = [w.strip().lower() for w in custom_stopwords.split(",") if w.strip()]
        sw.update(extras)

    words = [w for w in words if w not in sw]
    return words

def build_cooccurrence_graph(words, window_size=2):
    G = nx.Graph()
    for w in words:
        if not G.has_node(w):
            G.add_node(w)

    for i in range(len(words)):
        for j in range(i + 1, min(i + 1 + window_size, len(words))):
            u, v = words[i], words[j]
            if u == v:
                continue
            if G.has_edge(u, v):
                G[u][v]["weight"] += 1
            else:
                G.add_edge(u, v, weight=1)
    return G

def top_n_pagerank(G, n=20):
    try:
        pr = nx.pagerank(G, weight="weight")
        pr_sorted = sorted(pr.items(), key=lambda x: x[1], reverse=True)
        return pr_sorted[:n]
    except Exception as e:
        st.error(f"Error calculating PageRank: {e}")
        return []

def get_color_map(num_communities):
    # Membuat palet warna yang berbeda untuk setiap komunitas
    color_map = cm.get_cmap('viridis', num_communities)
    hex_colors = []
    for i in range(num_communities):
        rgba = color_map(i)
        hex_colors.append(mcolors.to_hex(rgba))
    return hex_colors

def pyvis_advanced_graph(G, pr_scores, height="600px", width="100%"):
    # Deteksi Komunitas (Clustering) untuk pewarnaan
    try:
        communities = nx.community.greedy_modularity_communities(G)
        # Mapping kata ke ID komunitas
        community_map = {}
        for i, comm in enumerate(communities):
            for node in comm:
                community_map[node] = i
        colors = get_color_map(len(communities))
    except:
        community_map = {}
        colors = ['#97c2fc']

    net = Network(height=height, width=width, notebook=False, bgcolor="#222222", font_color="white")
    
    # Set Physics agar graf lebih menyebar
    net.force_atlas_2based()
    
    # --- Tambahkan Nodes ---
    max_score = max((s for _, s in pr_scores), default=0.0001)
    nodeset = set(n for n, _ in pr_scores)
    
    for node, score in pr_scores:
        # Ukuran berdasarkan PageRank
        size = 15 + (score / max_score) * 45
        
        # Warna berdasarkan komunitas
        comm_id = community_map.get(node, 0)
        color = colors[comm_id % len(colors)] if colors else "#97c2fc"
        
        # Tooltip info saat di-hover
        degree = G.degree[node]
        title_html = (f"<b>{node}</b><br>"
                      f"PageRank: {score:.4f}<br>"
                      f"Degree: {degree}<br>"
                      f"Group: {comm_id}")
        
        net.add_node(node, label=node, size=size, title=title_html, color=color, 
                     borderWidth=2, borderColor="#ffffff")

    # --- Tambahkan Edges ---
    for u, v, data in G.edges(data=True):
        if u in nodeset and v in nodeset:
            w = data.get("weight", 1)
            # Ketebalan garis berdasarkan frekuensi muncul bersama
            width_edge = 1 + (w * 0.5)
            # Warna garis agak transparan
            net.add_edge(u, v, value=w, width=width_edge, color="rgba(200, 200, 200, 0.3)")

    # Tambahkan tombol kontrol fisika di UI
    net.show_buttons(filter_=['physics'])
    return net

def main():
    st.title("🕸️ Smart Document Graph Explorer")
    st.markdown("""
    Aplikasi ini mengubah dokumen teks menjadi jaringan kata (*Word Graph*) dan menggunakan algoritma **PageRank** untuk menemukan kata kunci terpenting serta mendeteksi **Komunitas Topik** dalam teks.
    """)
    
    ensure_nltk()

    # --- Sidebar Controls ---
    with st.sidebar:
        st.header("⚙️ Pengaturan")
        uploaded = st.file_uploader("Upload File PDF", type=["pdf"])
        
        st.divider()
        language = st.selectbox("Bahasa Stopwords", ["english", "indonesian"], index=0)
        
        st.subheader("Filter Kata")
        custom_sw = st.text_area("Custom Stopwords (pisahkan koma)", 
                                 placeholder="contoh: hal, yaitu, tsb, dll")
        
        st.divider()
        st.subheader("Parameter Graf")
        window_size = st.slider("Jendela Kata (Co-occurrence)", 1, 5, 2, 
                                help="Jarak maksimal antar kata untuk dianggap berhubungan.")
        top_n = st.slider("Jumlah Kata Kunci (Top N)", 10, 100, 30)

    # --- Processing ---
    full_text = ""
    
    # 1. Input Handling
    if uploaded is not None:
        file_bytes = BytesIO(uploaded.read())
        try:
            with st.spinner("Membaca PDF..."):
                full_text = read_pdf_bytes(file_bytes)
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return
    else:
        text_input = st.text_area("Atau tempel teks di sini (Opsional)", height=150)
        if text_input.strip():
            full_text = text_input

    if not full_text:
        st.info("👈 Silakan upload PDF atau masukkan teks di sidebar/area teks untuk memulai.")
        return

    # 2. Preprocessing
    with st.spinner("Memproses teks dan membangun graf..."):
        cleaned = clean_text(full_text)
        words = tokenize_words(cleaned, language=language, custom_stopwords=custom_sw)
        
        if len(words) < 5:
            st.warning("⚠️ Kata tidak cukup untuk dianalisis. Coba dokumen yang lebih panjang.")
            return

        # 3. Build Graph
        G = build_cooccurrence_graph(words, window_size=window_size)
        pr_top = top_n_pagerank(G, top_n)
        
    # --- Layout Outputs ---
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(f"📊 Visualisasi Jaringan ({top_n} Kata Teratas)")
        st.caption("Warna menunjukkan kelompok topik. Ukuran menunjukkan tingkat kepentingan.")
        
        # PyVis Graph
        net = pyvis_advanced_graph(G, pr_top, height="550px")
        
        # Save & Load HTML
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
            net.save_graph(tmp.name)
            with open(tmp.name, "r", encoding="utf-8") as f:
                html = f.read()
            st.components.v1.html(html, height=560, scrolling=True)
        except Exception as e:
            st.error(f"Gagal menampilkan graf: {e}")

    with col2:
        st.subheader("📈 Analisis Data")
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Kata", len(words))
        m2.metric("Total Node", G.number_of_nodes())
        m3.metric("Total Hubungan", G.number_of_edges())
        
        # Dataframe
        pr_df = pd.DataFrame(pr_top, columns=["Kata", "Skor PageRank"])
        pr_df["Skor PageRank"] = pr_df["Skor PageRank"].map('{:.5f}'.format)
        
        st.dataframe(pr_df, use_container_width=True, height=400)
        
        # Download Button
        csv = pr_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Hasil (CSV)",
            data=csv,
            file_name='pagerank_results.csv',
            mime='text/csv',
        )

    # --- Preview Text ---
    with st.expander("📄 Lihat Teks Hasil Preprocessing"):
        st.write(cleaned[:2000] + ("..." if len(cleaned) > 2000 else ""))

if __name__ == "__main__":
    main()