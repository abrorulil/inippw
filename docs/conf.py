# docs/conf.py

project = 'Proyek Analisis Data (inippw)'
author = 'Abror Ulil'

extensions = [
    'nbsphinx',
    'myst_parser',
    'sphinx_design',
]

html_theme = 'sphinx_book_theme'
html_logo = "_static/pp.png"
html_title = "Proyek Analisis Data"

html_theme_options = {
    "repository_url": "https://github.com/abrorulil/inippw",
    "use_repository_button": True,
    "path_to_book": "docs",
    "home_page_in_toc": True,  # Ubah ke True agar Home muncul di list
    "show_navbar_depth": 2,    # Ubah ke 2 agar anak bab terlihat
}

# --- BAGIAN PENTING: MEMAKSA SIDEBAR MUNCUL ---
html_sidebars = {
    "**": ["navbar-logo.html", "sbt-sidebar-nav.html", "search-field.html"]
}
# ----------------------------------------------

myst_enable_extensions = ["colon_fence", "html_image"]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']