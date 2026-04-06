from flask import Flask, render_template, request, redirect, session, url_for, send_file
import os
import pytz
import datetime
import uuid
import logging
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
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

import firebase_admin
from firebase_admin import credentials, firestore, storage
from firebase_auth import signup_with_email_password, login_with_email_password

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "AI_IMAGE_EDIT")

logger.info("=" * 50)
logger.info("Starting AI Image Edit Application")
logger.info("=" * 50)

try:
    # Get Firebase credentials path from environment variables
    firebase_creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    firebase_storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET", "ai-image-edit-ba941.appspot.com")
    
    logger.info(f"Loading Firebase credentials from: {firebase_creds_path}")
    cred = credentials.Certificate(firebase_creds_path)
    logger.info("✓ Firebase credentials loaded successfully")
    
    logger.info("Initializing Firebase app...")
    firebase_admin.initialize_app(
        cred,
        {"storageBucket": firebase_storage_bucket},
    )
    logger.info("✓ Firebase app initialized successfully")
    
    logger.info("Connecting to Firestore database...")
    db = firestore.client()
    logger.info("✓ Firestore connection successful")
    
    logger.info("Connecting to Firebase Storage bucket...")
    bucket = storage.bucket()
    logger.info("✓ Firebase Storage connection successful")
    
    logger.info("Getting 'users' collection reference...")
    user_ref = db.collection("users")
    logger.info("✓ Users collection reference obtained")
    
except Exception as e:
    logger.error(f"✗ Firebase initialization failed: {str(e)}", exc_info=True)
    raise

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
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
    logger.info(f"[FIREBASE] Starting image save process for: {image_path}")
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%d-%m-%Y %H:%M:%S")
    
    if "email" in session:
        email = session["email"]
        logger.info(f"[FIREBASE] User email found in session: {email}")
        
        try:
            logger.info(f"[FIREBASE] Querying database for user with email: {email}")
            user_doc_ref = db.collection("users").where("email", "==", email).get()
            logger.info(f"[FIREBASE] Query returned {len(user_doc_ref)} document(s)")
            
            if user_doc_ref:
                user_doc_id = user_doc_ref[0].id
                logger.info(f"[FIREBASE] User document ID: {user_doc_id}")
                
                filename = secure_filename(INPUT_FILENAME)
                logger.info(f"[FIREBASE] Original filename: {INPUT_FILENAME}")
                logger.info(f"[FIREBASE] Secure filename: {filename}")

                uuid_str = str(uuid.uuid4())
                filename_with_uuid = f"{uuid_str}_{filename}"
                logger.info(f"[FIREBASE] Generated unique filename: {filename_with_uuid}")
                
                metadata = {"author": email, "timestamp": timestamp}
                logger.info(f"[FIREBASE] Image metadata: {metadata}")
                
                logger.info(f"[FIREBASE] Uploading file to storage: images/{filename_with_uuid}")
                blob = bucket.blob(f"images/{filename_with_uuid}")
                blob.metadata = metadata
                blob.upload_from_filename(image_path)
                logger.info(f"✓ [FIREBASE] File uploaded successfully to storage")

                logger.info(f"[FIREBASE] Generating signed URL (5-day expiration)...")
                image_url = blob.generate_signed_url(
                    version="v4", expiration=datetime.timedelta(days=5)
                )
                logger.info(f"✓ [FIREBASE] Signed URL generated: {image_url[:50]}...")

                logger.info(f"[FIREBASE] Updating user document with image URL...")
                user_ref_doc = db.collection("users").document(user_doc_id)
                user_ref_doc.update({"image_urls": firestore.ArrayUnion([image_url])})
                logger.info(f"✓ [FIREBASE] User document updated successfully")
                
            else:
                logger.warning(f"[FIREBASE] No user document found for email: {email}")
        except Exception as e:
            logger.error(f"✗ [FIREBASE] Error during image save: {str(e)}", exc_info=True)
            raise
    else:
        logger.warning("[FIREBASE] No email found in session")


@app.route("/home", methods=["POST", "GET"])
def home():
    logger.info("[HOME] Home route accessed")
    global INPUT_FILENAME
    global filepath
    if "email" not in session:
        logger.warning("[HOME] User not logged in, redirecting to login")
        return redirect(url_for("login"))

    image_urls = []
    if "email" in session:
        email = session["email"]
        logger.info(f"[HOME] Fetching image URLs for user: {email}")
        try:
            user_doc_ref = db.collection("users").where("email", "==", email).get()
            if user_doc_ref:
                user_doc_id = user_doc_ref[0].id
                user_data = user_ref.document(user_doc_id).get().to_dict()
                if "image_urls" in user_data:
                    image_urls = user_data["image_urls"]
                    logger.info(f"✓ [HOME] Found {len(image_urls)} image(s) for user")
            else:
                logger.warning(f"[HOME] No user document found for email: {email}")
        except Exception as e:
            logger.error(f"✗ [HOME] Error fetching user images: {str(e)}", exc_info=True)
    
    if request.method == "POST":
        submit_button = request.form["submit_button"]
        logger.info(f"[HOME] Form submitted with action: {submit_button}")

        if submit_button == "upload_image":
            logger.info("[HOME] Image upload initiated")
            if "file" not in request.files:
                logger.warning("[HOME] No file part in request")
                return redirect(request.url)

            file = request.files["file"]

            if file.filename == "":
                logger.warning("[HOME] No file selected")
                return redirect(request.url)

            if file and allowed_file(file.filename):
                INPUT_FILENAME = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], INPUT_FILENAME)
                logger.info(f"[HOME] Saving file: {INPUT_FILENAME} to {filepath}")
                file.save(filepath)
                logger.info(f"✓ [HOME] File saved successfully")
                
                logger.info(f"[HOME] Creating backup copy of image")
                dupe_image(filepath, "copy")
                logger.info(f"✓ [HOME] Backup copy created")
                
                logger.info(f"[HOME] Refreshing image parameters")
                refresh_parameters(filepath)
                logger.info(f"✓ [HOME] Image parameters loaded")

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
    logger.info("[AUTH] Login route accessed")
    if "email" in session:
        logger.info(f"[AUTH] User already logged in, redirecting to home")
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        logger.info(f"[AUTH] Login attempt for email: {email}")
        try:
            logger.info(f"[AUTH] Calling Firebase authentication API...")
            result = login_with_email_password(email, password)
            
            if result["success"]:
                user_id = result["localId"]
                logger.info(f"✓ [AUTH] Authentication successful. User ID: {user_id}")
                
                logger.info(f"[AUTH] Fetching user document from Firestore...")
                doc_ref = db.collection("users").document(user_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    user_data = doc.to_dict()
                    name = user_data.get("name")
                    logger.info(f"✓ [AUTH] User document found. Name: {name}")
                    
                    session["email"] = email
                    session["name"] = name
                    logger.info(f"✓ [AUTH] Session created for user: {email}")
                    return redirect(url_for("home"))
                else:
                    logger.warning(f"[AUTH] User document not found in Firestore for ID: {user_id}")
                    return "User data not found. Please sign up first."
            else:
                logger.warning(f"[AUTH] Authentication failed: {result['error']}")
                return f"Login failed: {result['error']}"
        except Exception as e:
            logger.error(f"✗ [AUTH] Login error: {str(e)}", exc_info=True)
            return f"Failed to login: {str(e)}"
    return render_template("index.html")


@app.route("/signup", methods=["POST"])
def signup():
    logger.info("[AUTH] Signup route accessed")
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    logger.info(f"[AUTH] Signup attempt for email: {email}, name: {name}")
    try:
        logger.info(f"[AUTH] Calling Firebase authentication API for signup...")
        result = signup_with_email_password(email, password)
        
        if result["success"]:
            user_id = result["localId"]
            logger.info(f"✓ [AUTH] User created successfully. User ID: {user_id}")
            
            logger.info(f"[AUTH] Creating user document in Firestore...")
            user_ref1 = user_ref.document(user_id)
            user_ref1.set({"email": email, "name": name})
            logger.info(f"✓ [AUTH] User document created in Firestore")
            
            session["email"] = email
            session["name"] = name
            logger.info(f"✓ [AUTH] Session created for user: {email}")
            return redirect("/")
        else:
            error_message = result["error"]
            logger.warning(f"[AUTH] Signup failed: {error_message}")
            return render_template("index.html", error=error_message)
    except Exception as e:
        error_message = str(e)
        logger.error(f"✗ [AUTH] Signup error: {error_message}", exc_info=True)
        return render_template("index.html", error=error_message)


@app.route("/logout")
def logout():
    logger.info(f"[AUTH] Logout route accessed")
    if "email" in session:
        email = session["email"]
        session.pop("email", None)
        session.pop("name", None)
        logger.info(f"✓ [AUTH] User logged out: {email}")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
