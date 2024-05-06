# Copyright © 2024 Province of British Columbia
#
# Licensed under the BSD 3 Clause License, (the "License");
# you may not use this file except in compliance with the License.
# The template for the license can be found here
#    opensource.org/license/bsd-3-clause/
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""This module provides Structured Logging services.

This is targeted for our GCP based services.
"""
from __future__ import annotations
from logging import Logger

from flask import Flask
from flask.logging import default_handler

import structlog


class StructuredLogging:
    """SBC Connect structured logging library"""

    def __init__(self, app: Flask = None) -> StructuredLogging:
        """Create the object."""
        self.app = None
        self.logger = None
        self.log_level = NOTSET

        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> StructuredLogging:
        """Initialize the logger."""
        self.app = app
        structlog.stdlib.recreate_defaults(log_level=self.log_level)
        log_level = app.config.get('STRUCTURED_LOG_LEVEL', 'NOTSET')
        self.log_level = _NAME_TO_LEVEL[log_level.lower()]
        self.logger = getJSONLogger()
    
    def get_logger(self) -> Logger.logger:
        """Get or create the logger and return it."""
        if not self.logger:
           self.logger = getJSONLogger()
        return self.logger 


# Adapted from the stdlib
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_NAME_TO_LEVEL = {
    "critical": CRITICAL,
    "exception": ERROR,
    "error": ERROR,
    "warn": WARNING,
    "warning": WARNING,
    "info": INFO,
    "debug": DEBUG,
    "notset": NOTSET,
}


# adapted from https://github.com/ymotongpoo/cloud-logging-configurations/blob/master/python/structlog/main.py
def field_name_modifier(
    logger: structlog._loggers.PrintLogger, log_method: str, event_dict: dict
) -> dict:
    """A structlog processor for mapping fields to Cloud Logging.
    Learn more at https://www.structlog.org/en/stable/processors.html

    Args:
        logger: A logger object.
        log_method: The name of the wrapped method.
        event_dict:Current context together with the current event.

    Returns:
        A structlog processor.
    """
    # Changes the keys for some of the fields, to match Cloud Logging's expectations
    event_dict["severity"] = event_dict["level"]
    del event_dict["level"]
    event_dict["message"] = event_dict["event"]
    del event_dict["event"]
    return event_dict


def getJSONLogger() -> structlog._config.BoundLoggerLazyProxy:
    """Initialize a logger configured for JSON structured logs.

    Returns:
        A configured logger object.
    """
    # extend using https://www.structlog.org/en/stable/processors.html
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            field_name_modifier,
            structlog.processors.TimeStamper("iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
    )
    return structlog.get_logger()


def logging_flush() -> None:
    # Setting PYTHONUNBUFFERED in Dockerfile ensured no buffering
    pass
