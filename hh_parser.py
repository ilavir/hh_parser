import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db, login
from app.models import User

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'login': login}

if __name__ == '__main__':
    app.run()