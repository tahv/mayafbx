"""Autodoc extension to resolve 'missing-reference' on 'autotypevar'.

https://github.com/sphinx-doc/sphinx/issues/10785
https://sphinx-toolbox.readthedocs.io/en/latest/extensions/more_autodoc/typevars.html
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docutils.nodes import Element
    from sphinx.addnodes import pending_xref
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


def resolve_type_aliases(
    app: Sphinx,
    env: BuildEnvironment,
    node: pending_xref,
    contnode: Element,
) -> Element | None:
    """Try to resolve :class: references as :data:."""
    if node["refdomain"] == "py" and node["reftype"] == "class":
        return app.env.get_domain("py").resolve_xref(
            env,
            node["refdoc"],
            app.builder,
            "data",
            node["reftarget"],
            node,
            contnode,
        )
    return None


def setup(app: Sphinx) -> None:
    """Setup extension."""
    app.connect("missing-reference", resolve_type_aliases)
