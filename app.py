import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from database import (
    create_db_table,
    delete_user,
    get_user_by_id,
    get_users,
    insert_user,
    patch_user,
    update_user,
)

app = Flask(__name__)
CORS(app)
app.config["JSON_SORT_KEYS"] = False

REQUIRED_FIELDS = ["name", "email", "phone", "address", "country"]
ALLOWED_PATCH_FIELDS = REQUIRED_FIELDS


def json_error(message, status_code):
    return jsonify({"error": message}), status_code


@app.errorhandler(404)
def handle_not_found(error):
    return json_error("Resource not found", 404)


@app.errorhandler(405)
def handle_method_not_allowed(error):
    return json_error("Method not allowed", 405)


@app.errorhandler(500)
def handle_server_error(error):
    return json_error("Internal server error", 500)


@app.route("/api/users", methods=["GET"])
def get_all_users():
    users = get_users()
    return jsonify(users), 200


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_single_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return json_error("User not found", 404)
    return jsonify(user), 200


@app.route("/api/users/add", methods=["POST"])
def add_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return json_error("JSON body is required", 400)

    missing_fields = [field for field in REQUIRED_FIELDS if field not in data or data[field] is None or str(data[field]).strip() == ""]
    if missing_fields:
        return json_error(f"Missing required fields: {', '.join(missing_fields)}", 400)

    try:
        new_user = insert_user(data)
    except ValueError as exc:
        return json_error(str(exc), 400)
    except Exception:
        return json_error("Unable to create user", 500)

    if new_user is None:
        return json_error("Unable to create user", 500)

    return jsonify(new_user), 201


@app.route("/api/users/update", methods=["PUT"])
def update_existing_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return json_error("JSON body is required", 400)

    required_fields = ["user_id", *REQUIRED_FIELDS]
    missing_fields = [field for field in required_fields if field not in data or data[field] is None or str(data[field]).strip() == ""]
    if missing_fields:
        return json_error(f"Missing required fields: {', '.join(missing_fields)}", 400)

    try:
        user_id = int(data["user_id"])
    except (TypeError, ValueError):
        return json_error("user_id must be an integer", 400)

    user_payload = {
        "user_id": user_id,
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"],
        "address": data["address"],
        "country": data["country"],
    }

    try:
        updated_user = update_user(user_payload)
    except ValueError as exc:
        return json_error(str(exc), 400)

    if updated_user is None:
        return json_error("User not found", 404)

    return jsonify(updated_user), 200


@app.route("/api/users/<int:user_id>", methods=["PATCH"])
def patch_existing_user(user_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return json_error("JSON body is required", 400)

    invalid_fields = [field for field in data if field not in ALLOWED_PATCH_FIELDS]
    if invalid_fields:
        return json_error(f"Invalid field names: {', '.join(invalid_fields)}", 400)

    if "user_id" in data:
        return json_error("user_id cannot be changed using PATCH", 400)

    if not data:
        return json_error("No valid fields provided for update", 400)

    try:
        updated_user = patch_user(user_id, data)
    except ValueError as exc:
        return json_error(str(exc), 400)

    if updated_user is None:
        return json_error("User not found", 404)

    return jsonify(updated_user), 200


@app.route("/api/users/delete/<int:user_id>", methods=["DELETE"])
def delete_existing_user(user_id):
    deleted_count = delete_user(user_id)
    if deleted_count == 0:
        return json_error("User not found", 404)

    return jsonify({"status": "User deleted successfully"}), 200


create_db_table()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
