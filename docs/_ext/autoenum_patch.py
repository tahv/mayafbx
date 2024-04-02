from typing import get_type_hints

from enum_tools.autoenum import (
    INSTANCEATTR,
    SUPPRESS,
    ClassLevelDocumenter,
    EnumMemberDocumenter,
    get_type_hints,
    memory_address_re,
    safe_getattr,
    stringify_typehint,
    suppress,
)
from sphinx.application import Sphinx

# TODO: delete patch when resolved: https://github.com/domdfcoding/enum_tools/issues/34

def add_directive_header(self, sig: str) -> None:
    """Patch of `EnumMemberrDocumenter.add_directive_header` to only show value name.

    This is a hack that replicate that implement this MR:
    https://github.com/domdfcoding/enum_tools/pull/63
    """
    ClassLevelDocumenter.add_directive_header(self, sig)
    sourcename = self.get_sourcename()
    if not self.options.annotation:
        # obtain type annotation for this attribute
        try:
            annotations = get_type_hints(self.parent)
        except NameError:
            # Failed to evaluate ForwardRef (maybe TYPE_CHECKING)
            annotations = safe_getattr(self.parent, "__annotations__", {})
        except (TypeError, KeyError, AttributeError):
            # KeyError = a broken class found (refs: https://github.com/sphinx-doc/sphinx/issues/8084)
            # AttributeError is raised on 3.5.2 (fixed by 3.5.3)
            annotations = {}

        if self.objpath[-1] in annotations:
            objrepr = stringify_typehint(annotations.get(self.objpath[-1]))
            self.add_line("   :type: " + objrepr, sourcename)
        else:
            key = ('.'.join(self.objpath[:-1]), self.objpath[-1])
            if self.analyzer and key in self.analyzer.annotations:
                self.add_line("   :type: " + self.analyzer.annotations[key], sourcename)

    elif self.options.annotation is SUPPRESS:
        pass
    else:
        self.add_line("   :annotation: %s" % self.options.annotation, sourcename)

    if not self.options.annotation:
        with suppress(Exception):
            if self.object is not INSTANCEATTR:

                # Workaround for https://github.com/sphinx-doc/sphinx/issues/9272
                # which broke Enum displays in 4.1.0
                objrepr = memory_address_re.sub('', repr(self.object.value)).replace('\n', ' ')
                self.add_line(f'   :value: {objrepr}', self.get_sourcename())


def setup(_: Sphinx) -> None:
    """Setup our extension."""
    EnumMemberDocumenter.add_directive_header = add_directive_header
