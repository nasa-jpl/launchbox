from bottle import request


def index(**kwargs):
    """Respond to calling /<api_key>/auth"""
    # TODO: Figure out how this should respond. Redirect to auth/login?
    pass


def login(**kwargs):
    """Respond to calling /<api_key>/auth/login"""
    # TODO: Get URL from provider plugin
    return {
        "url": "???"
    }


def verify(data, **kwargs):
    """Respond to calling /<api_key>/auth/verify"""
    params = request.params
    return {
        "valid": True,
        "identity": { "username": "cranfill" }
    }
