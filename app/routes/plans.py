from flask import Blueprint, jsonify, request, current_app
from app.model.ProgramMaster import ProgramMaster 
from app.model import db
from flask_jwt_extended import create_access_token , jwt_required , get_jwt_identity
plans_bp = Blueprint("plans", __name__)

@plans_bp.route('/', methods=['POST'])
def planslist():
    plans = (
        db.session.query(ProgramMaster)
        .order_by(ProgramMaster.SL.asc())
        .all()
    )

    planslist = [
        {
            "SL": p.SL,
            "Program_ID": p.Program_ID,
            "Program_Name": p.Program_Name,
            "Program_Details": p.Program_Details,
            "Program_Img_Path": p.Program_Img_Path,
            "prev_price": p.prev_price,
            "Price": p.Price,
            "Duration": p.Duration,
            "Active_Sts": p.Active_Sts
        }
        for p in plans
    ]

    return jsonify({
        "status": True,
        "content": planslist
    }), 200

@plans_bp.route('/details', methods=['POST'])
@jwt_required()
def plansdetails():
    program_id = request.json.get("Program_ID")
    plan = (
        db.session.query(ProgramMaster).filter_by(Program_ID=program_id)
    )
    plandetails = [
        {
            "SL": p.SL,
            "Program_ID": p.Program_ID,
            "Program_Name": p.Program_Name,
            "Program_Details": p.Program_Details,
            "Program_Img_Path": p.Program_Img_Path,
            "prev_price": p.prev_price,
            "Price": p.Price,
            "Duration": p.Duration,
            "Active_Sts": p.Active_Sts
        }
        for p in plan
    ]
    return jsonify({
        "status": True,
        "content": plandetails
    }), 200
