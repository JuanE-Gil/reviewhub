# Development Guide for ReviewHub

This document provides essential information for advanced developers working on the ReviewHub project.

## Build/Configuration Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL
- Virtual environment (recommended)

### Setup
1. **Environment Variables**: Create a `.env` file in the root directory. Required variables:
   - `SECRET_KEY`: Django secret key.
   - Database configuration (if not using defaults in `local.py`).
2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Database Migrations**:
   ```powershell
   python manage.py migrate
   ```
4. **Run Server**:
   ```powershell
   python manage.py runserver
   ```

## Testing Information

### Configuration
Tests use the default Django test runner. A test database will be created automatically.

### Running Tests
To run all tests:
```powershell
python manage.py test
```
To run tests for a specific app:
```powershell
python manage.py test apps.<app_name>
```

### Guidelines for New Tests
- Place tests in the `tests.py` file within each app directory or create a `tests/` package.
- Use `django.test.TestCase` for tests that require a database.
- Follow the Arrange-Act-Assert pattern.

### Working Test Example
The following test demonstrates creating a user, a category, and a review, verifying the automatic slug generation.

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.reviews.models import Category, Review

User = get_user_model()

class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='dev@example.com',
            username='devuser',
            password='password123'
        )
        self.category = Category.objects.create(name='Electronics')

    def test_review_creation_and_slug(self):
        review = Review.objects.create(
            user=self.user,
            category=self.category,
            title='Awesome Gadget',
            content='This gadget is life-changing.',
            score=5,
            status=Review.STATUS_PUBLISHED
        )
        self.assertEqual(review.slug, 'awesome-gadget')
        self.assertEqual(str(review), 'Awesome Gadget - devuser')
```

## Additional Development Information

### Project Structure
- `apps/`: Contains the project's applications (`accounts`, `reviews`, `interactions`).
- `config/settings/`: Multi-environment settings (`base.py`, `local.py`, `production.py`).

### Code Style
- Follow PEP 8 guidelines.
- Use meaningful variable and function names in English.
- Docstrings are encouraged for models and complex logic.

### Known Issues & Findings
- **Slug Generation Bug**: In `apps/reviews/models.py`, the `Review.save()` method incorrectly references `Category.objects.filter(slug=slug)` instead of `Review.objects.filter(slug=slug)` when checking for duplicate slugs. This leads to `IntegrityError` if two reviews have the same title and no category has a matching slug.
- **Custom User Model**: The project uses a custom user model `apps.accounts.User` which uses `email` as the primary identifier instead of `username`.
