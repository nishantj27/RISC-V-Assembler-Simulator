"""Domain-specific errors with source locations."""


class ToolchainError(Exception):
    """Base class for errors that should be shown to a command-line user."""


class AssemblyError(ToolchainError):
    def __init__(self, line: int, message: str) -> None:
        self.line = line
        self.message = message
        super().__init__(f"line {line}: {message}")


class SimulationError(ToolchainError):
    def __init__(self, message: str, *, line: int | None = None) -> None:
        self.line = line
        self.message = message
        prefix = f"line {line}: " if line is not None else ""
        super().__init__(prefix + message)
