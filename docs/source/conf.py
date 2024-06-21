# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
import pkg_resources

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("pygments"))

project = "Gloe"
copyright = "2024, Samir Braga"
author = "Samir Braga"
version = pkg_resources.get_distribution("gloe").version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_toolbox.more_autodoc.variables",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    # "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinxext.opengraph",
    "sphinxcontrib.katex",
    # "sphinx_autodoc_typehints",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_sitemap",
]
overloads_location = "bottom"
napoleon_google_docstring = True
autosectionlabel_prefix_document = True
napoleon_use_rtype = False
# intersphinx_mapping = {"httpx": ("https://www.python-httpx.org/", None)}
ogp_social_cards = {
    "enable": True,
    "line_color": "#00afac",
    "image": "_static/assets/gloe-logo.png",
}
ogp_site_url = "https://gloe.ideos.com.br/"
# ogp_image = "https://gloe.ideos.com.br/_static/assets/gloe-logo.png"
html_baseurl = "https://gloe.ideos.com.br/"
sitemap_locales = [None]
sitemap_url_scheme = "{link}"
sitemap_excludes = [
    "theory.html",
]
html_extra_path = ["_static/robots.txt"]
ogp_description_length = 160

templates_path = ["_templates"]
exclude_patterns = ["Thumbs.db", ".DS_Store"]
autodoc_typehints = "description"
autodoc_type_aliases = {
    "PreviousTransformer": "gloe.base_transformer.PreviousTransformer"
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = "Gloe - You Code like a Flow"
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
# html_css_files = ["theme_customs.css"]
html_favicon = "_static/assets/favicon.ico"
html_theme_options = {
    # "main_nav_links": {"Docs": "/index", "About": "/about"},
    "light_logo": "assets/gloe-logo-small.webp",
    "dark_logo": "assets/gloe-logo-small.webp",
    "dark_css_variables": {
        "color-brand-primary": "#00e6bf",
        "color-brand-content": "#00e6bf",
        "color-link--visited": "#14c9ee",
        "font-stack": "Roboto, sans-serif",
        "font-stack--monospace": "Courier, monospace",
        "font-size--normal": "Courier, monospace",
    },
    "light_css_variables": {
        "color-brand-primary": "#00afac",
        "color-brand-content": "#00afac",
        "font-stack": "Roboto, sans-serif",
        "font-stack--monospace": "Courier, monospace",
        "font-size--normal": "Courier, monospace",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/ideos/gloe",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

# pygments_style = "styles.GloeStyle"
pygments_dark_style = "styles.GloeDarkStyle"
pygments_light_style = "styles.GloeLightStyle"


def source_read_handler(app, pagename, templatename, context, doctree):
    if context["pageurl"] == f"{html_baseurl}index.html":
        context["pageurl"] = html_baseurl.rstrip("/")


def setup(app):
    app.connect("html-page-context", source_read_handler)
