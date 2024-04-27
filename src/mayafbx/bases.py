from __future__ import annotations

import enum
from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, Generic, Iterator, TypeVar, cast, overload

from mayafbx.enums import StrEnum
from mayafbx.utils import run_mel_command

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = [
    "FbxProperty",
    "FbxOptions",
    "FbxPropertyField",
    "apply_options",
    "applied_options",
]

T = TypeVar("T", bool, str, float, int, StrEnum)


class FbxProperty(Generic[T]):
    """Wrapper of a ``FBXProperty`` mel command."""

    def __init__(
        self,
        command: str,
        type: type[T],  # noqa: A002
        default: T | Callable[[], T],
    ) -> None:
        self._command = command
        self._type = type
        self._default = default

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(command={self._command!r}, type={self._type!r})"
        )

    @property
    def command(self) -> str:
        """FBXProperty mel command."""
        return self._command

    @property
    def default(self) -> T:
        """Default value."""
        return self._default() if callable(self._default) else self._default

    def get(self) -> T:
        """Get fbx property value from scene."""
        value = run_mel_command(f"{self._command} -q")
        return self._type(value)

    def set(self, value: T) -> None:
        """Set property value to scene."""
        if issubclass(self._type, bool):
            value_ = {True: "true", False: "false"}[bool(value)]
        elif issubclass(self._type, str):
            value_ = f'"{value}"'
        else:  # NOTE: notably float and int
            value_ = str(value)

        args = [self._command]
        if self._command not in {"FBXExportUpAxis", "FBXExportAxisConversionMethod"}:
            args += ["-v"]
        args += [value_]

        run_mel_command(" ".join(args))


class FbxPropertyField(Generic[T]):
    """Access a value for a `FbxProperty` on a class like a python `property`."""

    # TODO: example
    def __init__(
        self,
        command: str,
        *,
        type: type[T],  # noqa: A002
        default: T | Callable[[], T],
    ) -> None:
        self.fbx_property = FbxProperty(command, type, default)
        self.name = ""

    def __set_name__(self, owner: type[object], name: str) -> None:
        self.name = name


    @overload
    def __get__(self, obj: None, objtype: None) -> FbxPropertyField[T]: ...

    @overload
    def __get__(self, obj: object, objtype: type[object]) -> T: ...

    def __get__(
        self,
        obj: object | None,
        objtype: type[object] | None = None,
    ) -> FbxPropertyField[T] | T:
        if obj is None:
            return self
        return obj.__dict__.get(self.name) or self.fbx_property.default

    def __set__(self, obj: object, value: T) -> None:
        obj.__dict__[self.name] = value


class FbxOptions:
    """Base class for declaring and manipulating a collection of `FbxProperty`.

    Example::

        import mayafbx

        class MyFbxOptionClass(mayafbx.FbxOptions):

            triangulate = mayafbx.FbxPropertyField(
                "FBXProperty Export|IncludeGrp|Geometry|Triangulate",
                default=False,
                type=bool,
            )

        options = MyFbxOptions()
        options.triangulate = True
    """

    @classmethod
    def from_scene(cls) -> Self:
        """Initialize a new instance from scene values."""
        self = cls()
        for descriptor in self.__class__.__dict__.values():
            if isinstance(descriptor, FbxPropertyField):
                descriptor.__set__(self, descriptor.fbx_property.get())
        return self

    def __iter__(self) -> Iterator[tuple[FbxProperty, object]]:
        for descriptor in self.__class__.__dict__.values():
            if isinstance(descriptor, FbxPropertyField):
                value = descriptor.__get__(self, type(self))
                yield (descriptor.fbx_property, value)


def apply_options(options: FbxOptions) -> None:
    """Apply ``options`` to scene."""
    for prop, value in options:
        prop.set(value)


@contextmanager
def applied_options(options: FbxOptions) -> Iterator[None]:
    """Apply ``options`` to scene during context."""
    backup = options.from_scene()
    apply_options(options)
    yield
    apply_options(backup)
