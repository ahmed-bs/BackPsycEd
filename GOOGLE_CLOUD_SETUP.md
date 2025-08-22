# Google Cloud Translation API Setup

This project now includes automatic translation functionality using Google Cloud Translation API. Follow these steps to set it up:

## 1. Install Dependencies

The required dependency has been added to `requirements.txt`. Install it by running:

```bash
pip install -r requirements.txt
```

## 2. Set Up Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Cloud Translation API:
   - Go to "APIs & Services" > "Library"
   - Search for "Cloud Translation API"
   - Click on it and press "Enable"

## 3. Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details
4. Click "Create and Continue"
5. For the role, select "Cloud Translation API User"
6. Click "Done"

## 4. Download Service Account Key

1. Click on the created service account
2. Go to the "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" format
5. Download the key file and save it securely

## 5. Configure Environment

### Option 1: Environment Variable (Recommended)

Set the environment variable to point to your service account key file:

```bash
# Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-key.json"

# Windows (Command Prompt)
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\service-account-key.json

# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

### Option 2: Direct Configuration

You can also set the credentials directly in your Django settings by uncommenting and modifying the line in `backend/settings.py`:

```python
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/service-account-key.json'
```

## 6. Test the Setup

The translation service will automatically ensure:
- **`name` and `description` fields always contain French text**
- **`name_ar` and `description_ar` fields always contain Arabic text**

### Translation Behavior:

**Case 1: When only `name`/`description` are provided:**
- If the text is Arabic → translate to French for main field, keep Arabic in `_ar` field
- If the text is French/English → keep original in main field, translate to Arabic for `_ar` field

**Case 2: When only `name_ar`/`description_ar` are provided:**
- If the text is Arabic → translate to French for main field, keep Arabic in `_ar` field
- If the text is not Arabic → show warning (unexpected case)

**Case 3: When both fields are provided:**
- Skip translation (user has provided both versions)

## 7. Usage

The translation is automatically applied when:
- Creating a new ProfileDomain (POST request)
- Updating an existing ProfileDomain (PUT/PATCH request)

**Field Behavior:**
- `name` and `description` fields will always contain French text
- `name_ar` and `description_ar` fields will always contain Arabic text

## 8. Error Handling

If the Google Cloud Translation API is not properly configured, the system will continue to work without translation functionality. You'll see warning messages in the console.

## Security Notes

- Never commit your service account key file to version control
- Keep your service account key secure and restrict access
- Consider using environment variables for production deployments
- Monitor your Google Cloud API usage to avoid unexpected charges 