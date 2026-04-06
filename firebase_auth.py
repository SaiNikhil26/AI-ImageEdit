"""
Firebase Authentication Helper
Uses REST API for user authentication since firebase-admin doesn't support signup/login directly
"""
import requests
import json
import logging

logger = logging.getLogger(__name__)

# Firebase REST API endpoints
FIREBASE_REST_API_URL = "https://www.googleapis.com/identitytoolkit/v3/relyingparty"
FIREBASE_API_KEY = "AIzaSyCBoz2YzBThJVC1neWrH7UXfVOmGF5HjGk"


def signup_with_email_password(email, password):
    """
    Create a new user with email and password
    """
    logger.info(f"[FIREBASE_AUTH] Signup API call for email: {email}")
    try:
        url = f"{FIREBASE_REST_API_URL}/signupNewUser?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        logger.debug(f"[FIREBASE_AUTH] Sending signup request to: {url}")
        response = requests.post(url, json=payload, timeout=10)
        
        logger.debug(f"[FIREBASE_AUTH] Response status code: {response.status_code}")
        logger.debug(f"[FIREBASE_AUTH] Response text: {response.text[:200]}")
        
        # Check if response has content
        if not response.text:
            logger.error(f"✗ [FIREBASE_AUTH] Empty response from Firebase API")
            return {
                "success": False,
                "error": "Empty response from Firebase API"
            }
        
        # Try to parse JSON
        try:
            result = response.json()
        except json.JSONDecodeError as je:
            logger.error(f"✗ [FIREBASE_AUTH] Failed to parse JSON response: {str(je)}")
            logger.error(f"[FIREBASE_AUTH] Response content: {response.text[:500]}")
            return {
                "success": False,
                "error": f"Invalid response from Firebase: {response.text[:200]}"
            }
        
        if response.status_code == 200:
            logger.info(f"✓ [FIREBASE_AUTH] Signup successful for email: {email}")
            return {
                "success": True,
                "localId": result.get("localId"),
                "email": result.get("email"),
                "idToken": result.get("idToken")
            }
        else:
            error = result.get("error", {}).get("message", "Unknown error")
            logger.error(f"✗ [FIREBASE_AUTH] Signup failed (status {response.status_code}): {error}")
            return {
                "success": False,
                "error": error
            }
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ [FIREBASE_AUTH] Network/request exception: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"✗ [FIREBASE_AUTH] Signup exception: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def login_with_email_password(email, password):
    """
    Login user with email and password
    """
    logger.info(f"[FIREBASE_AUTH] Login API call for email: {email}")
    try:
        url = f"{FIREBASE_REST_API_URL}/verifyPassword?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        logger.debug(f"[FIREBASE_AUTH] Sending login request to: {url}")
        response = requests.post(url, json=payload, timeout=10)
        
        logger.debug(f"[FIREBASE_AUTH] Response status code: {response.status_code}")
        logger.debug(f"[FIREBASE_AUTH] Response text: {response.text[:200]}")
        
        # Check if response has content
        if not response.text:
            logger.error(f"✗ [FIREBASE_AUTH] Empty response from Firebase API")
            return {
                "success": False,
                "error": "Empty response from Firebase API"
            }
        
        # Try to parse JSON
        try:
            result = response.json()
        except json.JSONDecodeError as je:
            logger.error(f"✗ [FIREBASE_AUTH] Failed to parse JSON response: {str(je)}")
            logger.error(f"[FIREBASE_AUTH] Response content: {response.text[:500]}")
            return {
                "success": False,
                "error": f"Invalid response from Firebase: {response.text[:200]}"
            }
        
        if response.status_code == 200:
            logger.info(f"✓ [FIREBASE_AUTH] Login successful for email: {email}")
            return {
                "success": True,
                "localId": result.get("localId"),
                "email": result.get("email"),
                "idToken": result.get("idToken")
            }
        else:
            error = result.get("error", {}).get("message", "Unknown error")
            logger.error(f"✗ [FIREBASE_AUTH] Login failed (status {response.status_code}): {error}")
            return {
                "success": False,
                "error": error
            }
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ [FIREBASE_AUTH] Network/request exception: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"✗ [FIREBASE_AUTH] Login exception: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
