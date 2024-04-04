"""Configuration file for the Sphinx documentation builder.

Documentation:
    https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import importlib.metadata
import sys
from pathlib import Path

sys.path.append(str(Path("./_ext").absolute()))

# -- Project information -----------------------------------------------------

project = "mayafbx"
author = "Thibaud Gambier"
copyright = f"2024, {author}"  # noqa: A001
release = importlib.metadata.version("mayafbx")
version = ".".join(release.split(".", 2)[0:2])

# -- General configuration ---------------------------------------------------

# fmt: off
extensions = [
    "myst_parser",               # markdown
    "sphinx.ext.autodoc",        # docstring
    "enum_tools.autoenum",       # docstring, enums
    "sphinx.ext.napoleon",       # dosctring, google style
    "sphinx.ext.intersphinx",    # cross-projects references
    "autodoc_fbxpropertyfield",  # docstring, FbxPropertyField
]
# fmt: on

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
maximum_signature_line_length = 80
default_role = "any"

# -- Extensions configuration ------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autodoc_class_signature = "separated"
autodoc_mock_imports = ["maya"]
autodoc_default_options = {
    "exclude-members": "__new__",
}

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_title = "mayafbx"

