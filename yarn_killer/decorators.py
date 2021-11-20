import functools
from werkzeug.exceptions import abort
from flask_login import current_user
from flask import current_app

def admin_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.config.get('TESTING') is False:
            if current_user.role != 'admin':
                abort(401)
            return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return decorated_view