from flask import Blueprint, request, jsonify,current_app,redirect
from werkzeug.security import generate_password_hash , check_password_hash
import uuid
from flask_mail import Mail, Message
from flask_jwt_extended import create_access_token , jwt_required , get_jwt_identity,create_refresh_token
from itsdangerous import URLSafeTimedSerializer,SignatureExpired,BadSignature
from app.model import db
from app.model.SubscriberMaster import SubscriberMaster

auth_bp = Blueprint("auth", __name__)


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

    existing_email = db.session.query(db.session.query(SubscriberMaster).filter_by(Email=email,User_Verification=True).exists()).scalar()

    if existing_email:
        return jsonify({"status":False,"Message": "User already exists"}), 200
    S = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    existing_email_Not_Verified = db.session.query(db.session.query(SubscriberMaster).filter_by(Email=email).exists()).scalar()
    token = S.dumps(email, salt='email-confirm')
    sub_id = generate_sub_id()
    hashed_password = generate_password_hash(password)
    entry = SubscriberMaster(
        Sub_ID=sub_id,
        Name=name,
        Email=email,
        Password=hashed_password,
        Ver_Url = token
    )
    try:
        if not existing_email_Not_Verified:
          db.session.add(entry)
        else :
          SubscriberMaster.query.filter_by(Email=email).update({"Name":name,
        "Email":email,
        "Password":hashed_password,"Ver_Url": token})
        db.session.commit()
        mail = current_app.extensions.get('mail')
        if mail:
            confirm_link = f"http://127.0.0.1:5000/auth/verify?token={token}"  # Change to your frontend URL
            msg = Message(
                subject="Confirm Your Email",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"Hello {name},\n\nPlease confirm your email by clicking the link below:\n{confirm_link}\n\nThis link is valid for 10 minutes."
            )
            mail.send(msg)
        return jsonify({
            "status":True,
            "Message": f"{name} registered successfully. Please confirm your email."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"Message": f"Database error: {str(e)}"}), 500
    
@auth_bp.route("/verify", methods=['GET'])
def verify():
    Token = request.args.get('token')
    S = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
       email = S.loads(Token, salt='email-confirm',max_age =500)
    except SignatureExpired:
        return jsonify({'Massage':f'The Link Has Expire {email}'}),403
    except BadSignature:
        return jsonify({'Massage':f'The Link Has Expire {email}'}),403
    existing_email = db.session.query(db.session.query(SubscriberMaster).filter_by(Email=email,Ver_Url=Token).exists()).scalar()
    if not existing_email :
        return jsonify({'Massage':f'The Link Has Expire {email}'}),403
    try:
        db.session.query(SubscriberMaster).filter_by(Email=email).update({"User_Verification": True})
        db.session.commit()
        return redirect('https://localhost:5173/signin'),200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500 

@auth_bp.route("/login", methods=['POST'])
def Login():
    email = request.json.get('email').strip()
    password = request.json.get('password').strip()
    auth = request.headers.get('Authxxxxx')
    if auth != 'XYZ':
        return jsonify({"Message": "Unauthorized request"}), 403
    if  not email or not password:
        return jsonify({"Status":False,"Message": "All fields are required"}), 400
    user = SubscriberMaster.query.filter_by(Email=email).first()
    if not user or user.User_Verification == False:
        return jsonify({"Status":False,"Message":"User Is Not Exites"}),200
    if not check_password_hash(user.Password, password):
        return jsonify({"Status":False,"Message":"Wrong Password"}),200
    token = create_access_token(identity=user.Sub_ID)
    refresh = create_refresh_token(identity=user.Sub_ID)
    return jsonify({"Status":True,'Message':'Login successfully','token':f'{token}'}),200 

@auth_bp.route("/resetpass", methods=['POST'])
def ResetPass():
   auth = request.headers.get('Authxxxxx')
   if auth != 'XYZ':
        return jsonify({"Status":False,"Message": "Unauthorized request"}), 403
    
   email = request.json.get('email')
   user = SubscriberMaster.query.filter_by(Email = email).first()
   if not user :
       return jsonify({"Status":False,"Message":"User Is Not Exits"}),403
   S = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
   token = S.dumps(user.Sub_ID, salt='email-confirm')
   mail = current_app.extensions.get('mail')
   if mail:
        confirm_link = f"http://127.0.0.1:5000/auth/resetverify?token={token}"  # Change to your frontend URL
        msg = Message(
        subject="Confirm Your Email",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email],
        body=f"Hello {user.Name},\n\nPlease confirm your email by clicking the link below:\n{confirm_link}\n\nThis link is valid for 10 minutes."
        )
        mail.send(msg)
        db.session.query(SubscriberMaster).filter_by(Email=email).update({"Ver_Url": token})
        db.session.commit()
   return jsonify({"Status":True,
            "Message": f"{user.Name} Please confirm your email.",
        }), 201

@auth_bp.route("/resetverify", methods=['GET'])
def Resetverify():
    Token = request.args.get('token')
    S = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
       id = S.loads(Token, salt='email-confirm' ,max_age =500)
    except SignatureExpired:
        return jsonify({'Massage':f'The Link Has Expire'}),403
    except BadSignature:
        return jsonify({'Massage':f'The Link Has Expire'}),403
    token = S.dumps(id, salt='set passWord')
    user = SubscriberMaster.query.filter_by(Sub_ID=id, Ver_Url=Token).first()

    if not user:
        return jsonify({'Status': False, 'Message': 'This reset link has expired or is invalid.'}), 403
    
    db.session.query(SubscriberMaster).filter_by(Sub_ID=id).update({"Ver_Url": token})
    db.session.commit()
    return redirect(f'http://localhost:5173/resetpassword?token={token}')
@auth_bp.route("/setpass", methods=['POST'])
def setPass():
    auth = request.headers.get('Authxxxxx')
    if auth != 'XYZ':
        return jsonify({"Status":False,"Message": "Unauthorized request"}), 403
    password = request.json.get('password').strip()
    token = request.json.get('token').strip()
    if not token or not password:
            return jsonify({"Status":False,"Message": "Unauthorized request"}), 403

    S = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
      id = S.loads(token , salt='set passWord' , max_age=500)
    except SignatureExpired :
        return jsonify({'Message':f'request Time Out ,Please request a new password reset'}),403
    except BadSignature:
        return jsonify({'Message':f'Something Went Wrong!'}),403
    user = SubscriberMaster.query.filter_by(Sub_ID=id, Ver_Url=token).first()
    if not user:
        return jsonify({'Status': False, 'Message': 'This reset link has expired or is invalid.'}), 403
    try:
        db.session.query(SubscriberMaster).filter_by(Sub_ID = id).update({"Password":generate_password_hash(password)})
        db.session.commit()
        return jsonify({"Status":True,"Message":"password updated Successfully"}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({"Message": f"Database error: {str(e)}"}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access=access_token)
 

 
