from app import db
from app.models.video import Video
from app.models.rental import Rental
from flask import request, Blueprint, jsonify

videos_bp = Blueprint("videos_bp", __name__, url_prefix="/videos")


@videos_bp.route("", methods=["POST"])
def post_videos():
    request_body = request.get_json()
    if "title" not in request_body:
        return jsonify(details="Request body must include title."), 400
    elif "release_date" not in request_body:
        return jsonify(details="Request body must include release_date."), 400
    elif "total_inventory" not in request_body:
        return jsonify(details="Request body must include total_inventory."), 400
    new_video=Video.from_json(request_body)

    db.session.add(new_video)
    db.session.commit()

    return jsonify(new_video.to_json()), 201
        
@videos_bp.route("", methods=["GET"])
def get_videos():
    videos = Video.query.all()
    response_body = []
    for video in videos:
        response_body.append(video.to_json())
    return jsonify(response_body), 200


@videos_bp.route("/<video_id>", methods=["GET"])
def get_video(video_id):
    if not video_id.isnumeric():
        return jsonify("Video id must be an integer"), 400

    video = Video.query.get(video_id)
    if video is None:
        return jsonify(message=f"Video {video_id} was not found"), 404

    return jsonify(video.to_json()), 200

@videos_bp.route("/<video_id>", methods=["PUT"])
def put_video(video_id):
    if not video_id.isnumeric():
        return jsonify("Video id must be an integer"), 400
    video = Video.query.get(video_id)
    if video is None:
        return jsonify(message=f"Video {video_id} was not found"), 404

    request_body = request.get_json()
    if "title" not in request_body:
        return jsonify("Request body must include title."), 400
    elif "release_date" not in request_body:
        return jsonify("Request body must include release_date."), 400
    elif "total_inventory" not in request_body:
        return jsonify("Request body must include total_inventory."), 400
    elif type(request_body["total_inventory"]) != int:   
        return jsonify("Total_inventory must be an integer."), 400

    video.title = request_body["title"]
    video.release_date = request_body["release_date"]
    video.total_inventory = request_body["total_inventory"]
    db.session.commit()
    return jsonify(video.to_json()), 200


@videos_bp.route("/<video_id>", methods=["DELETE"])
def delete_video(video_id):
    if not video_id.isnumeric():
        return jsonify("Video id must be an integer"), 400

    video = Video.query.get(video_id)
    if video is None:
        return jsonify(message=f"Video {video_id} was not found"), 404

    db.session.delete(video)
    db.session.commit()
    return jsonify(id=video.id), 200


@videos_bp.route("/<video_id>/rentals", methods=["GET"])
def handle_video_rentals(video_id):
    if not video_id.isnumeric():
        return jsonify("Video id must be an integer"), 400

    video = Video.query.get(video_id)
    if video is None:
        return jsonify(message=f"Video {video_id} was not found"), 404
    customers = video.customers
    customers_response = []
    for customer in customers:
        customer_info = customer.to_json()
        customer_info.pop("id")
        customer_info.pop("registered_at")
        customer_info["due_date"] = Rental.query.get((customer.id, video.id)).due_date
        customers_response.append(customer_info)
    return jsonify(customers_response), 200        