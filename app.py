from flask import Flask, render_template, request, redirect, session, url_for, send_file
import pyrebase
import os
import pytz
import datetime
import uuid
from werkzeug.utils import secure_filename
from cleanup import remove_static_files
from pillow import (
    load_image,
    dupe_image,
    get_default_slider,
    apply_enhancers,
    apply_hue_shift,
    get_dominant_colors,
)
from pillow import apply_blur, apply_sharpen, apply_edge_enhance, apply_smooth
from pillow import get_image_size, rotate_image, resize_image, crop_image

app = Flask(__name__)
app.secret_key = "AI_IMAGE_EDIT"

firebaseConfig = {
    "apiKey": "AIzaSyCBoz2YzBThJVC1neWrH7UXfVOmGF5HjGk",
    "authDomain": "ai-image-edit-ba941.firebaseapp.com",
    "projectId": "ai-image-edit-ba941",
    "storageBucket": "ai-image-edit-ba941.appspot.com",
    "messagingSenderId": "943131642925",
    "appId": "1:943131642925:web:12e08da1625f39dcb83ca4",
    "databaseURL": "",
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate(
    "ai-image-edit-ba941-firebase-adminsdk-yir1p-607386ad8d.json"
)
firebase_admin.initialize_app(
    cred,
    {"storageBucket": "ai-image-edit-ba941.appspot.com"},
)
db = firestore.client()
bucket = storage.bucket()
user_ref = db.collection("users")

UPLOAD_FOLDER = "C:/Users/Dell/Software-Engineering/Login-Page/LOGIN-FORM2/static"
ALLOWED_EXTENSIONS = set(["png", "jpeg", "jpg"])
INPUT_FILENAME = ""
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024 * 1024

image, slider = None, None
colors = []
width, height = 0, 0


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def refresh_parameters(image_path):
    global image, slider, hue_angle, colors, width, height
    image = load_image(image_path)
    slider = get_default_slider()
    width, height = get_image_size(image)
    colors = get_dominant_colors(image_path)


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response


def save_to_firebase(image_path):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%d-%m-%Y %H:%M:%S")
    if "email" in session:
        email = session["email"]
        user_doc_ref = db.collection("users").where("email", "==", email).get()
        if user_doc_ref:
            user_doc_id = user_doc_ref[0].id
            filename = secure_filename(INPUT_FILENAME)

            uuid_str = str(uuid.uuid4())
            filename_with_uuid = f"{uuid_str}_{filename}"
            metadata = {"author": email, "timestamp": timestamp}
            blob = bucket.blob(f"images/{filename_with_uuid}")
            blob.metadata = metadata
            blob.upload_from_filename(image_path)

            image_url = blob.generate_signed_url(
                version="v4", expiration=datetime.timedelta(days=5)
            )

            # Update user document with the new image URL
            user_ref = db.collection("users").document(user_doc_id)
            user_ref.update({"image_urls": firestore.ArrayUnion([image_url])})


@app.route("/home", methods=["POST", "GET"])
def home():
    global INPUT_FILENAME
    global filepath
    if "email" not in session:
        return redirect(url_for("login"))

    image_urls = []
    if "email" in session:
        email = session["email"]
        user_doc_ref = db.collection("users").where("email", "==", email).get()
        if user_doc_ref:
            user_doc_id = user_doc_ref[0].id
            user_data = user_ref.document(user_doc_id).get().to_dict()
            if "image_urls" in user_data:
                image_urls = user_data["image_urls"]
                print(len(image_urls))
                # print(image_urls)
    if request.method == "POST":
        submit_button = request.form["submit_button"]

        if submit_button == "upload_image":

            if "file" not in request.files:
                return redirect(request.url)

            file = request.files["file"]

            if file.filename == "":
                return redirect(request.url)

            if file and allowed_file(file.filename):
                INPUT_FILENAME = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME))
                dupe_image(
                    os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME), "copy"
                )
                refresh_parameters(
                    os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME)
                )

                return redirect(url_for("uploaded"))

    return render_template("home.html", image_urls=image_urls)


@app.route("/uploaded", methods=["GET", "POST"])
def uploaded():
    global image, slider, hue_angle
    if INPUT_FILENAME:
        print(filepath)
        if request.method == "POST":
            home_button = request.form.get("home_button")
            original_button = request.form.get("original_button")
            download_button = request.form.get("download_button")
            enhance_button = request.form.get("enhance_button")
            # print("before hue")
            hue_button = request.form.get("hue_button")
            # print("after hue")
            blur_button = request.form.get("blur_button")
            sharpen_button = request.form.get("sharpen_button")
            edge_button = request.form.get("edge_button")
            smoothen_button = request.form.get("smoothen_button")
            rotate_button = request.form.get("rotate_button")
            resize_button = request.form.get("resize_button")
            crop_button = request.form.get("crop_button")
            if home_button:
                return redirect(url_for("home"))

            if original_button:
                dupe_image(
                    os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME), "replace"
                )
            if download_button:
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME)
                save_to_firebase(image_path)
                return send_file(
                    os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME),
                    as_attachment=True,
                )
            if enhance_button:
                print(slider)
                slider["color"] = float(request.form["color"])
                slider["bright"] = float(request.form["bright"])
                slider["sharp"] = float(request.form["sharp"])
                slider["contrast"] = float(request.form["contrast"])
                # print(slider)
                apply_enhancers(
                    image,
                    os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME),
                    slider,
                )
            if hue_button:
                hue_angle = float(request.form["hue_angle"])
                # print(hue_angle)
                apply_hue_shift(
                    os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME),
                    hue_angle,
                )
            if blur_button:
                apply_blur(
                    os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME),
                    # blur_button
                )
            if sharpen_button:
                apply_sharpen(os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME))
            if edge_button:
                apply_edge_enhance(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME))
            if smoothen_button:
                apply_smooth(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME))
            if rotate_button:
                angle = int(request.form["angle"])
                rotate_image(os.path.join(UPLOAD_FOLDER, INPUT_FILENAME), angle)
            if resize_button:
                n_width = int(request.form["width"])
                n_height = int(request.form["height"])
                resize_image(
                    os.path.join(UPLOAD_FOLDER, INPUT_FILENAME), n_width, n_height
                )
            if crop_button:
                start_x = int(request.form["start_x"])
                start_y = int(request.form["start_y"])
                end_x = int(request.form["end_x"])
                end_y = int(request.form["end_x"])
                # print(start_x, start_y, end_x, end_y)
                crop_image(
                    os.path.join(UPLOAD_FOLDER, INPUT_FILENAME),
                    start_x,
                    start_y,
                    end_x,
                    end_y,
                )
        return render_template(
            "uploaded.html",
            filename=INPUT_FILENAME,
            slider=slider,
            colors=colors,
            width=width,
            height=height,
        )

    return render_template("uploaded.html", slider=slider)


@app.route("/", methods=["POST", "GET"])
def login():
    if "username" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_id = user["localId"]
            doc_ref = db.collection("users").document(user_id)
            doc = doc_ref.get()
            user_data = doc.to_dict()
            name = user_data.get("name")
            session["email"] = email
            session["name"] = name

            return redirect(url_for("home"))
        except Exception as e:
            print(e)
            return "Failed to login"
    return render_template("index.html")


@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    try:
        user = auth.create_user_with_email_and_password(email, password)
        user_ref1 = user_ref.document(user["localId"])
        user_ref1.set({"email": email, "name": name})
        session["email"] = email
        session["name"] = name
        return redirect("/")
    except Exception as e:
        error_message = e
        print(error_message)
        # You can handle sign-up errors here (e.g., display error message on the sign-up form)
        return render_template("index.html", error=error_message)


@app.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("name", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
