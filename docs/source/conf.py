# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("pygments"))

project = "Gloe"
copyright = "2023, Samir Braga"
author = "Samir Braga"
release = "0.4.3"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_toolbox.more_autodoc.variables",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    # "sphinx_autodoc_typehints",
    "myst_parser",
    "sphinx_copybutton",
]
overloads_location = "bottom"
napoleon_google_docstring = True
autosectionlabel_prefix_document = True
napoleon_use_rtype = False
intersphinx_mapping = {"httpx": ("https://www.python-httpx.org/", None)}

templates_path = ["_templates"]
exclude_patterns = ["Thumbs.db", ".DS_Store"]
autodoc_typehints = "description"
autodoc_type_aliases = {
    "PreviousTransformer": "gloe.base_transformer.PreviousTransformer"
}
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = "Gloe"
# html_logo = "assets/gloe-logo-small.png"
html_theme = "furo"
html_last_updated_fmt = ""
# html_use_index = False  # Don't create index
# html_domain_indices = False  # Don't need module indices
# html_copy_source = False  # Don't need sources
html_sidebars: dict[str, list[str]] = {
    "Home": ["/"],
}
# autodoc_default_options = {"ignore-module-all": True}

html_static_path = ["_static"]
html_css_files = ["theme_customs.css"]
html_favicon = "_static/assets/favicon.ico"
html_theme_options = {
    # "main_nav_links": {"Docs": "/index", "About": "/about"},
    "light_logo": "assets/gloe-logo-small.png",
    "dark_logo": "assets/gloe-logo-small.png",
    "dark_css_variables": {
        "color-brand-primary": "#00e6bf",
        "color-brand-content": "#00e6bf",
        "font-stack": "Roboto, sans-serif",
        "font-stack--monospace": "Courier, monospace",
        "font-size--normal": "Courier, monospace",
    },
}

# pygments_style = "styles.GloeStyle"
pygments_dark_style = "styles.GloeStyle"
