project = 'Proyek Analisis Data (inippw)'
author = 'Abror Ulil'
extensions = [
    'nbsphinx',
    'myst_parser',
    'sphinx.ext.mathjax',
]

html_theme = 'sphinx_book_theme'
html_title = "Website PPW - inippw"
html_static_path = ['_static']

# Gunakan logo jika ada file pp.png di docs/_static/
html_logo = "_static/pp.png"

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']