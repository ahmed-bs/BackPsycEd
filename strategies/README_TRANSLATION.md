# Strategies Translation Functionality

This document explains how the automatic translation functionality works in the strategies app.

## Overview

The strategies app now supports automatic translation between French and Arabic for the `title` and `description` fields. The translation system ensures that:

- The main `title` and `description` fields always contain French text
- The `title_ar` and `description_ar` fields always contain Arabic text
- Translation happens automatically when creating or updating strategies

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

#### Creating a Strategy

```json
POST /api/strategies/
{
    "profile": 1,
    "title": "Behavioral Intervention Strategy",
    "title_ar": "",
    "description": "This strategy focuses on improving student behavior through positive reinforcement techniques.",
    "description_ar": "",
    "status": "Active",
    "responsible": "Dr. Smith"
}
```

Result: The system will automatically translate the title and description to Arabic and store them in `title_ar` and `description_ar`.

#### Creating a Strategy with Arabic Content

```json
POST /api/strategies/
{
    "profile": 1,
    "title": "",
    "title_ar": "استراتيجية التدخل السلوكي",
    "description": "",
    "description_ar": "تركز هذه الاستراتيجية على تحسين سلوك الطالب من خلال تقنيات التعزيز الإيجابي.",
    "status": "Active",
    "responsible": "د. سميث"
}
```

Result: The system will automatically translate the Arabic title and description to French and store them in the main fields.

#### Updating a Strategy

```json
PUT /api/strategies/1/
{
    "title": "Updated Behavioral Strategy",
    "description": "Enhanced intervention approach with new techniques."
}
```

Result: The system will automatically translate the updated title and description to Arabic and update the `_ar` fields.

## Fallback Translation

If the Google Translate service is unavailable, the system uses a predefined dictionary of common terms for basic translation, including:

- Strategy-related terms (strategy, plan, goal, objective, etc.)
- Education terms (learning, teaching, student, progress, etc.)
- Health terms (behavior, therapy, intervention, etc.)
- Status terms (active, completed, ongoing, etc.)
- Responsibility terms (responsible, supervisor, coordinator, etc.)

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

1. **Create Operations**: When creating a strategy, both title and description are automatically translated
2. **Update Operations**: When updating a strategy, only the fields being updated are translated
3. **Partial Updates**: If only title or only description is updated, only that field is translated
4. **Preservation**: If both main and Arabic fields have content, no translation occurs to preserve user input
