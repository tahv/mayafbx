from __future__ import annotations

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

    @property
    def default(self) -> T:
        """Default value."""
        return self._default() if callable(self._default) else self._default

    def get(self) -> T:
        """Get fbx property value from scene."""
        value = cast(str, run_mel_command(f"{self._command} -q"))
        value_ = {"true": True, "false": False}.get(value)
        if value_ is None:
            value_ = self._type(value)
        return value_  # type: ignore[assignment]

    def set(self, value: T) -> None:
        """Set property value to scene."""
        formatter: Callable[[T], str] = {
            bool: lambda v: str(v).lower(),
            str: lambda v: f'"{v}"',
            float: lambda v: str(v),
            int: lambda v: str(v),
        }.get(self._type, lambda v: str(v))

        args = [self._command]
        if self._command not in {"FBXExportUpAxis", "FBXExportAxisConversionMethod"}:
            args += ["-v"]
        args += [formatter(value)]

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
    for fbx_property, value in options:
        fbx_property.set(value)


@contextmanager
def applied_options(options: FbxOptions) -> Iterator[None]:
    """Apply ``options`` to scene during context."""
    backup = options.from_scene()
    apply_options(options)
    yield
    apply_options(backup)
