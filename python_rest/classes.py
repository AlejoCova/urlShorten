"""JAMPP Url Shorten Restful API - CLASSES"""

from passlib.apps import custom_app_context as pwd_context

from extensions import DB, AUTH

@AUTH.verify_password
def verify_password(username, password):
    """Verify user passwords callback function."""
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class User(DB.Model):
    """User class for login."""
    __tablename__ = 'users'
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(32), index=True)
    password_hash = DB.Column(DB.String(128))

    def hash_password(self, password):
        """Hash user passwords."""
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Verify user passwords."""
        return pwd_context.verify(password, self.password_hash)