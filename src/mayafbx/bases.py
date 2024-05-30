"""Base classes and functions."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, Generic, Iterator, TypeVar, overload

from mayafbx.enums import StrEnum
from mayafbx.utils import get_maya_version, logger, run_mel_command

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
        *,
        type_: type[T],
        default: T | Callable[[], T],
        available: tuple[int | None, int | None] = (None, None),
    ) -> None:
        self._command = command
        self._type: type[T] = type_
        self._default: T | Callable[[], T] = default
        self._available = available

    def __repr__(self) -> str:  # pragma: no cover
        properties = (
            f"command={self._command!r}",
            f"rype={self._type!r}",
        )
        return f"{self.__class__.__name__}({', '.join(properties)})"

    def is_available(self) -> bool:
        """Property is available in current Maya version."""
        current_version = get_maya_version()
        version_added, version_removed = self._available
        if version_added is not None and current_version < version_added:
            return False
        if version_removed is not None and current_version >= version_removed:
            return False
        return True

    @property
    def command(self) -> str:
        """FBXProperty mel command."""
        return self._command

    @property
    def default(self) -> T:
        """Default value."""
        return self._default() if callable(self._default) else self._default

    def get(self) -> T | None:
        """Get fbx property value from scene.

        Returns ``None`` if property is not availble in current Maya version.
        """
        if not self.is_available():
            return None
        value = run_mel_command(f"{self._command} -q")
        return self._type(value)  # type: ignore[arg-type]  # type: ignore[arg-type]

    def set(self, value: T) -> None:
        """Set property value to scene."""
        if not self.is_available():
            logger.debug(
                "Property not available in this version of Maya, skipping set: '%s'",
                self._command,
            )
            return

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
        available: tuple[int | None, int | None] = (None, None),
    ) -> None:
        self.fbx_property: FbxProperty[T] = FbxProperty(
            command,
            type_=type,
            default=default,
            available=available,
        )
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
        if obj is None:  # pragma: no cover
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

    def __init__(self, **kwargs: object) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_scene(cls) -> Self:
        """Initialize a new instance from scene values."""
        self = cls()
        for descriptor in self.__class__.__dict__.values():
            if isinstance(descriptor, FbxPropertyField):
                value = descriptor.fbx_property.get()
                if value is None:
                    continue
                descriptor.__set__(self, value)
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
