"""
Errors types.

This defines all the error classes for use in the application
"""


class CustomError(ValueError):
    """
    Custom Error.

    Has response method to give a response
    """

    def __init__(self, message):
        """
        Init function.

        Overrides the method field.
        """
        self.message = message
        super().__init__(message)

    def response(self):
        """
        Response method.

        Gives back a human response for results
        """
        return 'Server Errro', 500


class UsernameError(CustomError):
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

    def response(self):
        """
        Response method.

        Gives back a human response for results
        """
        return 'Username invalid', 400


class PasswordError(CustomError):
    """
    Password error.

    Error for a wrong password
    """

    def __init__(self, message):
        """
        Init function.

        Overrides the method field.
        """
        self.message = message
        super().__init__(message)

    def response(self):
        """
        Response method.

        Gives back a human response for results
        """
        return 'Password invalid', 400


class FileIDError(CustomError):
    """
    File id error.

    The file id is invalid.
    """

    def __init__(self, message):
        """
        Init function.

        Overrides the method field.
        """
        self.message = message
        super().__init__(message)

    def response(self):
        """
        Response method.

        Gives back a human response for results
        """
        return 'Fileid invalid', 400


class JWTError(CustomError):
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

    def response(self):
        """
        Response method.

        Gives back a human response for results
        """
        if self.timeout:
            return 'JWT timed out', 400
        return 'JWT processing error', 500


class DBError(CustomError):
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

    def response():
        """
        Response method.

        Gives back a human response for results
        """
        return 'error with db', 500


class JSONError(CustomError):
    """
    Json error.

    Error with parsing or processing json
    """

    def __init__(self, message, invalid):
        """
        Init function.

        Overrides the method field.
        """
        self.message = message
        self.invalid = invalid
        super().__init__(message)

    def response(self):
        """
        Response method.

        Gives back a human response for results
        """
        if self.invalid:
            return 'json is invalid', 400
        return 'error parsing json', 500


class ArgError(CustomError):
    """
    Arg Error.

    Issue with arguments
    """

    def __init__(self, args):
        """
        Init function.

        Overrides the method field.
        """
        self.args = args
        super().__init__(str(args))

    def response(self):
        """
        Response method.

        Gives back a human response for results
        """
        res = ""
        for k, v in self.args:
            res += f'{k} is present: {v is None}, '
        return res
