from flask import Flask, render_template
from .config import Config
from .extensions import login_manager, init_mongo
from .routes.auth import auth_bp
from .routes.home import home_bp
from .routes.mood import mood_bp
from .routes.journal import journal_bp
from .routes.stories import stories_bp
from .routes.prompts import prompts_bp
from .routes.chat import chat_bp
from .routes.dashboard import dashboard_bp
from .routes.profile import profile_bp
from .routes.resources import resources_bp
from .models import User
from .routes.comfort import comfort_bp
from .routes.counselor import counselor_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_mongo(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(mood_bp, url_prefix="/mood")
    app.register_blueprint(journal_bp, url_prefix="/journal")
    app.register_blueprint(stories_bp, url_prefix="/stories")
    app.register_blueprint(prompts_bp, url_prefix="/prompts")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(resources_bp, url_prefix="/resources")
    app.register_blueprint(comfort_bp, url_prefix="/comfort")
    app.register_blueprint(counselor_bp, url_prefix="/counselor")

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(_):
        return render_template("500.html"), 500

    return app
