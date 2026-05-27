"""Package utils."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, NamedTuple, cast

from maya import cmds, mel
from maya.api import OpenMaya, OpenMayaAnim

from mayafbx.exceptions import MelEvalError

logger = logging.getLogger("mayafbx")


if TYPE_CHECKING:
    from typing_extensions import Required, TypedDict

    class FbxPropDict(TypedDict, total=False):
        """Content of a `FBXProperties` line."""

        path: Required[str]
        value: Required[str]
        type: Required[str]
        possible: list[str]


__all__ = ("Take",)


class Take(NamedTuple):
    """FBX take description."""

    name: str
    """Take name."""

    start: int
    """Start frame."""

    end: int
    """End frame."""


def get_export_takes() -> list[Take]:
    """Get a list of export takes from `FBXExportSplitAnimationIntoTakes` command."""
    output = run_mel_command("FBXExportSplitAnimationIntoTakes -q")
    if output == 0:
        return []

    takes: list[Take] = []
    for line in cast("list[str]", output):
        name, start, end = line.split()
        _, _, name = name.partition("=")
        _, _, start = start.partition("=")
        _, _, end = end.partition("=")
        takes.append(Take(name=name, start=int(start), end=int(end)))

    return takes


def set_export_takes(takes: list[Take]) -> None:
    """Set export takes using `FBXExportSplitAnimationIntoTakes` command.

    Warning:
        All existing export takes will be cleared beforehand.

    Raises:
        RuntimeError: When `Take.end` < `Take.start`.
    """
    run_mel_command("FBXExportSplitAnimationIntoTakes -c")  # clear takes
    for take in takes:
        if take.end < take.start:
            message = f"`Take.end` ({take.end}) < `Take.start` ({take.start})"
            raise RuntimeError(message)
        cmd = f"FBXExportSplitAnimationIntoTakes -v {take.name} {take.start} {take.end}"
        run_mel_command(cmd)


def get_maya_version() -> int:
    """Returns maya version."""
    return int(cmds.about(version=True))


def run_mel_command(command: str) -> str | list[str] | int:
    """Run a mel command and return the result.

    Raise:
        MelEvalError: Failed to run mel command.
    """
    logger.debug("Running mel command: '%s'", command)
    try:
        return mel.eval(command)  # type: ignore[no-any-return]
    except RuntimeError as exception:
        raise MelEvalError(command) from exception


def get_anim_control_start_time() -> int:
    """Return Animation Control start time."""
    return int(OpenMayaAnim.MAnimControl.animationStartTime().value)


def get_anim_control_end_time() -> int:
    """Return Animation Control end time."""
    return int(OpenMayaAnim.MAnimControl.animationEndTime().value)


def collect_fbx_properties() -> list[FbxPropDict]:
    """Dump the output of 'FBXProperties' command to a list of dict.

    Each item in returned list contain the following data:

    - path: Property path.
    - type: Property type.
    - value: Current value applied to the scene.
    - possible: A `list` of possible values. Only included for enum properties.
    """

    def callback(message: str, _: int, data: list[str]) -> bool:
        data.append(message)
        return True

    lines: list[str] = []
    id_ = OpenMaya.MCommandMessage.addCommandOutputFilterCallback(callback, lines)
    mel.eval("FBXProperties")
    OpenMaya.MCommandMessage.removeCallback(id_)

    regex = re.compile(
        r"PATH:\s(\S+)\s+"
        r"\(\sTYPE:\s(\w+)\s\)\s+"
        r"\(\sVALUE:\s([^\)]+)\s\)"
        r"(?:\s+\(POSSIBLE VALUES: ([^\)]+)\s+\))?",
    )
    result: list[FbxPropDict] = []
    for line in lines:
        match = regex.match(line)
        assert match, f"Failed to match line: {line}"  # noqa: S101

        data = {
            "path": match.group(1),
            "type": match.group(2),
            "value": match.group(3),
        }
        if match.group(4):
            data["possible"] = match.group(4).split()

        result.append(data)  # type: ignore[arg-type]

    return result
