import json
import pytest
from flask import Flask
from structured_logging import StructuredLogging

def test_get_logger(capsys):
    """Assure logger works and outputs JSON."""

    sl = StructuredLogging()
    logger = sl.get_logger()

    msg = 'a logged message'

    logger.info(msg)

    captured = capsys.readouterr()
    assert msg in captured.out
    assert 'info' in captured.out

    json_out = json.loads(captured.out)
    assert isinstance(json_out, dict)
    assert json_out['severity'] == 'info'
    assert json_out['message'] == msg


def test_flask_logger(capsys):
    """Assure logger works in Flask."""
    app = Flask(__name__)
    app.config['STRUCTURED_LOG_LEVEL'] = 'WARNING'
    slog = StructuredLogging()
    slog.init_app(app)

    msg = 'A warning message in the log.'

    slog.get_logger().warn(msg)

    captured = capsys.readouterr()
    assert msg in captured.out
    assert 'warn' in captured.out

    json_out = json.loads(captured.out)
    assert isinstance(json_out, dict)
    assert json_out['severity'] == 'warning'
    assert json_out['message'] == msg   

    check_logger = app.config.get(StructuredLogging.MODULE_NAME)
    assert isinstance(check_logger, StructuredLogging)


def test_flask_no_init_logger(capsys):
    """Assure logger works in Flask."""
    app = Flask(__name__)
    app.config['STRUCTURED_LOG_LEVEL'] = 'WARNING'
    slog = StructuredLogging()

    msg = 'A warning message in the log.'

    StructuredLogging.get_logger().warn(msg)

    captured = capsys.readouterr()
    assert msg in captured.out
    assert 'warn' in captured.out

    json_out = json.loads(captured.out)
    assert isinstance(json_out, dict)
    assert json_out['severity'] == 'warning'
    assert json_out['message'] == msg   

    check_logger = app.config.get(StructuredLogging.MODULE_NAME)
    assert not check_logger
