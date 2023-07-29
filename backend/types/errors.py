"""
Errors types.

This defines all the error classes for use in the application
"""


class UsernameError(ValueError):
    """
    Username error.

    Error for a wrong username or username that is already taken.
    """

    def __init__(self, message):
        """
        Init function.

        Overrides the method field.
        """
        self.message = message
        super().__init__(message)


class JWTError(ValueError):
    """
    JWT error.

    JWT is not valid
    """

    def __init__(self, message, timeout):
        """
        Init function.

        Overrides the method field.
        """
        self.message = message
        self.timeout = timeout
        super().__init__(message)


class DBError(ValueError):
    """
    DB error.

    Error with dynamo.
    """

    def __init__(self, message):
        """
        Init function.

        Overrides the method field.
        """
        self.message = message
        super().__init__(message)
