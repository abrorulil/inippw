# docs/conf.py

project = 'Proyek Analisis Data (inippw)'
author = 'Abror Ulil'
copyright = '2024, Abror Ulil'

extensions = [
    'nbsphinx',
    'myst_parser',
    'sphinx_design',
    'sphinx.ext.mathjax',
]

html_theme = 'sphinx_book_theme'
html_logo = "_static/pp.png" 
html_title = "Website Analisis Data - inippw"

html_theme_options = {
    "repository_url": "https://github.com/abrorulil/inippw",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "path_to_book": "docs",
    "home_page_in_toc": False, # Agar halaman utama tidak muncul dua kali di sidebar
    "show_navbar_depth": 1,
}

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']