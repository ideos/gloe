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
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinx_copybutton",
]
templates_path = ["_templates"]
exclude_patterns = ["Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = " "
# html_logo = "assets/gloe-logo-small.png"
html_theme = "furo"
html_last_updated_fmt = ""
# html_use_index = False  # Don't create index
# html_domain_indices = False  # Don't need module indices
# html_copy_source = False  # Don't need sources
html_sidebars: dict[str, list[str]] = {
    # "about": ["sidebar_main_nav_links.html"],
}
# autodoc_default_options = {"ignore-module-all": True}

html_static_path = ["_static"]
html_css_files = ["theme_customs.css"]
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
