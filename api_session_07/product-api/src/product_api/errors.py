from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    status_code = 500
    error = "internal_error"

    def __init__(self, detail=""):
        super().__init__(detail)
        self.detail = detail


class NotFound(ApiError):
    status_code = 404
    error = "not_found"


class Conflict(ApiError):
    status_code = 409
    error = "conflict"


class OutOfStock(Conflict):
    error = "out_of_stock"


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _api(e):
        return jsonify(error=e.error, detail=e.detail), e.status_code

    @app.errorhandler(ValidationError)
    def _validation(e):
        return jsonify(error="validation_error", detail=e.messages), 422

    @app.errorhandler(HTTPException)
    def _http(e):
        return jsonify(error=e.name.lower().replace(" ", "_"),
                       detail=e.description), e.code

    @app.errorhandler(Exception)
    def _unhandled(e):
        app.logger.exception("unhandled error")
        return jsonify(error="internal_error", detail="unexpected error"), 500