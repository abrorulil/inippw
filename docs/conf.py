# docs/conf.py

project = 'Proyek Analisis Data (inippw)'
author = 'Abror Ulil'
copyright = '2024, Abror Ulil'

# Ekstensi yang dibutuhkan agar fitur notebook dan desain muncul
extensions = [
    'nbsphinx',           # Untuk merender file .ipynb
    'myst_parser',        # Untuk merender file .md
    'sphinx_design',      # Untuk fitur kartu/tabs seperti di referensi
    'sphinx.ext.mathjax', # Untuk rumus matematika
]

# Menggunakan tema yang sama dengan Jupyter Book
html_theme = 'sphinx_book_theme'
html_title = "Website Analisis Data - inippw"

# Konfigurasi fitur "kayak github sebelumnya" (Tombol & Navigasi)
html_theme_options = {
    "repository_url": "https://github.com/abrorulil/inippw",
    "use_repository_button": True,     # Tombol ke repo GitHub
    "use_issues_button": True,         # Tombol lapor masalah
    "use_edit_page_button": True,      # Tombol edit halaman
    "path_to_book": "docs",            # Folder konten
    "home_page_in_toc": True,          # Masukkan halaman utama ke sidebar
    "show_navbar_depth": 1,            # Kedalaman navigasi di sidebar
    "show_toc_level": 2,               # Menampilkan isi bab di kanan
}

# Aset Statis (Logo dan Foto)
html_static_path = ['_static']
html_logo = "_static/pp.png"           # Pastikan file pp.png ada di docs/_static/

# File yang diabaikan saat build
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']