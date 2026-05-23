"""Autodoc extension for documenting `FbxPropertyField` descriptor."""

from enum import Enum
from typing import Any

from sphinx.application import Sphinx
from sphinx.ext.autodoc import AttributeDocumenter
from sphinx.ext.autodoc.mock import _MockObject
from typing_extensions import override


class FbxPropertyFieldDocumenter(AttributeDocumenter):
    """A specialized Documenter subclass for `FbxPropertyField` descriptors."""

    objtype = "fbxpropertyfield"
    directivetype = AttributeDocumenter.objtype
    priority = 10 + AttributeDocumenter.priority
    option_spec = dict(AttributeDocumenter.option_spec)  # noqa: RUF012

    @override
    @classmethod
    def can_document_member(
        cls,
        member: Any,
        membername: str,
        isattr: bool,
        parent: Any,
    ) -> bool:
        """Filter only `FbxPropertyField` descriptors."""
        from mayafbx.bases import FbxPropertyField

        return isinstance(member, FbxPropertyField)

    def add_directive_header(self, sig: str) -> None:
        """Add the directive header and options to the generated content."""
        super().add_directive_header(sig)

        from mayafbx.bases import FbxPropertyField

        source_name = self.get_sourcename()
        assert isinstance(self.object, FbxPropertyField)
        fbx_prop = self.object.fbx_property

        typename = fbx_prop._type.__name__  # noqa: SLF001
        self.add_line(f"   :type: {typename}", source_name)

        try:
            default = fbx_prop.default
        except Exception:  # noqa: BLE001
            return

        if isinstance(default, _MockObject):
            return

        if isinstance(default, Enum):
            default = f"{default.__class__.__name__}.{default.name}"
        else:
            default = repr(default)

        self.add_line(f"   :value: {default}", source_name)


def setup(app: Sphinx) -> None:
    """Setup our extension."""
    app.setup_extension("sphinx.ext.autodoc")
    app.add_autodocumenter(FbxPropertyFieldDocumenter)
