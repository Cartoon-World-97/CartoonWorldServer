from flask import Blueprint, request, jsonify, current_app, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
# from flask_mail import Mail, Message   # ❌ COMMENTED (not deleted)
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token
)
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.model import db
from app.model.SubscriberMaster import SubscriberMaster
import requests   # ✅ ADDED

auth_bp = Blueprint("auth", __name__)

MAIL_API_URL = "https://cartoonworldmailsender.vercel.app/send-mail"


def generate_sub_id():
    while True:
        new_uuid = str(uuid.uuid4())
        if not SubscriberMaster.query.filter_by(Sub_ID=new_uuid).first():
            return new_uuid


@auth_bp.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    auth = request.headers.get('Authxxxxx')
    if auth != 'XYZ':
        return jsonify({"Message": "Unauthorized request"}), 403

    if not name or not email or not password:
        return jsonify({"Message": "All fields are required"}), 400

    existing_email = db.session.query(
        db.session.query(SubscriberMaster)
        .filter_by(Email=email, User_Verification=True)
        .exists()
    ).scalar()

    if existing_email:
        return jsonify({"status": False, "Message": "User already exists"}), 200

    S = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = S.dumps(email, salt='email-confirm')
    sub_id = generate_sub_id()
    hashed_password = generate_password_hash(password)

    entry = SubscriberMaster(
        Sub_ID=sub_id,
        Name=name,
        Email=email,
        Password=hashed_password,
        Ver_Url=token
    )

    try:
        existing_not_verified = db.session.query(
            db.session.query(SubscriberMaster).filter_by(Email=email).exists()
        ).scalar()

        if not existing_not_verified:
            db.session.add(entry)
        else:
            SubscriberMaster.query.filter_by(Email=email).update({
                "Name": name,
                "Password": hashed_password,
                "Ver_Url": token
            })

        db.session.commit()

        # ===============================
        # ❌ FLASK MAIL (COMMENTED)
        # ===============================
        # mail = current_app.extensions.get('mail')
        # if mail:
        #     msg = Message(...)
        #     mail.send(msg)

        # ===============================
        # ✅ EXTERNAL MAIL API
        # ===============================
        confirm_link = f"http://127.0.0.1:5000/auth/verify?token={token}"

        requests.post(
            MAIL_API_URL,
            json={
                "to": email,
                "subject": "Confirm Your Email",
                "message": f"Hello {name},\n\nPlease confirm your email:\n{confirm_link}"
            },
            timeout=10
        )

        return jsonify({
            "status": True,
            "Message": f"{name} registered successfully. Please confirm your email."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"Message": f"Database error: {str(e)}"}), 500


@auth_bp.route("/verify", methods=['GET'])
def verify():
    Token = request.args.get('token')
    S = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        email = S.loads(Token, salt='email-confirm', max_age=500)
    except (SignatureExpired, BadSignature):
        return jsonify({'Message': 'The link has expired'}), 403

    user = SubscriberMaster.query.filter_by(Email=email, Ver_Url=Token).first()
    if not user:
        return jsonify({'Message': 'Invalid or expired link'}), 403

    db.session.query(SubscriberMaster).filter_by(Email=email).update({
        "User_Verification": True
    })
    db.session.commit()

    return redirect('https://localhost:5173/signin')


@auth_bp.route("/login", methods=['POST'])
def Login():
    email = request.json.get('email').strip()
    password = request.json.get('password').strip()

    auth = request.headers.get('Authxxxxx')
    if auth != 'XYZ':
        return jsonify({"Message": "Unauthorized request"}), 403

    user = SubscriberMaster.query.filter_by(Email=email).first()
    if not user or not user.User_Verification:
        return jsonify({"Status": False, "Message": "User does not exist"}), 200

    if not check_password_hash(user.Password, password):
        return jsonify({"Status": False, "Message": "Wrong password"}), 200

    token = create_access_token(identity=user.Sub_ID)
    refresh = create_refresh_token(identity=user.Sub_ID)

    return jsonify({
        "Status": True,
        "Message": "Login successful",
        "token": token,
        "refresh": refresh
    }), 200


@auth_bp.route("/resetpass", methods=['POST'])
def ResetPass():
    auth = request.headers.get('Authxxxxx')
    if auth != 'XYZ':
        return jsonify({"Status": False, "Message": "Unauthorized request"}), 403

    email = request.json.get('email')
    user = SubscriberMaster.query.filter_by(Email=email).first()
    if not user:
        return jsonify({"Status": False, "Message": "User not found"}), 403

    S = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = S.dumps(user.Sub_ID, salt='email-confirm')

    reset_link = f"http://127.0.0.1:5000/auth/resetverify?token={token}"

    requests.post(
        MAIL_API_URL,
        json={
            "to": email,
            "subject": "Password Reset",
            "message": f"Hello {user.Name},\n\nReset your password:\n{reset_link}"
        },
        timeout=10
    )

    SubscriberMaster.query.filter_by(Email=email).update({"Ver_Url": token})
    db.session.commit()

    return jsonify({
        "Status": True,
        "Message": "Password reset email sent"
    }), 201


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access=access_token)
