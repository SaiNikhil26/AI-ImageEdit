# 🔥 Complete Firebase Setup Guide for AI Image Edit

## Overview
This guide walks you through setting up a brand new Firebase project from scratch for the AI Image Edit application.

---

## 📋 Prerequisites

- ✅ Google Account (create one if needed at https://accounts.google.com)
- ✅ Internet connection
- ✅ Valid credit/debit card (for billing - we'll enable it immediately)
- ✅ This project code downloaded

---

## 🚀 Step-by-Step Setup

### Step 1: Create Firebase Project

1. **Go to Firebase Console:**
   ```
   https://console.firebase.google.com/
   ```

2. **Click "Add Project"**
   - Click the blue "+ Add project" button

3. **Enter Project Name:**
   - Project name: `ai-image-edit` (or any name you prefer)
   - Click "Continue"

4. **Google Analytics (Optional):**
   - You can disable this for now
   - Click "Continue"

5. **Create Project:**
   - Click "Create project"
   - Wait 2-3 minutes for creation (you'll see a progress spinner)

6. **When Ready:**
   - You'll see "Your new project is ready"
   - Click "Continue"

✅ **Your Firebase project is now created!**

---

### Step 2: Enable Firebase Authentication

1. **In Firebase Console, click your project**

2. **Navigate to Authentication:**
   - Left sidebar → "Authentication"
   - Click "Get started"

3. **Enable Email/Password Authentication:**
   - Click on "Email/Password"
   - Toggle "Enable" to ON
   - Make sure "Password-based accounts" is enabled
   - Click "Save"

4. **Verify Email Configuration:**
   - You should see "Email/Password" listed as enabled

✅ **Authentication is ready!**

---

### Step 3: Set Up Firestore Database

1. **Navigate to Firestore:**
   - Left sidebar → "Firestore Database"
   - Click "Create database"

2. **Choose Location:**
   - Select: `us-central1` (or closest to you)
   - Click "Next"

3. **Security Rules:**
   - Select: "Start in test mode"
   - Click "Create"
   - Wait 1-2 minutes for database creation

4. **When Ready:**
   - You'll see the Firestore console
   - Database is now active

✅ **Firestore is ready!**

---

### Step 4: Set Up Cloud Storage

1. **Navigate to Storage:**
   - Left sidebar → "Storage"
   - Click "Get started"

2. **Choose Location:**
   - Select: `us-central1` (same as Firestore)
   - Click "Next"

3. **Security Rules:**
   - Select: "Start in test mode"
   - Click "Done"
   - Wait 1-2 minutes for bucket creation

4. **When Ready:**
   - You'll see the Storage console
   - Storage bucket is now active

✅ **Cloud Storage is ready!**

---

### Step 5: Enable Billing (IMPORTANT!)

**⚠️ This is required for Cloud Storage to work!**

1. **Go to Google Cloud Console:**
   ```
   https://console.cloud.google.com/
   ```

2. **Make Sure Your Project is Selected:**
   - Top-left corner shows your project name
   - Click dropdown if needed to select `ai-image-edit`

3. **Navigate to Billing:**
   - Left sidebar → "Billing"
   - Click "Create Billing Account" if needed

4. **Create Billing Account (if first time):**
   - Account name: Enter any name (e.g., "Personal")
   - Country: Select yours
   - Click "Continue"

5. **Add Payment Method:**
   - Enter your credit/debit card details
   - Billing address: Enter your address
   - Click "Save"

6. **Link to Project:**
   - Go back to Billing page
   - Click "Link Billing Account"
   - Select the billing account you just created
   - Click "Link"

7. **Verify Project is on Blaze Plan:**
   - Go to: https://console.cloud.google.com/billing/projects
   - Find your `ai-image-edit` project
   - Status should show: "Active billing account" ✅

✅ **Billing is enabled!**

---

### Step 6: Create Service Account & Get Credentials

1. **Go to Google Cloud Console:**
   ```
   https://console.cloud.google.com/
   ```

2. **Navigate to Service Accounts:**
   - Left sidebar → "APIs & Services" → "Credentials"
   - Or direct: https://console.cloud.google.com/apis/credentials

3. **Create Service Account:**
   - Click "+ Create Credentials"
   - Select "Service Account"

4. **Fill Service Account Details:**
   - Service account name: `ai-image-edit-admin`
   - Service account ID: auto-filled (e.g., `ai-image-edit-admin@...`)
   - Description: `Admin service account for AI Image Edit`
   - Click "Create and Continue"

5. **Grant Permissions:**
   - Click "Grant this service account access to project"
   - Under "Select a role", choose: "Editor" or "Firebase Service Agent"
   - Click "Continue"

6. **Create Key:**
   - Click "Create Key"
   - Select "JSON"
   - Click "Create"
   - **A JSON file will download automatically!**
   - ⚠️ **Keep this file safe! You need it!**

✅ **Service account created with JSON credentials!**

---

### Step 7: Add Service Account to Firebase

1. **In Firebase Console, go to Project Settings:**
   - Top-left corner, click gear icon ⚙️
   - Select "Project settings"

2. **Navigate to Service Accounts:**
   - Click "Service Accounts" tab

3. **Click "Firebase Admin SDK":**
   - You'll see some code snippets
   - This is just for reference

4. **Verify:**
   - Your service account appears in the list
   - Status shows as available

✅ **Service account linked to Firebase!**

---

### Step 8: Get API Key for Web Apps

1. **In Firebase Console:**
   - Top-left corner, click gear icon ⚙️
   - Select "Project settings"

2. **Navigate to "General" tab:**
   - You'll see your Firebase project configuration

3. **Find "Web API Key":**
   - Look for: `apiKey: "AIzaSy..."`
   - Copy this key
   - You'll need it later

4. **Get Other Values:**
   - `authDomain`: `your-project.firebaseapp.com`
   - `projectId`: `your-project-id`
   - `storageBucket`: `your-project.appspot.com`
   - `messagingSenderId`: (number)
   - `appId`: (long string)

✅ **You have all Firebase credentials!**

---

### Step 9: Configure the Project

1. **Copy the Downloaded JSON File:**
   - The JSON file you downloaded in Step 6
   - Copy it to your project root directory
   - Path: `/Users/saiyeshwanth/Desktop/Nikhil/AI-ImageEdit/`
   - Filename: `service_account.json`

2. **Update `.env` File:**
   ```bash
   cd /Users/saiyeshwanth/Desktop/Nikhil/AI-ImageEdit
   ```

3. **Edit `.env` with Your Firebase Values:**
   ```properties
   # Firebase Configuration
   FIREBASE_API_KEY=YOUR_API_KEY_HERE
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   FIREBASE_APP_ID=your-app-id
   FIREBASE_CREDENTIALS_PATH=service_account.json

   # Flask Configuration
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=AI_IMAGE_EDIT

   # Server Configuration
   HOST=127.0.0.1
   PORT=5000

   # Development Mode
   DEV_MODE=False
   SKIP_STORAGE_UPLOAD=False
   ```

4. **Replace the Values:**
   - `YOUR_API_KEY_HERE` → Web API Key from Step 8
   - `your-project.firebaseapp.com` → Your auth domain
   - `your-project-id` → Your project ID
   - `your-project.appspot.com` → Your storage bucket
   - Others → From Firebase project settings

✅ **Configuration is complete!**

---

## 🔒 Security Rules (Important!)

### For Development (Test Mode - Current)

Your storage and Firestore are in "test mode" which allows:
- ✅ Anyone can read/write
- ✅ Perfect for development
- ✅ NOT for production

### For Production (Later)

When ready to deploy, update Security Rules:

**Firestore Security Rules:**
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}
```

**Storage Security Rules:**
```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /images/{userId}/{allPaths=**} {
      allow read: if request.auth.uid == userId;
      allow write: if request.auth.uid == userId && 
                      resource.size < 50 * 1024 * 1024;
    }
  }
}
```

---

## ✅ Verification Checklist

Before running the app, verify:

- [x] Firebase project created
- [x] Authentication enabled (Email/Password)
- [x] Firestore database created
- [x] Cloud Storage bucket created
- [x] Billing account linked
- [x] Service account created
- [x] JSON credentials downloaded and copied
- [x] `.env` file updated with correct values
- [x] `service_account.json` in project root

---

## 🧪 Test Your Setup

### Install Dependencies
```bash
cd /Users/saiyeshwanth/Desktop/Nikhil/AI-ImageEdit
source .venv/bin/activate
pip install python-dotenv firebase-admin
```

### Test Firebase Connection
```bash
python test_firebase_auth.py
```

Expected output:
```
[FIREBASE_AUTH] Signup API call for email: test@example.com
✓ [FIREBASE_AUTH] Signup successful
✓ [FIREBASE_AUTH] Login successful
```

### Run the Application
```bash
python app.py
```

Expected:
```
==================================================
Starting AI Image Edit Application
==================================================
✓ Firebase credentials loaded successfully
✓ Firebase app initialized successfully
✓ Firestore connection successful
✓ Firebase Storage connection successful
✓ Users collection reference obtained
```

### Test in Browser
1. Open: `http://localhost:5000`
2. Sign up: Create new account
3. Log in: Use credentials
4. Upload: Try image upload
5. Edit: Apply filters
6. Download: Save edited image

✅ **Everything should work!**

---

## 🎯 What Each Firebase Service Does

### Authentication
- User signup/login
- Email verification (optional)
- Password reset (optional)
- Session management

### Firestore
- Store user data (email, name)
- Store user settings
- Query user documents
- Real-time updates

### Cloud Storage
- Store uploaded images
- Generate download URLs
- Set expiration on URLs
- Organize files by user

---

## 🆘 Troubleshooting

### Problem: "Billing account is disabled"

**Solution:**
1. Go to: https://console.cloud.google.com/billing/projects
2. Click on your project
3. Verify "Active billing account" is shown
4. If not, click "Link Billing Account"
5. Wait 5-10 minutes for activation

### Problem: "Service account not found"

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "Service Account"
3. Follow Step 6 again

### Problem: "Invalid credentials"

**Solution:**
1. Check `.env` file has correct values
2. Check `service_account.json` is in project root
3. Compare values with Firebase console

### Problem: "Storage bucket not found"

**Solution:**
1. Go to Firebase Storage
2. Verify bucket is created and in "Started" state
3. Check `.env` has correct bucket name (ends with `.appspot.com`)

### Problem: "Firestore not initialized"

**Solution:**
1. Go to Firebase Firestore
2. Click "Create Database" if not present
3. Wait 1-2 minutes for creation
4. Restart the app

---

## 📊 Firebase Project Structure

After setup, your Firebase project will have:

```
Firebase Project: ai-image-edit
├── Authentication
│   └── Email/Password enabled
├── Firestore Database
│   └── Collections
│       └── users (auto-created when first user signs up)
├── Cloud Storage
│   └── Bucket: ai-image-edit.appspot.com
│       └── images/ (auto-created when first upload)
├── Service Accounts
│   └── ai-image-edit-admin (credentials)
└── Settings
    └── API Keys & Credentials
```

---

## 🔐 Security Best Practices

1. **Never commit secrets to git:**
   - Add to `.gitignore`: `service_account.json`
   - Add to `.gitignore`: `.env`

2. **Use environment variables:**
   - Never hardcode credentials
   - Always load from `.env`

3. **Rotate credentials regularly:**
   - Delete old keys
   - Create new service account keys

4. **Use strong passwords:**
   - When creating test accounts
   - For admin accounts

5. **Enable billing alerts:**
   - Set spending limits
   - Monitor monthly charges

---

## 📱 Next Steps After Setup

1. **Test authentication:** Try signup/login
2. **Test storage:** Upload and download files
3. **Check Firestore:** View user documents
4. **Monitor billing:** Check Google Cloud console
5. **Update security rules:** When ready for production

---

## 📞 Firebase Documentation

- **Firebase Console**: https://console.firebase.google.com/
- **Firebase Docs**: https://firebase.google.com/docs
- **Authentication**: https://firebase.google.com/docs/auth
- **Firestore**: https://firebase.google.com/docs/firestore
- **Storage**: https://firebase.google.com/docs/storage
- **Admin SDK**: https://firebase.google.com/docs/admin/setup

---

## ✨ You're All Set!

After following these steps:
- ✅ Firebase project created
- ✅ All services enabled
- ✅ Billing configured
- ✅ Credentials obtained
- ✅ Project configured
- ✅ Ready to run

**Next:** Run `python app.py` and start building!

---

**Created:** April 6, 2026
**Status:** Complete Firebase setup guide
**Time to complete:** ~15-20 minutes
**Cost:** Free (with billing enabled, only pay for usage)
