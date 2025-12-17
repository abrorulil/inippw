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
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import tempfile
import pandas as pd


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
    # file_bytes: BytesIO
    reader = PyPDF2.PdfReader(file_bytes)
    pages = []
    for p in reader.pages:
        t = p.extract_text()
        if t:
            pages.append(t)
    return "\n".join(pages)


def clean_text(text: str):
    # remove references section if present
    cut = re.search(r"(DAFTAR PUSTAKA|REFERENSI|References|Bibliographie)", text, re.IGNORECASE)
    if cut:
        text = text[: cut.start()]
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_words(text: str, language="english", do_stem=False):
    # Prefer NLTK tokenization but fall back to a simple regex tokenizer
    # because some NLTK punkt models (e.g., for Indonesian) may not be available
    try:
        toks = word_tokenize(text.lower())
    except LookupError:
        toks = re.findall(r"[a-zA-Z]+", text.lower())

    # keep only alphabetic tokens
    words = [re.sub(r"[^a-zA-Z]", "", w) for w in toks]
    words = [w for w in words if w]

    if language == "english":
        sw = set(stopwords.words("english"))
    elif language == "indonesia":
        factory = StopWordRemoverFactory()
        sw = set(factory.get_stop_words())
    else:
        sw = set()
    words = [w for w in words if w not in sw]
    if do_stem and language == "indonesia":
        stemmer = StemmerFactory().create_stemmer()
        words = [stemmer.stem(w) for w in words]
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
    pr = nx.pagerank(G, weight="weight")
    pr_sorted = sorted(pr.items(), key=lambda x: x[1], reverse=True)
    return pr_sorted[:n]


def pyvis_from_subgraph(G, pr_scores, height="600px", width="100%"):
    net = Network(height=height, width=width, notebook=False)
    # add nodes with size ~ pagerank
    max_score = max((s for _, s in pr_scores), default=0.0001)
    for node, score in pr_scores:
        size = 10 + (score / max_score) * 40
        net.add_node(node, label=node, size=size, title=f"{node}: {score:.6f}")

    # add edges between these top nodes if present in G
    nodeset = set(n for n, _ in pr_scores)
    for u, v, data in G.edges(data=True):
        if u in nodeset and v in nodeset:
            w = data.get("weight", 1)
            net.add_edge(u, v, value=w)

    net.barnes_hut()
    return net


def main():
    st.title("Eksplorator Word Graph & PageRank dari Paper")
    ensure_nltk()

    st.sidebar.header("Unggah / Input")
    uploaded = st.sidebar.file_uploader("Unggah file PDF", type=["pdf"])
    text_input = st.sidebar.text_area("Atau tempel teks (opsional)", height=150)

    lang_display = st.sidebar.selectbox("Bahasa untuk stopword", ["Bahasa Indonesia", "Bahasa Inggris"], index=0)
    language = "indonesia" if lang_display == "Bahasa Indonesia" else "english"
    do_stem = st.sidebar.checkbox("Lakukan stemming (Bahasa Indonesia)", value=False)
    window_size = st.sidebar.slider("Jarak co-occurrence (window)", min_value=1, max_value=5, value=2)
    top_n = st.sidebar.slider("Jumlah kata teratas", min_value=5, max_value=100, value=20)

    if uploaded is None and not text_input.strip():
        st.info("Unggah PDF atau tempel teks untuk memulai.")
        return

    full_text = ""
    if uploaded is not None:
        file_bytes = BytesIO(uploaded.read())
        try:
            full_text = read_pdf_bytes(file_bytes)
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca PDF: {e}")

    if text_input.strip():
        full_text += "\n" + text_input

    cleaned = clean_text(full_text)
    st.subheader("Teks yang diekstrak (pratinjau)")
    st.write(cleaned[:5000] + ("..." if len(cleaned) > 5000 else ""))

    words = tokenize_words(cleaned, language=language, do_stem=do_stem)
    st.write(f"Jumlah kata (setelah pembersihan): {len(words)}")

    if len(words) < 5:
        st.warning("Tidak cukup kata untuk membangun graf. Coba dokumen yang lebih panjang.")
        return

    G = build_cooccurrence_graph(words, window_size=window_size)

    st.subheader("Ringkasan graf")
    st.write(f"Simpul: {G.number_of_nodes()}, Sisi: {G.number_of_edges()}")

    pr_top = top_n_pagerank(G, top_n)
    pr_df = pd.DataFrame(pr_top, columns=["kata", "pagerank"])

    st.subheader("Kata teratas menurut PageRank")
    st.dataframe(pr_df)
    st.bar_chart(pr_df.set_index("kata")["pagerank"])

    st.subheader("Graf interaktif (kata teratas)")
    net = pyvis_from_subgraph(G, pr_top)
    # save to temp html and display
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    net.save_graph(tmp.name)
    with open(tmp.name, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=600, scrolling=True)


if __name__ == "__main__":
    main()
