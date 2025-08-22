# Goals Translation Functionality

This document explains how the automatic translation functionality works in the goals app.

## Overview

The goals app now supports automatic translation between French and Arabic for the `title` and `description` fields. The translation system ensures that:

- The main `title` and `description` fields always contain French text
- The `title_ar` and `description_ar` fields always contain Arabic text
- Translation happens automatically when creating or updating goals

## How It Works

### Translation Service

The translation functionality is implemented in `translation_utils.py` using the `googletrans` library with fallback translations.

### Translation Logic

The system handles four scenarios:

1. **Only main field has content**: If you provide content in the main field, it will be translated to Arabic and stored in the corresponding `_ar` field
2. **Only Arabic field has content**: If you provide content in the `_ar` field, it will be translated to French and stored in the main field
3. **Both fields have content**: No translation occurs (both values are preserved)
4. **Neither field has content**: No translation occurs

### API Usage

#### Creating a Goal

```json
POST /api/goals/
{
    "profile_id": 1,
    "domain_id": 2,
    "title": "Improve reading comprehension skills",
    "title_ar": "",
    "description": "The student will demonstrate improved reading comprehension by answering questions about grade-level texts with 80% accuracy.",
    "description_ar": "",
    "target_date": "2024-06-30",
    "priority": "high"
}
```

Result: The system will automatically translate the title and description to Arabic and store them in `title_ar` and `description_ar`.

#### Creating a Goal with Arabic Content

```json
POST /api/goals/
{
    "profile_id": 1,
    "domain_id": 2,
    "title": "",
    "title_ar": "تحسين مهارات فهم القراءة",
    "description": "",
    "description_ar": "سيظهر الطالب تحسناً في فهم القراءة من خلال الإجابة على أسئلة حول نصوص مستوى الصف بدقة 80%.",
    "target_date": "2024-06-30",
    "priority": "high"
}
```

Result: The system will automatically translate the Arabic title and description to French and store them in the main fields.

#### Updating a Goal

```json
PUT /api/goals/1/
{
    "title": "Enhanced reading comprehension strategy",
    "description": "Updated approach to improve reading skills through interactive exercises."
}
```

Result: The system will automatically translate the updated title and description to Arabic and update the `_ar` fields.

#### Partial Updates

```json
PATCH /api/goals/1/
{
    "title": "Modified goal title"
}
```

Result: Only the title will be translated, the description remains unchanged.

## Sub-Objectives

Sub-objectives currently do not have Arabic translation fields, but this functionality can be extended if needed in the future.

## Fallback Translation

If the Google Translate service is unavailable, the system uses a predefined dictionary of common terms for basic translation, including:

- Goal-related terms (goal, objective, target, achievement, etc.)
- Priority levels (high, medium, low, urgent, important, etc.)
- Education terms (learning, teaching, student, progress, etc.)
- Health terms (behavior, therapy, intervention, etc.)
- Action terms (improve, increase, develop, achieve, etc.)
- Time terms (date, week, month, year, deadline, etc.)

## Dependencies

- `googletrans==4.0.0rc1` - For automatic translation
- Internet connection - Required for Google Translate API calls

## Error Handling

- If translation fails, the original content is preserved
- The system logs translation attempts and failures for debugging
- Fallback translations ensure basic functionality even without internet access

## Supported Fields

The following fields support automatic translation:

- `title` ↔ `title_ar`
- `description` ↔ `description_ar`

## Translation Behavior

1. **Create Operations**: When creating a goal, both title and description are automatically translated
2. **Update Operations**: When updating a goal, only the fields being updated are translated
3. **Partial Updates**: If only title or only description is updated, only that field is translated
4. **Preservation**: If both main and Arabic fields have content, no translation occurs to preserve user input

## Integration with Other Features

The translation functionality works seamlessly with:

- Domain associations (`domain_id`)
- Profile associations (`profile_id`)
- Sub-objectives creation and management
- Priority settings
- Target date management
- Permission checking for profile access

## Example Workflow

1. **Create Goal**: Submit with French title and description
2. **Auto-Translation**: System detects French and translates to Arabic
3. **Storage**: Both French (main) and Arabic (`_ar`) versions are saved
4. **Retrieval**: API returns both versions for multilingual display
5. **Updates**: When updating, only changed fields are re-translated

## Performance Considerations

- Translation occurs during create/update operations, not during read operations
- Fallback translations provide fast response when online translation is unavailable
- Failed translations don't block goal creation/updates
- Translation results are cached in the database for future use
