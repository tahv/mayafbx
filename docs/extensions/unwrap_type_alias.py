from __future__ import annotations

import operator
from typing import TYPE_CHECKING, Any, TypeGuard

import griffe
from griffe_modernized_annotations.predicates import canonical_path_of
from griffe_modernized_annotations.traversal import walk_expressions, walk_objects_of

if TYPE_CHECKING:
    from griffe_modernized_annotations.types import Expression, Predicate


class UnwrapTypeAlias(griffe.Extension):
    """Griffe extension that unwrap `typing.TypeAlias`."""

    def __init__(self) -> None:
        self._type_aliases: dict[str, str | griffe.Expr | None] = {}

    def on_package(self, *, pkg: griffe.Module, **kwargs: Any) -> None:
        self._inspect_package_type_aliases(pkg)

        for function in walk_objects_of(pkg, type=griffe.Function):
            self._handle_function(function)

        for attribute in walk_objects_of(pkg, type=griffe.Attribute):
            self._handle_attribute(attribute)

    def _inspect_package_type_aliases(self, pkg: griffe.Module) -> None:
        for attribute in walk_objects_of(pkg, type=griffe.Attribute):
            if not isinstance(attribute.annotation, griffe.Expr):
                continue
            if not is_type_alias(attribute.annotation):
                continue
            self._type_aliases[attribute.canonical_path] = attribute.value

    def _handle_function(self, function: griffe.Function) -> None:
        for parameter in function.parameters:
            parameter.annotation = self._unwrap(parameter.annotation)

        function.returns = self._unwrap(function.returns)

    def _handle_attribute(self, attribute: griffe.Attribute) -> None:
        if attribute.annotation is None:
            return
        if is_type_alias(attribute.annotation):
            attribute.value = self._unwrap(attribute.value)
        else:
            attribute.annotation = self._unwrap(attribute.annotation)

    def _unwrap(
        self,
        annotation: Expression | None,
    ) -> Expression | None:
        if annotation is None:
            return None

        predicate = is_expr_name_with(set(self._type_aliases.keys()))
        for node in walk_expressions(annotation, predicate=predicate):
            # TODO(tga): replace node, requires parent
            # left = subscript.left
            # assert isinstance(left, ExprName)
            # left.name = self._collections[canonical_path_of(left)]
            pass

        return annotation


def is_type_alias(instance: str | griffe.Expr | griffe.Object) -> bool:
    return canonical_path_of(instance) in (
        "typing.TypeAlias",
        "typing_extensions.TypeAlias",
    )


def is_expr_name_with(canonical_path: str | set[str]) -> Predicate[griffe.ExprName]:
    comparator = operator.eq if isinstance(canonical_path, str) else operator.contains

    def predicate(expression: Expression) -> TypeGuard[griffe.ExprName]:
        return isinstance(expression, griffe.ExprName) and (
            comparator(canonical_path, canonical_path_of(expression))
        )

    return predicate
