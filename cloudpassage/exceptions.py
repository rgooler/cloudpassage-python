#!/usr/bin/env python
from __future__ import absolute_import


class CloudPassageError(Exception):
    """Exception raised from the API.

    Attributes:
        err_type -- input expression in which the error occurred
        err_desc  -- explanation of the error
    """

    def __init__(self, err_type, err_desc):
        self.expr = err_type
        self.msg = err_desc


class InvalidClientError(Exception):
    """
    Invalid Client - usually bad credentials or the like

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg


class ValidationFailedError(Exception):
    """
    Invalid data passed to the API - usually an "X already exists" thing

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg
