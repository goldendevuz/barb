class DomainException(Exception):
    """Base exception for all domain logic/business rule violations."""
    def __init__(self, message: str, code: str = "domain_error"):
        super().__init__(message)
        self.message = message
        self.code = code


class StateTransitionError(DomainException):
    """Raised when an invalid state transition is attempted on a StateMachine."""
    def __init__(self, message: str):
        super().__init__(message, code="invalid_state_transition")


class AutomationExecutionError(DomainException):
    """Raised when automation execution fails."""
    def __init__(self, message: str):
        super().__init__(message, code="automation_execution_failed")
