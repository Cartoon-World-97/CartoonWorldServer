from flask import Blueprint , request , jsonify, json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime,date,timedelta
from app.model.videoCategory import videoCategory
from app.model.videoMaster import videoMaster
from app.model.SubscriberMaster import SubscriberMaster
from app.model.SubCategory import SubCategory
from app.model.SearchHistory import SearchHistory
from app.model.WatchHistory import WatchHistory
from app.model.SubCategoryVideoList import SubCategoryVideoList
from flask_jwt_extended import create_access_token , jwt_required , get_jwt_identity
from app.model import db
from app.model.VideosCatList import VideosCatList
from app.model.playlistsMaster import playlistsMaster
from app.model.ActivePlans import ActivePlans
from app.model.ProgramMaster import ProgramMaster
from app.model.BannerSection import BannerSection
from flask_mail import Mail, Message  # ✅ Make sure Message is imported
from app import mail  # mail = Mail(app) in create_app()
view_bp = Blueprint("view", __name__) 

from flask_jwt_extended import jwt_required, get_jwt_identity
import json

def IsActive(plan_date, Duration):
    if date.today() <= plan_date + timedelta(days=Duration):
        return True
    else:
        return False
# @view_bp.route('/', methods=['GET'])
# @jwt_required(optional=True)   # allow both logged-in & guest
# def index():

#     user_id = get_jwt_identity()
#     data = request.get_json(silent=True) or {}

#     Limit = int(data.get('limit', 1))
#     page = int(data.get('page', 1))
#     # page = int(request.json.get('page', 1))
#     # Limit = int(request.json.get('limit', 1))
#     # print(Limit,page)
#     offsets = (page - 1) * Limit
#     FinalResponce = []
#     if page == 1:
#         # ------------------ User Watch History ----------------------
#         history_list = []

#         if user_id:
#             history = WatchHistory.query.filter_by(Sub_ID=user_id).first()

#             if history and history.Watch_Json:
#                 try:
#                     history_ids = json.loads(history.Watch_Json)
#                     history_id_list = [item['video_id'] for item in history_ids]
#                 except:
#                     history_id_list = []

#                 if len(history_ids) > 0:
#                     videos = (
#                         db.session.query(videoMaster)
#                         .filter(videoMaster.Video_ID.in_(history_id_list))
#                         .all()
#                     )
#                     history_list = [
#                         {
#                             "SL": v.SL,
#                             "Video_ID": v.Video_ID,
#                             "Category_ID": v.Category_ID,
#                             "Title": v.Title,
#                             "Description": v.Description,
#                             "Video_Url": v.Video_Url,
#                             "View": v.View,
#                             "Free": v.Free,
#                             "AD": v.AD,
#                             "Ad_Video_URL": v.Ad_Video_URL,
#                             "Into_Json": v.Into_Json,
#                         }
#                         for v in videos
#                     ]
#                     FinalResponce.append({
#                     "Name": "History Videos",
#                     "Is_title_Card": 0,
#                     "Videos": history_list
#                     })
        
            
#         # ------------------ Latest 10 videos ----------------------
#         LatestVideos = (
#             db.session.query(videoMaster)
#             .order_by(videoMaster.SL.desc())
#             .limit(10)
#             .all()
#         )

#         latest_list = [
#             {
#                 "SL": v.SL,
#                 "Video_ID": v.Video_ID,
#                 "Category_ID": v.Category_ID,
#                 "Title": v.Title,
#                 "Description": v.Description,
#                 "Video_Url": v.Video_Url,
#                 "View": v.View,
#                 "Free": v.Free,
#                 "AD": v.AD,
#                 "Ad_Video_URL": v.Ad_Video_URL,
#                 "Into_Json": v.Into_Json,
#             }
#             for v in LatestVideos
#         ]
#         FinalResponce.append({
#                     "Name": "Latest Videos",
#                     "Videos": latest_list
#                 })
#     # ------------------ Similar Videos (Recommended) ----------------------
#     videosListes = (
#         db.session.query(videoMaster, videoCategory)
#         .join(videoCategory, videoMaster.Category_ID == videoCategory.Category_ID)
#         .all()
#     )

#     documents = []
#     video_data = []
#     similar_videos = []

#     for v, c in videosListes:
#         text = f"{v.Title} {v.Description} {v.Content_Type} {c.Category_Name}".lower()
#         documents.append(text)
#         video_data.append((v, c))

#     vectorizer = TfidfVectorizer(stop_words="english")
#     tfidf_matrix = vectorizer.fit_transform(documents)

#     videosTypeListes = (
#     db.session.query(VideosCatList)
#     .filter(VideosCatList.Status == 1)
#     .limit(Limit)
#     .offset(offsets)
#     .all())
    
#     for videoType in videosTypeListes:
#         VideoListName = vectorizer.transform([videoType.Name])
#         scores = cosine_similarity(VideoListName, tfidf_matrix).flatten()
#         ranked_indices = scores.argsort()[::-1]

#         selected_indices = ranked_indices[1:10]

#         for idx in selected_indices:
#             if scores[idx] > 0:
#                 v, c = video_data[idx]
#                 similar_videos.append({
#                     "Video_ID": v.Video_ID,
#                     "Category_ID": v.Category_ID,
#                     "Category_Name": c.Category_Name,
#                     "Title": v.Title,
#                     "image": v.Thumbnail_URL,
#                     "Description": v.Description,
#                     "Video_Url": v.Video_Url,
#                     "Content_Type": v.Content_Type,
#                     "View": v.View,
#                     "Free": v.Free,
#                     "AD": v.AD,
#                     "Ad_Video_URL": v.Ad_Video_URL,
#                     "Into_Json": v.Into_Json,
#                 })
#         FinalResponce.append({
#                 "Name": videoType.Name,
#                 "Is_title_Card": videoType.Is_title_Card,
#                 "Videos": similar_videos
#             })
#     return jsonify(FinalResponce), 200


@view_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def index():

    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    limit = int(data.get('limit', 3))
    page = int(data.get('page', 1))
    offset = (page - 1) * limit

    FinalResponse = []

    # ------------------ PAGE 1 EXTRA DATA ------------------
    if page == 1:

        # ----------- History Videos -----------
        if user_id:
            history = WatchHistory.query.filter_by(Sub_ID=user_id).first()
            history_list = []

            if history and history.Watch_Json:
                try:
                    history_ids = json.loads(history.Watch_Json)
                    history_id_list = [i['video_id'] for i in history_ids]

                    videos = (
                        db.session.query(videoMaster)
                        .filter(videoMaster.Video_ID.in_(history_id_list))
                        .all()
                    )

                    history_list = [{
                        "Video_ID": v.Video_ID,
                        "Title": v.Title,
                        "image": v.Thumbnail_URL,
                        "Video_Url": v.Video_Url,
                        "View": v.View,
                        "Free": v.Free,
                        "AD": v.AD,
                        "Ad_Video_URL": v.Ad_Video_URL,
                        "Into_Json": v.Into_Json
                    } for v in videos]

                except:
                    history_list = []

            if history_list:
                FinalResponse.append({
                    "Name": "History Videos",
                    "Is_title_Card": 0,
                    "Videos": history_list
                })

        # ----------- Latest Videos -----------
        latest = (
            db.session.query(videoMaster)
            .order_by(videoMaster.SL.desc())
            .limit(10)
            .all()
        )

        FinalResponse.append({
            "Name": "Latest Videos",
            "Is_title_Card": 0,
            "Videos": [{
                "Video_ID": v.Video_ID,
                "image": v.Thumbnail_URL,
                "Title": v.Title,
                "Video_Url": v.Video_Url,
                "View": v.View,
                "Free": v.Free,
                "AD": v.AD,
                "Ad_Video_URL": v.Ad_Video_URL,
                "Into_Json": v.Into_Json
            } for v in latest]
        })

    # ------------------ PAGINATED SECTIONS ------------------
    video_types = (
        db.session.query(VideosCatList)
        .filter(VideosCatList.Status == 1)
        .limit(limit + 1)          # 👈 IMPORTANT
        .offset(offset)
        .all()
    )

    has_more = len(video_types) > limit
    video_types = video_types[:limit]   # trim extra one

    # ----------- TF-IDF PREP -----------
    videosList = (
        db.session.query(videoMaster, videoCategory)
        .join(videoCategory)
        .all()
    )

    documents = []
    video_data = []

    for v, c in videosList:
        documents.append(
            f"{v.Title} {v.Description} {v.Content_Type} {c.Category_Name}".lower()
        )
        video_data.append((v, c))

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    # ----------- BUILD SECTIONS -----------
    for videoType in video_types:
        similar_videos = []   # ✅ RESET HERE

        query_vec = vectorizer.transform([videoType.Name])
        scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
        ranked_indices = scores.argsort()[::-1][1:10]

        for idx in ranked_indices:
            if scores[idx] > 0:
                v, c = video_data[idx]
                similar_videos.append({
                    "Video_ID": v.Video_ID,
                    "Title": v.Title,
                    "image": v.Thumbnail_URL,
                    "Video_Url": v.Video_Url,
                    "View": v.View,
                    "Free": v.Free,
                    "AD": v.AD,
                    "Ad_Video_URL": v.Ad_Video_URL,
                    "Into_Json": v.Into_Json
                })

        FinalResponse.append({
            "Name": videoType.Name,
            "Is_title_Card": videoType.Is_title_Card,
            "Videos": similar_videos
        })

    return jsonify({
        "results": FinalResponse,
        "has_more": has_more,
        "page": page
    }), 200


@view_bp.route('/videolist', methods=['GET'])
def videolist():
    # Fetch all SubCategories
    subcategories = db.session.query(SubCategory).order_by(SubCategory.SL.asc()).all()

    # Prepare the response structure
    SubCategorylist = []

    for c in subcategories:
        # Fetch all active videos linked to this subcategory
        subcat_videos = db.session.query(SubCategoryVideoList).filter_by(
            Sub_Cat_Id=c.Sub_Cat_Id,
            Status=1
        ).all()


        VideoList = []
        for v in subcat_videos:
            video = db.session.query(videoMaster).filter_by(Video_ID=v.Video_ID).first()
            if video:  # Ensure video exists
                VideoList.append({
                    "SL": video.SL,
                    "Video_ID": video.Video_ID,
                    "Video_Url": video.Video_Url,
                    # "Date": video.Date.strftime("%Y-%m-%d") if video.Date else None,
                    # "Time": video.Time.strftime("%H:%M:%S") if video.Time else None,
                    # "Status": video.Status
                })

        # Add subcategory + its videos
        SubCategorylist.append({
            "SL": c.SL,
            "Sub_Cat_Id": c.Sub_Cat_Id,
            "Category_Title": c.Category_Title,
            "Date": c.Date.strftime("%Y-%m-%d") if c.Date else None,
            "Time": c.Time.strftime("%H:%M:%S") if c.Time else None,
            "Status": c.Status,
            "videos": VideoList
        })

    return jsonify({"status": True, "content": SubCategorylist}), 200

def saveWatchHistory(user_id, video_id):
    history_row = WatchHistory.query.filter_by(Sub_ID=user_id).first()

    if history_row:
        try:
            history_list = json.loads(history_row.Watch_Json or "[]")
        except:
            history_list = []
    else:
        history_row = WatchHistory(Sub_ID=user_id, Watch_Json="[]")
        history_list = []

    # remove if exists
    history_list = [h for h in history_list if h.get("video_id") != video_id]

    # keep max 5
    if len(history_list) >= 10:
        history_list.pop(0)

    history_list.append({"video_id": video_id})

    history_row.Watch_Json = json.dumps(history_list)
    db.session.add(history_row)
    db.session.commit()

@view_bp.route('/video', methods=['POST'])
@jwt_required()
def videoPlay():
    user_id = get_jwt_identity()
    user = SubscriberMaster.query.filter_by(Sub_ID=user_id).first()

    if not user:
        return jsonify({'Message': 'User not found'}), 404

    videoId = request.json.get('id')

    video = (
        db.session.query(videoMaster, videoCategory)
        .join(videoCategory, videoMaster.Category_ID == videoCategory.Category_ID)
        .filter(videoMaster.Video_ID == videoId)
        .first()
    )

    if not video:
        return jsonify({"status": False, "Message": "This Video Is Not Available!"}), 403

    vm, vc = video

    main_video = {
        "SL": vm.SL,
        "Video_ID": vm.Video_ID,
        "Category_ID": vm.Category_ID,
        "Category_Name": vc.Category_Name,
        "Title": vm.Title,
        "Description": vm.Description,
        "image": vm.Thumbnail_URL,
        "Video_Url": vm.Video_Url,
        "Content_Type": vm.Content_Type,
        "View": vm.View,
        "Free": vm.Free,
        "AD": vm.AD,
        "Ad_Video_URL": vm.Ad_Video_URL,
        "Into_Json": vm.Into_Json,
        "Date": vm.Date.strftime("%Y-%m-%d") if vm.Date else "",
        "Time": vm.Time.strftime("%H:%M:%S") if vm.Time else "",
    }

    # Similarity Text
    query_text = f"{vm.Title} {vm.Description} {vm.Content_Type} {vc.Category_Name}".lower()

    # Fetch all videos
    results = (
        db.session.query(videoMaster, videoCategory)
        .join(videoCategory, videoMaster.Category_ID == videoCategory.Category_ID)
        .all()
    )

    if not results:
        return jsonify({"status": True, "Video": main_video, "Similar": []}), 200

    documents, video_data = [], []

    for v, c in results:
        text = f"{v.Title} {v.Description} {v.Content_Type} {c.Category_Name}".lower()
        documents.append(text)
        video_data.append((v, c))

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    query_vec = vectorizer.transform([query_text])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    ranked_indices = scores.argsort()[::-1]
    selected_indices = ranked_indices[1:28]

    similar_videos = []

    for idx in selected_indices:
        if scores[idx] > 0:
            v, c = video_data[idx]
            similar_videos.append({
                "Video_ID": v.Video_ID,
                "Category_ID": v.Category_ID,
                "Category_Name": c.Category_Name,
                "Title": v.Title,
                "image": v.Thumbnail_URL,
                "Description": v.Description,
                "Video_Url": v.Video_Url,
                "Content_Type": v.Content_Type,
                "View": v.View,
                "Free": v.Free,
                "AD": v.AD,
                "Ad_Video_URL": v.Ad_Video_URL,
                "Into_Json": v.Into_Json,
            })
    saveWatchHistory(user_id, vm.Video_ID)
    return jsonify({
        "status": True,
        "Video": main_video,
        "Similar": similar_videos
    }), 200

@view_bp.route('/search', methods=['POST'])
@jwt_required(optional=True)
def search():
    user_id = get_jwt_identity()
    query = request.json.get('query', "").strip().lower()
    Limit = int(request.json.get('limit', 10))
    page = int(request.json.get('page', 1))
    types = request.json.get('type', '')

    new_data = {"query": query}

    results = (
        db.session.query(videoMaster, videoCategory)
        .join(videoCategory, videoMaster.Category_ID == videoCategory.Category_ID)
        .all()
    )

    if not results:
        return jsonify([]), 200

    documents = []
    video_data = []

    for v, c in results:
        text = f"{v.Title} {v.Description} {v.Content_Type} {c.Category_Name}".lower()
        documents.append(text)
        video_data.append((v, c))

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    ranked_indices = scores.argsort()[::-1]

    start = (page - 1) * Limit
    end = start + Limit
    selected = ranked_indices[start:end]
    data = []

    for idx in selected:
        if scores[idx] > 0: 
            v, c = video_data[idx]
            data.append({
                "Video_ID": v.Video_ID,
                "Category_ID": v.Category_ID,
                "Category_Name": c.Category_Name,
                "Title": v.Title,
                "image": v.Thumbnail_URL,
                "Description": v.Description,
                "Video_Url": v.Video_Url,
                "Content_Type": v.Content_Type,
                "View": v.View,
                "Free": v.Free,
                "AD": v.AD,
                "Ad_Video_URL": v.Ad_Video_URL,
                "Into_Json": v.Into_Json,
            })

    remaining_scores = scores[ranked_indices[end:]]
    has_more_relevant = any(s > 0 for s in remaining_scores)
    endList = not has_more_relevant

    if types == 'search':
        history_row = SearchHistory.query.filter_by(Sub_ID=user_id).first()

        
        if history_row:
            try:
                history_list = json.loads(history_row.Search_Json or "[]")
            except:
                history_list = []
        else:
            
            history_row = SearchHistory(Sub_ID=user_id, Search_Json="[]")
            history_list = []

        # Ensure list
        if not isinstance(history_list, list):
            history_list = []

        # ---------------------------------------------
        #  CHECK IF QUERY ALREADY EXISTS
        # ---------------------------------------------
        existing_index = next(
            (i for i, item in enumerate(history_list)
            if item.get("query") == new_data["query"]),
            None
        )

        if existing_index is not None:
            # Move existing item to position 5 (index=4)
            existing_item = history_list.pop(existing_index)

            insert_pos = 4  # 5th position
            if len(history_list) > insert_pos:
                history_list.insert(insert_pos, existing_item)
            else:
                history_list.append(existing_item)

        else:
            # ---------------------------------------------
            # NEW QUERY
            # Keep max 5 items — delete only if >5
            # ---------------------------------------------
            if len(history_list) >= 5:
                history_list.pop(0)   # delete oldest ONLY WHEN >5

            history_list.append(new_data)

        # Save back
        history_row.Search_Json = json.dumps(history_list)
        db.session.add(history_row)
        db.session.commit()

    if (types == 'fetchSuggestions' and query == '') or (types == 'fetchSuggestions' and len(data) == 0):
        history_row = SearchHistory.query.filter_by(Sub_ID=user_id).first()

        if history_row and history_row.Search_Json:
            try:
                history_list = json.loads(history_row.Search_Json)
            except:
                history_list = []
        else:
            history_list = []
        
        history_list = history_list[::-1]
        formatted_history = [{"Title": item.get("query", "")} for item in history_list]
        return jsonify({
            "results": formatted_history
        }), 200

    return jsonify({'Vidoes': data, 'endList': endList, 'query_ret': query}), 200

@view_bp.route('/page', methods=['POST'])
@jwt_required(optional=True)   # allow both logged-in & guest
def Movie():
    user_id = get_jwt_identity()

    data = request.get_json(silent=True) or {}

    Limit = int(data.get("limit", 10))
    page = int(data.get("page", 1))
    pageName = data.get("pageName", "")

    offsets = (page - 1) * Limit
    FinalResponce = []

    videosListes = (
        db.session.query(videoMaster, videoCategory)
        .join(videoCategory, videoMaster.Category_ID == videoCategory.Category_ID)
        .filter(videoCategory.Category_Name == pageName, videoMaster.Status == 1)
        .all()
    )

    documents = []
    video_data = []
    similar_videos = []

    if not videosListes:
        return jsonify({
            "data": FinalResponce,
            "hasMore": False,
            "page": page,
            "limit": Limit
        }), 200

    for v, c in videosListes:
        text = f"{v.Title} {v.Description} {v.Content_Type} {c.Category_Name}".lower()
        documents.append(text)
        video_data.append((v, c))

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    # 🔹 total count (ONLY for hasMore)
    total_count = (
        db.session.query(VideosCatList)
        .join(videoCategory, VideosCatList.Category_ID == videoCategory.Category_ID)
        .filter(
            VideosCatList.Status == 1,
            videoCategory.Category_Name == pageName,
        )
        .count()
    )

    hasMore = (offsets + Limit) < total_count

    videosTypeListes = (
        db.session.query(VideosCatList, videoCategory)
        .join(videoCategory, VideosCatList.Category_ID == videoCategory.Category_ID)
        .filter(
            VideosCatList.Status == 1,
            videoCategory.Category_Name == pageName,
        )
        .limit(Limit)
        .offset(offsets)
        .all()
    )

    if not videosTypeListes:
        return jsonify({
            "data": FinalResponce,
            "hasMore": hasMore,
            "page": page,
            "limit": Limit
        }), 200

    for videoType, cat in videosTypeListes:
        similar_videos = []

        VideoListName = vectorizer.transform([videoType.Name])
        scores = cosine_similarity(VideoListName, tfidf_matrix).flatten()
        ranked_indices = scores.argsort()[::-1]

        selected_indices = ranked_indices[1:10]

        for idx in selected_indices:
            if scores[idx] > 0:
                v, c = video_data[idx]
                similar_videos.append({
                    "Video_ID": v.Video_ID,
                    "Category_ID": v.Category_ID,
                    "Category_Name": c.Category_Name,
                    "Title": v.Title,
                    "image": v.Thumbnail_URL,
                    "Description": v.Description,
                    "Video_Url": v.Video_Url,
                    "Content_Type": v.Content_Type,
                    "View": v.View,
                    "Free": v.Free,
                    "AD": v.AD,
                    "Ad_Video_URL": v.Ad_Video_URL,
                    "Into_Json": v.Into_Json,
                })

        FinalResponce.append({
            "Name": videoType.Name,
            "Videos": similar_videos
        })

    return jsonify({
        "data": FinalResponce,
        "hasMore": hasMore,
        "page": page,
        "limit": Limit
    }), 200

@view_bp.route('/addList', methods=['POST'])
@jwt_required()
def addPlaylist():
    sub_id = get_jwt_identity()
    video_id = request.json.get('video_Id')

    if not video_id:
        return jsonify({"status": False, "message": "video_Id is required"}), 400
    existing_video_id = db.session.query(db.session.query(playlistsMaster).filter_by(Sub_ID=sub_id,Video_ID=video_id).exists()).scalar()
    if existing_video_id:
        return jsonify({"status": False, "message": "vidoe is alredy added"}), 200
    try:
        new_video = playlistsMaster(Sub_ID=sub_id, Video_ID=video_id)
        db.session.add(new_video)
        db.session.commit()
        
        return jsonify({
            "status": True,
            "message": "Video added to playlist successfully"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": False,
            "message": "Something went wrong",
        }), 500

@view_bp.route('/deleteList', methods=['POST'])
@jwt_required()
def deletePlaylist():
    sub_id = get_jwt_identity()
    video_id = request.json.get('video_Id')

    if not video_id:
        return jsonify({"status": False, "message": "video_Id is required"}), 400

    # Check if the record exists
    item = playlistsMaster.query.filter_by(Sub_ID=sub_id, Video_ID=video_id).first()

    if not item:
        return jsonify({
            "status": False,
            "message": "Video not found in playlist"
        }), 404

    try:
        db.session.delete(item)
        db.session.commit()

        return jsonify({
            "status": True,
            "message": "Video removed from playlist successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": False,
            "message": "Something went wrong",
            "error": str(e)
        }), 500
@view_bp.route('/videoList', methods=['POST'])
@jwt_required()
def VideoList():
    sub_id = get_jwt_identity()
    videos = (
        db.session.query(videoMaster)
        .join(playlistsMaster, playlistsMaster.Video_ID == videoMaster.Video_ID)
        .filter(playlistsMaster.Sub_ID == sub_id)
        .all()
    )

    video_list = [
        {
            "SL": v.SL,
            "Video_ID": v.Video_ID,
            "Category_ID": v.Category_ID,
            "Title": v.Title,
            "Description": v.Description,
            "Thumbnail_URL": v.Thumbnail_URL,
            "Video_Url": v.Video_Url,
            "Content_Type": v.Content_Type,
            "View": v.View,
            "Free": v.Free,
            "AD": v.AD,
            "Ad_Video_URL": v.Ad_Video_URL,
            "Into_Json": v.Into_Json,
            "Status": v.Status,
            "Date": v.Date.isoformat() if v.Date else None,
            "Time": v.Time.strftime("%H:%M:%S") if v.Time else None
        }
        for v in videos
    ]

    return jsonify({
        "status": True,
        "videos": video_list
    }), 200

@view_bp.route("/profile", methods=['POST'])
@jwt_required()
def porfile():
    user_id = get_jwt_identity()
    responce = []
    user = SubscriberMaster.query.filter_by(Sub_ID=user_id).first()
    responce.append({"Name":user.Name,"Email":user.Email})
    active_plans = (
        db.session.query(ActivePlans, ProgramMaster)
        .join(ProgramMaster, ActivePlans.Program_ID == ProgramMaster.Program_ID)
        .filter(
            ActivePlans.Sub_ID == user_id,
            ActivePlans.Status == 1
        )
        .all()
    )
    if active_plans :
      All_Active_Plans = []     
        # for plan, program in active_plans :
      for plan, program in active_plans:

         if IsActive(plan.Date,plan.Duration):
             All_Active_Plans.append({
            "Program_ID": program.Program_ID,
            "Program_Name": program.Program_Name,
            "Program_Details": program.Program_Details,
            "Program_Image": program.Program_Img_Path,
            "Price": program.Price,
            "Duration": plan.Duration,
            "Start_Date": plan.Date.strftime("%Y-%m-%d"),
            "Start_Time": plan.Time.strftime("%H:%M:%S"),
            "Status": plan.Status
        })
      responce.append({"ACtive_Plan":All_Active_Plans})
    else:
        plans = (
        db.session.query(ProgramMaster.Price)
        .order_by(ProgramMaster.Price.asc())
         .first())
        lowest_price = plans.Price if plans else None
        responce.append({"Lowest_Price": lowest_price})

    history = WatchHistory.query.filter_by(Sub_ID=user_id).first()
    
    if history and history.Watch_Json:
        try:
            history_ids = json.loads(history.Watch_Json)
            history_id_list = [item['video_id'] for item in history_ids]
        except:
            history_id_list = []
        if len(history_id_list) > 0:
                    videos = (
                        db.session.query(videoMaster)
                        .filter(videoMaster.Video_ID.in_(history_id_list))
                        .all()
                    )
                    history_list = [
                        {
                            "SL": v.SL,
                            "Video_ID": v.Video_ID,
                            "Category_ID": v.Category_ID,
                            "Title": v.Title,
                            "Description": v.Description,
                            "Video_Url": v.Video_Url,
                            "image": v.Thumbnail_URL,
                            "View": v.View,
                            "Free": v.Free,
                            "AD": v.AD,
                            "Ad_Video_URL": v.Ad_Video_URL,
                            "Into_Json": v.Into_Json,
                        }
                        for v in videos
                    ]
                    responce.append({
                    "History_Video": history_list
                })
    
    return jsonify(responce),200

@view_bp.route('/banner', methods=['POST'])
@jwt_required(optional=True)
def banner():
    user_id = get_jwt_identity()

    suggested_list = []

    # ================= USER HISTORY =================
    history = None
    if user_id:
        history = WatchHistory.query.filter_by(Sub_ID=user_id).first()

    if history and history.Watch_Json:
        try:
            history_ids = json.loads(history.Watch_Json)
            history_id_list = [item['video_id'] for item in history_ids]
        except:
            history_id_list = []
    else:
        history_id_list = []

    # ================= PERSONALIZED BANNER =================
    if len(history_id_list) > 0:
        watched_videos = (
            db.session.query(videoMaster)
            .filter(videoMaster.Video_ID.in_(history_id_list))
            .all()
        )

        if watched_videos:
            first_video = watched_videos[0]
            query = f"{first_video.Title} {first_video.Description}"

            results = (
                db.session.query(videoMaster, videoCategory)
                .join(videoCategory, videoMaster.Category_ID == videoCategory.Category_ID)
                .filter(~videoMaster.Video_ID.in_(history_id_list))
                .all()
            )

            documents = []
            video_data = []

            for v, c in results:
                documents.append(
                    f"{v.Title} {v.Description} {v.Content_Type} {c.Category_Name}".lower()
                )
                video_data.append((v, c))

            if documents:
                vectorizer = TfidfVectorizer(stop_words="english")
                tfidf_matrix = vectorizer.fit_transform(documents)

                query_vec = vectorizer.transform([query])
                scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

                ranked_indices = scores.argsort()[::-1][:5]

                for idx in ranked_indices:
                    if scores[idx] > 0:
                        v, c = video_data[idx]
                        suggested_list.append({
                            "Video_ID": v.Video_ID,
                            "Category_ID": v.Category_ID,
                            "Category_Name": c.Category_Name,
                            "Title": v.Title,
                            "image": v.Thumbnail_URL,
                            "Description": v.Description,
                            "Video_Url": v.Video_Url,
                            "Content_Type": v.Content_Type,
                            "View": v.View,
                            "Free": v.Free,
                            "AD": v.AD,
                            "Ad_Video_URL": v.Ad_Video_URL,
                            "Into_Json": v.Into_Json,
                        })

    # ================= NON-DEFAULT BANNER (FALLBACK) =================
    if not suggested_list:
        BannerVideos = (
            BannerSection.query
            .filter_by(Active_sts=1, Default=0)
            .order_by(BannerSection.SL.desc())
            .all()
        )

        for banner in BannerVideos:
            video = videoMaster.query.filter_by(Video_ID=banner.Video_ID).first()
            if video:
                suggested_list.append({
                    "Video_ID": video.Video_ID,
                    "Category_ID": video.Category_ID,
                    "Title": video.Title,
                    "image": video.Thumbnail_URL,
                    "Description": video.Description,
                    "Video_Url": video.Video_Url,
                    "Content_Type": video.Content_Type,
                    "View": video.View,
                    "Free": video.Free,
                    "AD": video.AD,
                    "Ad_Video_URL": video.Ad_Video_URL,
                    "Into_Json": video.Into_Json,
                })

    # ================= DEFAULT BANNER (ALWAYS APPEND) =================
    BannerDefaultVideos = (
        BannerSection.query
        .filter_by(Active_sts=1, Default=1)
        .order_by(BannerSection.SL.desc())
        .all()
    )

    for banner in BannerDefaultVideos:
        videoDefault = videoMaster.query.filter_by(Video_ID=banner.Video_ID).first()
        if videoDefault:
            suggested_list.append({
                "Video_ID": videoDefault.Video_ID,
                "Category_ID": videoDefault.Category_ID,
                "Title": videoDefault.Title,
                "image": videoDefault.Thumbnail_URL,
                "Description": videoDefault.Description,
                "Video_Url": videoDefault.Video_Url,
                "Content_Type": videoDefault.Content_Type,
                "View": videoDefault.View,
                "Free": videoDefault.Free,
                "AD": videoDefault.AD,
                "Ad_Video_URL": videoDefault.Ad_Video_URL,
                "Into_Json": videoDefault.Into_Json,
            })

    return jsonify({
        "status": True,
        "Banner_Suggestions": suggested_list
    }), 200

@view_bp.route('/category', methods=['POST'])
def category():
    data = []
    categories = db.session.query(videoCategory).order_by(videoCategory.Category_Name.asc()).all()
    for category in categories:
        data.append({
            "Category_ID": category.Category_ID,
            "Category_Name": category.Category_Name,
            "icon": category.icon,
            "Description": category.Description
        })
    return jsonify({"status": True, "categories": data}), 200

@view_bp.route("/renewurl", methods=["GET"])
def send_test_mail():
    return jsonify({"status": True}), 200
