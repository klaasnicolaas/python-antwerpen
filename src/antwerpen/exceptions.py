"""Asynchronous Python client providing Open Data information of Antwerpen."""


class ODPAntwerpenError(Exception):
    """Generic Open Data Platform Antwerpen exception."""


class ODPAntwerpenConnectionError(ODPAntwerpenError):
    """Open Data Platform Antwerpen - connection error."""
