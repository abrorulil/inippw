# docs/conf.py

project = 'Proyek Analisis Data (inippw)'
author = 'Abror Ulil'
extensions = [
    'nbsphinx',
    'myst_parser',
    'sphinx.ext.mathjax',
    'sphinx_design',
]

html_theme = 'sphinx_book_theme'
html_title = "Website Analisis Data - inippw"

html_theme_options = {
    # UBAH URL DI SINI
    "repository_url": "https://github.com/abrorulil/inippw", 
    "use_repository_button": True,
    "use_issues_button": True,
    "path_to_book": "docs",
    "show_navbar_depth": 2,
}

html_static_path = ['_static']
html_logo = "_static/pp.png" 
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']