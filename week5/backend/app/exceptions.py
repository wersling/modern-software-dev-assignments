"""Custom exception classes for the application.

This module defines a hierarchy of exception classes that provide
consistent error responses across all API endpoints.
"""


class AppException(Exception):
    """Base exception class for all application errors.

    All custom exceptions should inherit from this class.
    It provides the standard structure for error responses.

    Attributes:
        code: Error code (e.g., "NOT_FOUND", "VALIDATION_ERROR")
        message: Human-readable error message
        status_code: HTTP status code to return

    Example:
        raise AppException(
            code="CUSTOM_ERROR",
            message="Something went wrong",
            status_code=400
        )
    """

    def __init__(self, code: str, message: str, status_code: int = 500):
        """Initialize the exception.

        Args:
            code: Error code identifier
            message: Human-readable error message
            status_code: HTTP status code
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found.

    Example:
        raise NotFoundException("Note", f"id={note_id}")
    """

    def __init__(self, resource: str, identifier: str):
        """Initialize the exception.

        Args:
            resource: Resource type (e.g., "Note", "Tag")
            identifier: Resource identifier (e.g., "id=123", "name='example'")
        """
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} with {identifier} not found",
            status_code=404,
        )


class ValidationException(AppException):
    """Exception raised when request validation fails.

    This is different from Pydantic validation errors (422).
    Use this for business logic validation failures.

    Example:
        raise ValidationException("Tag name already exists")
    """

    def __init__(self, message: str):
        """Initialize the exception.

        Args:
            message: Validation error message
        """
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=400,
        )


class ConflictException(AppException):
    """Exception raised when a resource conflict occurs.

    Example:
        raise ConflictException("Tag", f"name '{name}' already exists")
    """

    def __init__(self, resource: str, message: str):
        """Initialize the exception.

        Args:
            resource: Resource type in conflict
            message: Detailed conflict message
        """
        super().__init__(
            code="CONFLICT",
            message=f"{resource} conflict: {message}",
            status_code=409,
        )


class BadRequestException(AppException):
    """Exception raised when the request is malformed or invalid.

    Example:
        raise BadRequestException("Invalid query parameters")
    """

    def __init__(self, message: str):
        """Initialize the exception.

        Args:
            message: Error message describing what was wrong with the request
        """
        super().__init__(
            code="BAD_REQUEST",
            message=message,
            status_code=400,
        )


class UnauthorizedException(AppException):
    """Exception raised when authentication is required but missing.

    Example:
        raise UnauthorizedException("Valid authentication token required")
    """

    def __init__(self, message: str = "Authentication required"):
        """Initialize the exception.

        Args:
            message: Error message (default: "Authentication required")
        """
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401,
        )


class ForbiddenException(AppException):
    """Exception raised when user lacks permission for an action.

    Example:
        raise ForbiddenException("You do not have permission to modify this resource")
    """

    def __init__(self, message: str = "Access forbidden"):
        """Initialize the exception.

        Args:
            message: Error message (default: "Access forbidden")
        """
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403,
        )


class InternalServerErrorException(AppException):
    """Exception raised when an unexpected server error occurs.

    This should be used for unexpected errors that should be logged
    but not exposed to the client in detail.

    Example:
        try:
            # some operation
        except Exception as e:
            logger.error("Unexpected error", exc_info=e)
            raise InternalServerErrorException("An unexpected error occurred")
    """

    def __init__(self, message: str = "Internal server error"):
        """Initialize the exception.

        Args:
            message: Generic error message (default: "Internal server error")
        """
        super().__init__(
            code="INTERNAL_ERROR",
            message=message,
            status_code=500,
        )
