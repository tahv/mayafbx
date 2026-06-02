from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Generic, Iterator, TypeVar, overload

from mayafbx.enums import StrEnum
from mayafbx.utils import get_maya_version, logger, run_mel_command

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    "FbxOptions",
    "FbxProperty",
    "FbxPropertyField",
    "applied_options",
    "apply_options",
    "run_mel_command",
)

_T = TypeVar("_T", bool, str, float, int, StrEnum)


class FbxProperty(Generic[_T]):
    """Wrapper of a `FBXProperty` mel command."""

    def __init__(
        self,
        command: str,
        *,
        type_: type[_T],
        default: _T | Callable[[], _T],
        available: tuple[int | None, int | None] = (None, None),
    ) -> None:
        self._command = command
        self._type: type[_T] = type_
        self._default: _T | Callable[[], _T] = default
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
        if version_removed is not None and current_version >= version_removed:  # noqa: SIM103
            return False
        return True

    @property
    def command(self) -> str:
        """FBXProperty mel command."""
        return self._command

    @property
    def default(self) -> _T:
        """Default value."""
        return self._default() if callable(self._default) else self._default

    def get(self) -> _T | None:
        """Get fbx property value from scene.

        Returns ``None`` if property is not available in current Maya version.
        """
        if not self.is_available():
            return None
        value = run_mel_command(f"{self._command} -q")
        return self._type(value)  # type: ignore[arg-type]  # type: ignore[arg-type]

    def set(self, value: _T) -> None:
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
        if self._command not in {
            "FBXExportUpAxis",
            "FBXExportAxisConversionMethod",
            "FBXImportScaleFactor",
        }:
            args += ["-v"]
        args += [value_]

        run_mel_command(" ".join(args))


class FbxPropertyField(Generic[_T]):
    """Access a value for a `FbxProperty` on a class like a python `property`."""

    # TODO(tga): example
    def __init__(
        self,
        command: str,
        *,
        type: type[_T],  # noqa: A002
        default: _T | Callable[[], _T],
        available: tuple[int | None, int | None] = (None, None),
    ) -> None:
        self.fbx_property: FbxProperty[_T] = FbxProperty(
            command,
            type_=type,
            default=default,
            available=available,
        )
        self.name: str = ""

    def __set_name__(self, owner: type[object], name: str) -> None:
        self.name = name

    @overload
    def __get__(self, obj: None, objtype: None) -> FbxPropertyField[_T]: ...

    @overload
    def __get__(self, obj: object, objtype: type[object]) -> _T: ...

    def __get__(
        self,
        obj: object | None,
        objtype: type[object] | None = None,
    ) -> FbxPropertyField[_T] | _T:
        if obj is None:  # pragma: no cover
            return self
        value = obj.__dict__.get(self.name)
        if value is None:
            value = self.fbx_property.default
        return value

    def __set__(self, obj: object, value: _T) -> None:
        obj.__dict__[self.name] = value


class FbxOptions:
    """Base class for declaring and manipulating a collection of `FbxProperty`.

    Example:
        ```python
        import mayafbx

        class MyFbxOptionClass(mayafbx.FbxOptions):

            triangulate = mayafbx.FbxPropertyField(
                "FBXProperty Export|IncludeGrp|Geometry|Triangulate",
                default=False,
                type=bool,
            )

        options = MyFbxOptions()
        options.triangulate = True
        ```
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

    def __iter__(self) -> Iterator[tuple[FbxProperty[Any], object]]:
        for descriptor in self.__class__.__dict__.values():
            if isinstance(descriptor, FbxPropertyField):
                value = descriptor.__get__(self, type(self))
                yield (descriptor.fbx_property, value)


def apply_options(options: FbxOptions) -> None:
    """Apply `options` to scene."""
    for prop, value in options:
        prop.set(value)


@contextmanager
def applied_options(options: FbxOptions) -> Iterator[None]:
    """Apply `options` to scene during context."""
    backup = options.__class__.from_scene()
    apply_options(options)
    yield
    apply_options(backup)
