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


def tokenize_words(text: str, language="english"):
    toks = word_tokenize(text.lower())
    words = [re.sub(r"[^a-zA-Z]", "", w) for w in toks]
    words = [w for w in words if w]
    sw = set(stopwords.words(language)) if language in ["english"] else set()
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
    st.title("Paper Word Graph & PageRank Explorer")
    ensure_nltk()

    st.sidebar.header("Upload / Input")
    uploaded = st.sidebar.file_uploader("Upload PDF file", type=["pdf"])
    text_input = st.sidebar.text_area("Or paste text (optional)", height=150)

    language = st.sidebar.selectbox("Language for stopwords", ["english"], index=0)
    window_size = st.sidebar.slider("Co-occurrence window", min_value=1, max_value=5, value=2)
    top_n = st.sidebar.slider("Top N words", min_value=5, max_value=100, value=20)

    if uploaded is None and not text_input.strip():
        st.info("Upload a PDF or paste text to begin.")
        return

    full_text = ""
    if uploaded is not None:
        file_bytes = BytesIO(uploaded.read())
        try:
            full_text = read_pdf_bytes(file_bytes)
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

    if text_input.strip():
        full_text += "\n" + text_input

    cleaned = clean_text(full_text)
    st.subheader("Extracted Text (preview)")
    st.write(cleaned[:5000] + ("..." if len(cleaned) > 5000 else ""))

    words = tokenize_words(cleaned, language=language)
    st.write(f"Total words (after cleaning): {len(words)}")

    if len(words) < 5:
        st.warning("Not enough words to build a graph. Try a longer document.")
        return

    G = build_cooccurrence_graph(words, window_size=window_size)

    st.subheader("Graph summary")
    st.write(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

    pr_top = top_n_pagerank(G, top_n)
    pr_df = pd.DataFrame(pr_top, columns=["word", "pagerank"])

    st.subheader("Top PageRank words")
    st.dataframe(pr_df)
    st.bar_chart(pr_df.set_index("word")["pagerank"])

    st.subheader("Interactive Graph (top words)")
    net = pyvis_from_subgraph(G, pr_top)
    # save to temp html and display
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    net.save_graph(tmp.name)
    with open(tmp.name, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=600, scrolling=True)


if __name__ == "__main__":
    main()
