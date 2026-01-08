# Employee Photo Capture System

A simple web app to capture employee photos and upload them to Google Drive. Perfect for building employee datasets with no coding experience required!

## Features

✅ **Live Camera Capture** - Use your webcam to take photos  
✅ **Organize by Employee** - Photos automatically organized into employee folders  
✅ **Google Drive Upload** - Upload all photos directly to your Google Drive  
✅ **Simple Interface** - Easy to use, no technical knowledge needed  
✅ **View Progress** - See how many photos you've captured per employee  

## Quick Start Guide

### Step 1: Set Up (One Time)

1. Open terminal in VS Code (Ctrl+`)
2. Run these commands:
```bash
pip install -r requirements.txt
python app.py
```

3. Open your browser and go to: `http://localhost:5000`

### Step 2: Connect to Google Drive (Optional but Recommended)

To enable uploading photos to Google Drive:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create OAuth 2.0 Desktop Application credentials
5. Download the credentials as JSON
6. Save it as `credentials.json` in the project folder
7. In the app, click "Connect to Google Drive" and follow the login

### Step 3: Start Capturing Photos

1. Enter the employee's name
2. Click "Capture Photo" button
3. Review the preview and click "Save Photo"
4. The photo is saved locally in the `photos` folder

### Step 4: Upload to Google Drive

1. Click "Upload All to Google Drive"
2. Photos will be organized by employee name automatically

## File Structure

```
project/
├── app.py                 # Main Python app
├── requirements.txt       # Dependencies
├── templates/
│   └── index.html        # Web interface
├── photos/               # Local photo storage (auto-created)
│   └── Employee Name/
│       └── photo_*.jpg
├── credentials.json      # Google Drive credentials (add this)
└── token.json           # Auto-generated after Google auth
```

## Troubleshooting

**App won't start?**
- Make sure you're in the project folder: `cd /workspaces/FA-preview-code`
- Check that Python is installed: `python --version`

**Camera not working?**
- Allow camera access when the browser asks
- Make sure no other app is using your camera
- Try refreshing the page (F5)

**Google Drive upload fails?**
- Make sure `credentials.json` is in the project folder
- Check that Google Drive API is enabled in Google Cloud Console
- Try clicking "Connect to Google Drive" again

**Photos not saving?**
- Check that the `photos` folder exists and is writable
- Make sure you've entered an employee name

## Need Help?

Check the browser console (F12 → Console tab) for error messages. The error messages will tell you what's wrong!

## Tips for Success

1. **Name consistency** - Use the same spelling for employee names for better organization
2. **Lighting** - Good lighting helps with photo quality
3. **Batch uploads** - Capture all photos first, then upload to Google Drive once
4. **Regular backups** - Photos are backed up to Google Drive automatically

---

Happy capturing! 📸