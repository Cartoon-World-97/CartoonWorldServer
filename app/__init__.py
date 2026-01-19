from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_jwt_extended import JWTManager
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.model import db
from .routes.auth import auth_bp
from .routes.view import view_bp
from .routes.payments import payment_bp
from .routes.plans import plans_bp
from .config import DevelopmentConfig

from datetime import datetime
mail = Mail()
def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    # CORS(app)
    CORS(app, resources={r"/*": {"origins": "*"}})


    mail = Mail(app)
    JWTManager(app)
    db.init_app(app)

    S = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(view_bp, url_prefix="/")
    app.register_blueprint(payment_bp, url_prefix="/payments")
    app.register_blueprint(plans_bp, url_prefix="/plans")

    @app.route('/send-email', methods=['GET'])
    def send_email():
        msg = Message(
            subject="Test Email from Flask",
            recipients=["cartoonworld.server@gmail.com"],
            body="Hello, this is a test email sent using Flask-Mail.",
        )
        mail.send(msg)
        return jsonify({"Message": "Email sent successfully!"}), 200

    @app.route('/link', methods=['POST'])
    def send_link():
        email = request.json.get("Email")
        token = S.dumps(email, salt='email-confirm')
        return jsonify({
            'Message': f'Your confirmation link is valid for 10 minutes',
            'Token': token
        }), 200

    @app.route('/link_confirm', methods=['GET'])
    def link_confirm():
        token = request.args.get("Token")
        try:
            email = S.loads(token, salt='email-confirm', max_age=600)
        except SignatureExpired:
            return jsonify({'Message': 'The link has expired'}), 403
        except BadSignature:
            return jsonify({'Message': 'Invalid link'}), 403

        return redirect('http://localhost:5173/')

    return app
