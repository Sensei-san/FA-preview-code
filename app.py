from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from pathlib import Path
import base64
import io
from PIL import Image
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'photos'
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

# Ensure uploads folder exists
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# Google Drive service
drive_service = None


def authenticate_google_drive():
    """Authenticate with Google Drive API"""
    global drive_service
    creds = None
    
    # Token.json stores the user's access and refresh tokens
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                return False, "Please upload credentials.json first"
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    drive_service = build('drive', 'v3', credentials=creds)
    return True, "Connected to Google Drive"


def create_or_get_folder(folder_name, parent_id=None):
    """Create a folder in Google Drive or get existing one"""
    try:
        # Check if folder exists
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        
        files = results.get('files', [])
        if files:
            return files[0]['id']
        
        # Create new folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = drive_service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        return folder.get('id')
    except Exception as e:
        print(f"Error creating/getting folder: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload-photo', methods=['POST'])
def upload_photo():
    """Handle photo upload"""
    try:
        data = request.json
        employee_name = data.get('employee_name', 'Unknown')
        employee_id = data.get('employee_id', 'Unknown')
        photo_data = data.get('photo')
        pose = data.get('pose', 'unknown')
        
        if not photo_data:
            return jsonify({'error': 'No photo data'}), 400
        
        # Decode base64 photo
        photo_bytes = base64.b64decode(photo_data.split(',')[1])
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Create employee folder with name_id format
        folder_name = f"{employee_name}_{employee_id}"
        employee_folder = Path(UPLOAD_FOLDER) / folder_name
        employee_folder.mkdir(parents=True, exist_ok=True)
        
        # Save photo with pose name
        photo_path = employee_folder / f"{pose}.jpg"
        image.save(str(photo_path), 'JPEG')
        
        return jsonify({
            'success': True,
            'message': f'Photo saved for {employee_name}',
            'path': str(photo_path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-to-gdrive', methods=['POST'])
def upload_to_gdrive():
    """Upload all photos to Google Drive"""
    try:
        if not drive_service:
            return jsonify({'error': 'Not connected to Google Drive. Authenticate first.'}), 401
        
        data = request.json
        upload_folder_name = data.get('folder_name', 'Employee Photos')
        
        # Create main folder in Google Drive
        main_folder_id = create_or_get_folder(upload_folder_name)
        if not main_folder_id:
            return jsonify({'error': 'Failed to create folder in Google Drive'}), 500
        
        # Upload all employee folders
        uploaded_count = 0
        for employee_folder in Path(UPLOAD_FOLDER).iterdir():
            if not employee_folder.is_dir():
                continue
            
            # Create employee subfolder
            employee_folder_id = create_or_get_folder(
                employee_folder.name, 
                main_folder_id
            )
            
            # Upload all photos
            for photo_file in employee_folder.glob('*.jpg'):
                file_metadata = {
                    'name': photo_file.name,
                    'parents': [employee_folder_id]
                }
                
                media = MediaFileUpload(str(photo_file), mimetype='image/jpeg')
                drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                uploaded_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Uploaded {uploaded_count} photos to Google Drive',
            'folder_id': main_folder_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/authenticate-gdrive', methods=['POST'])
def authenticate():
    """Authenticate with Google Drive"""
    try:
        success, message = authenticate_google_drive()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get list of employees with photo counts"""
    try:
        employees = []
        if Path(UPLOAD_FOLDER).exists():
            for folder in Path(UPLOAD_FOLDER).iterdir():
                if folder.is_dir():
                    photo_count = len(list(folder.glob('*.jpg')))
                    employees.append({
                        'name': folder.name,
                        'photo_count': photo_count
                    })
        return jsonify({'employees': employees})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-session', methods=['POST'])
def upload_session():
    """Upload a complete session (all 6 photos) to Google Drive"""
    try:
        if not drive_service:
            return jsonify({'error': 'Not connected to Google Drive. Authenticate first.'}), 401
        
        data = request.json
        employee_name = data.get('employee_name', 'Unknown')
        employee_id = data.get('employee_id', 'Unknown')
        folder_name = f"{employee_name}_{employee_id}"
        
        # Create main folder in Google Drive
        main_folder_id = create_or_get_folder('Employee Photos')
        if not main_folder_id:
            return jsonify({'error': 'Failed to create folder in Google Drive'}), 500
        
        # Create employee subfolder with name_id
        employee_folder_id = create_or_get_folder(folder_name, main_folder_id)
        
        # Upload all photos
        local_folder = Path(UPLOAD_FOLDER) / folder_name
        if not local_folder.exists():
            return jsonify({'error': 'No photos found for this employee'}), 404
        
        uploaded_count = 0
        for photo_file in sorted(local_folder.glob('*.jpg')):
            file_metadata = {
                'name': photo_file.name,
                'parents': [employee_folder_id]
            }
            
            media = MediaFileUpload(str(photo_file), mimetype='image/jpeg')
            drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            uploaded_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Uploaded {uploaded_count} photos to Google Drive',
            'folder_id': employee_folder_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
