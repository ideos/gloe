"""Sphinx configuration for the concise Gloe 0.8 guide."""

from __future__ import annotations

import importlib.metadata
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "Gloe"
copyright = "2024, Samir Braga"
author = "Samir Braga"

try:
    version = importlib.metadata.version("gloe")
except importlib.metadata.PackageNotFoundError:
    from gloe import __version__ as version

release = version

extensions = ["myst_parser"]
myst_enable_extensions = ["colon_fence", "deflist", "fieldlist", "substitution"]
templates_path = ["_templates"]
exclude_patterns = ["Thumbs.db", ".DS_Store"]

html_title = "Gloe - Typed Python pipelines"
html_theme = "furo"
html_last_updated_fmt = ""
html_static_path = ["_static"]
html_favicon = "_static/assets/favicon.ico"
html_theme_options = {
    "light_logo": "assets/gloe-logo-small.webp",
    "dark_logo": "assets/gloe-logo-small.webp",
}
html_extra_path = ["_static/robots.txt"]

ogp_site_url = "https://gloe.ideos.com.br/"
html_baseurl = "https://gloe.ideos.com.br/"
