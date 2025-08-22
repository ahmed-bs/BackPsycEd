# Notes Translation Functionality

This document explains how the automatic translation functionality works in the notes app.

## Overview

The notes app now supports automatic translation between French and Arabic for the `content` field. The translation system ensures that:

- The main `content` field always contains French text
- The `content_ar` field always contains Arabic text
- Translation happens automatically when creating or updating notes

## How It Works

### Translation Service

The translation functionality is implemented in `translation_utils.py` using the `googletrans` library with fallback translations.

### Translation Logic

The system handles four scenarios:

1. **Only main field has content**: If you provide content in the main field, it will be translated to Arabic and stored in `content_ar`
2. **Only Arabic field has content**: If you provide content in `content_ar`, it will be translated to French and stored in the main field
3. **Both fields have content**: No translation occurs (both values are preserved)
4. **Neither field has content**: No translation occurs

### API Usage

#### Creating a Note

```json
POST /api/notes/
{
    "profile_id": 1,
    "content": "This is an important note about student progress",
    "content_ar": ""
}
```

Result: The system will automatically translate the content to Arabic and store it in `content_ar`.

#### Creating a Note with Arabic Content

```json
POST /api/notes/
{
    "profile_id": 1,
    "content": "",
    "content_ar": "هذه ملاحظة مهمة حول تقدم الطالب"
}
```

Result: The system will automatically translate the Arabic content to French and store it in the main `content` field.

#### Updating a Note

```json
PUT /api/notes/1/
{
    "content": "Updated note content in French"
}
```

Result: The system will automatically translate the updated content to Arabic and update `content_ar`.

## Fallback Translation

If the Google Translate service is unavailable, the system uses a predefined dictionary of common terms for basic translation.

## Dependencies

- `googletrans==4.0.0rc1` - For automatic translation
- Internet connection - Required for Google Translate API calls

## Error Handling

- If translation fails, the original content is preserved
- The system logs translation attempts and failures for debugging
- Fallback translations ensure basic functionality even without internet access
