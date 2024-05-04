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
    """Resolve :class: references to our type aliases as :data: (autotypevar)."""
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


def setup(app: Sphinx):
    app.connect("missing-reference", resolve_type_aliases)
