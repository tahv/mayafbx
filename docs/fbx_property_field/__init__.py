from __future__ import annotations

from typing import Any

import griffe
from typing_extensions import override


class FbxPropertyField(griffe.Extension):
    """Griffe extension for documenting `FbxPropertyField` descriptors."""

    @override
    def on_object(
        self,
        *,
        obj: griffe.Object,
        loader: griffe.GriffeLoader,
        **kwargs: Any,
    ) -> None:
        if not obj.is_class:
            return

        for member in obj.members.values():
            if not isinstance(member, griffe.Attribute):
                continue
            if not isinstance(member.value, griffe.ExprCall):
                continue
            if not isinstance(member.value.function, griffe.ExprName):
                continue
            if member.value.function.name != "FbxPropertyField":
                continue

            arguments: dict[str, griffe.ExprKeyword] = {}
            for arg in member.value.arguments:
                if not isinstance(arg, griffe.ExprKeyword):
                    continue  # command
                arguments[arg.name] = arg

            member.value = arguments["default"].value
            member.annotation = arguments["type"].value
