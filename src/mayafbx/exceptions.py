"""Package exceptions."""


class MayaFbxError(Exception):
    """Base exception for ``mayafbx`` package errors."""


class MelEvalError(MayaFbxError):
    """Failed to run a ``maya.mel`` command."""
