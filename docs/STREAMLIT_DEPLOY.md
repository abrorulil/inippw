# Deploying `app.py` to Streamlit

Steps to run locally:

1. Create a virtual environment and activate it (optional but recommended)

   python -m venv .venv
   .\.venv\Scripts\activate

2. Install dependencies:

   pip install -r requirements.txt

3. Run the app locally:

   streamlit run app.py


To deploy on Streamlit Cloud:

1. Push the code to GitHub (e.g., https://github.com/abrorulil/inippw)
2. Log in to https://share.streamlit.io and click "New app" → select the repo and branch, and set the main file to `inippw/app.py`.
3. Click deploy.

Notes:
- Jika ingin antarmuka Bahasa Indonesia, pilih opsi Bahasa Indonesia pada sidebar aplikasi.
- Jika PDF besar, pertimbangkan memotong atau tempel teks langsung.
- Aplikasi menggunakan `pyvis` untuk menampilkan graf interaktif.
