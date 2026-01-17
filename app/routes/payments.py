from datetime import datetime, timedelta
from flask_mail import Mail, Message
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.model import db
from app.model.TransactionDetails import TransactionDetails
from app.model.ActivePlans import ActivePlans
from app.model.ProgramMaster import ProgramMaster
from app.model.SubscriberMaster import SubscriberMaster
import requests
import base64

payment_bp = Blueprint("payments", __name__)


# =====================================================
# 🔹 1. Generate PayPal Access Token
# =====================================================
def generate_access_token():
    client_id = current_app.config["PAYPAL_CLIENT_ID"]
    secret = current_app.config["PAYPAL_SECRET"]
    paypal_api = current_app.config["PAYPAL_API"]

    # Encode client id + secret
    auth_string = f"{client_id}:{secret}".encode("utf-8")
    b64_auth = base64.b64encode(auth_string).decode("utf-8")

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}

    response = requests.post(
        f"{paypal_api}/v1/oauth2/token",
        headers=headers,
        data=data
    )

    return response.json().get("access_token")


# =====================================================
# 🔹 2. Create PayPal Order  (POST /payments/)
# =====================================================
@payment_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    paypal_api = current_app.config["PAYPAL_API"]
    access_token = generate_access_token()

    user_id = get_jwt_identity()   # 🔐 from JWT
    amount = request.json.get("amount", 10)
    Program_ID = request.json.get("Program_ID")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    body = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": str(amount)
            }
        }]
    }

    response = requests.post(
        f"{paypal_api}/v2/checkout/orders",
        headers=headers,
        json=body
    )

    data = response.json()
    order_id = data.get("id")

    # 🔹 Save PENDING transaction
    txn = TransactionDetails(
        Sub_ID=user_id,
        Txn_ID=order_id,
        Card_Category="PAYPAL",
        Txn_Category="ONLINE",
        Program_ID=Program_ID,
        Amount=amount,
        Status="PENDING"
    )

    db.session.add(txn)
    db.session.commit()

    approve_link = next(
        (l["href"] for l in data.get("links", []) if l["rel"] == "approve"),
        None
    )

    return jsonify({
        "order_id": order_id,
        "approve_link": approve_link
    })


# =====================================================
# 🔹 3. Capture Payment  (POST /payments/capture/<order_id>)
# =====================================================
@payment_bp.route('/capture/<order_id>', methods=['POST'])
@jwt_required()
def capture_payment(order_id):
    paypal_api = current_app.config["PAYPAL_API"]
    access_token = generate_access_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(
        f"{paypal_api}/v2/checkout/orders/{order_id}/capture",
        headers=headers
    )

    result = response.json()
    status = result.get("status")

    txn = TransactionDetails.query.filter_by(Txn_ID=order_id).first()

    if txn:
        txn.Status = "SUCCESS" if status == "COMPLETED" else "FAILED"
        db.session.commit()

    return jsonify(result)



# =====================================================
# 🔹 4. Webhook (PayPal → Your Server)
# =====================================================
# @payment_bp.route('/webhook', methods=['POST'])
# def paypal_webhook():
#     data = request.json
#     event = data.get("event_type")

#     if event == "PAYMENT.CAPTURE.COMPLETED":
#         order_id = data["resource"]["supplementary_data"]["related_ids"]["order_id"]
        
#         txn = TransactionDetails.query.filter_by(Txn_ID=order_id).first()
#         Program = ProgramMaster.query.filter_by(Program_ID=txn.Program_ID).first()
#         subcriber = SubscriberMaster.query.filter_by(Sub_ID=txn.Sub_ID).first()
#         Active_Plan = ActivePlans(
#             Sub_ID=txn.Sub_ID,
#             Program_ID=txn.Program_ID,
#             Duration=Program.Duration
#         );
#         if txn:
#             txn.Status = "SUCCESS"
#             db.session.commit()
#         def send_invoice_email(email, name, invoice_no, program_name, amount, txn_id):
#                 mail = current_app.extensions.get('mail')
#                 if not mail:
#                         return False

#                 msg = Message(
#                         subject="Payment Invoice – Thank You for Your Purchase",
#                         sender=current_app.config['MAIL_USERNAME'],
#                         recipients=[email],
#                         body=f"""
#                 Hello {name},

#                 Thank you for your payment! 🎉

#                 Here are your invoice details:

#                 Invoice No   : {invoice_no}
#                 Program      : {program_name}
#                 Amount Paid  : ₹{amount}
#                 Transaction  : {txn_id}
#                 Date         : {datetime.now().strftime('%d %b %Y, %I:%M %p')}

#                 If you have any questions, feel free to contact our support team.

#                 Regards,
#                 Cartoon World Team
#                 """
#                     )
#                 mail.send(msg)
#                 return True
#         send_invoice_email()

#     elif event == "PAYMENT.CAPTURE.DENIED":
#         order_id = data["resource"]["supplementary_data"]["related_ids"]["order_id"]

#         txn = TransactionDetails.query.filter_by(Txn_ID=order_id).first()
#         if txn:
#             txn.Status = "FAILED"
#             db.session.commit()

#     return jsonify({"status": "OK"}), 200



def send_invoice_email(email, name, invoice_no, program_name, amount, txn_id):
    mail = current_app.extensions.get('mail')
    if not mail:
        return

    msg = Message(
        subject="Payment Invoice – Thank You for Your Purchase",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email],
        body=f"""
Hello {name},

Thank you for your payment! 🎉

Invoice Details:
-------------------------
Invoice No   : {invoice_no}
Program      : {program_name}
Amount Paid  : ₹{amount}
Transaction  : {txn_id}
Date         : {datetime.now().strftime('%d %b %Y, %I:%M %p')}

Regards,
Cartoon World Team
"""
    )
    mail.send(msg)


def send_plan_activation_email(email, name, program_name, duration):
    mail = current_app.extensions.get('mail')
    if not mail:
        return

    start_date = datetime.now()
    end_date = start_date + timedelta(days=duration)

    msg = Message(
        subject="Your Subscription is Now Active 🎉",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email],
        body=f"""
Hello {name},

Your subscription has been activated successfully 🚀

Plan Name   : {program_name}
Start Date : {start_date.strftime('%d %b %Y')}
End Date   : {end_date.strftime('%d %b %Y')}

Enjoy unlimited entertainment!

Regards,
Cartoon World Team
"""
    )
    mail.send(msg)


# ---------------- PAYPAL WEBHOOK ---------------- #

@payment_bp.route('/webhook', methods=['POST'])
def paypal_webhook():
    data = request.get_json(silent=True)
    event = data.get("event_type") if data else None

    if event == "PAYMENT.CAPTURE.COMPLETED":
        try:
            order_id = data["resource"]["supplementary_data"]["related_ids"]["order_id"]

            txn = TransactionDetails.query.filter_by(Txn_ID=order_id).first()
            if not txn:
                return jsonify({"status": "txn not found"}), 200

            program = ProgramMaster.query.filter_by(
                Program_ID=txn.Program_ID
            ).first()

            subscriber = SubscriberMaster.query.filter_by(
                Sub_ID=txn.Sub_ID
            ).first()

            # Update transaction
            txn.Status = "SUCCESS"

            # Activate plan
            active_plan = ActivePlans(
                Sub_ID=txn.Sub_ID,
                Program_ID=txn.Program_ID,
                Duration=program.Duration
            )
            db.session.add(active_plan)
            db.session.commit()

            # Send emails
            send_invoice_email(
                email=subscriber.Email,
                name=subscriber.Name,
                invoice_no=f"INV-{txn.Txn_ID}",
                program_name=program.Program_Name,
                amount=program.Price,
                txn_id=txn.Txn_ID
            )

            send_plan_activation_email(
                email=subscriber.Email,
                name=subscriber.Name,
                program_name=program.Program_Name,
                duration=program.Duration
            )

        except Exception as e:
            current_app.logger.error(f"Webhook error: {e}")

    elif event == "PAYMENT.CAPTURE.DENIED":
        order_id = data["resource"]["supplementary_data"]["related_ids"]["order_id"]
        txn = TransactionDetails.query.filter_by(Txn_ID=order_id).first()
        if txn:
            txn.Status = "FAILED"
            db.session.commit()

    # PayPal requires 200 always
    return jsonify({"status": "OK"}), 200