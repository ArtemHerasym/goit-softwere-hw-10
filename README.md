# Django Quotes App

A Django web application inspired by quotes.toscrape.com.

## Features

- User registration, login, and logout
- Public quote list
- Public author detail pages
- Add authors only for logged-in users
- Add quotes only for logged-in users
- Search quotes by tags
- Top Ten Tags block
- Pagination
- MongoDB to PostgreSQL data import
- Optional scraping from quotes.toscrape.com

## Technologies

- Python
- Django
- PostgreSQL
- MongoDB
- BeautifulSoup
- Poetry

## Setup

Install dependencies:

```bash
poetry install
```

Create `.env` in the same folder as `manage.py`:

```env
POSTGRES_DB=quotes_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=567234
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

MONGO_URI=your_mongodb_connection_string
MONGO_DB=module_8_db
```

Start PostgreSQL with Docker:

```bash
docker start quotes-postgres
```

Run migrations:

```bash
python manage.py migrate
```

Import data from MongoDB:

```bash
python manage.py import_quotes
```

Create admin user:

```bash
python manage.py createsuperuser
```

Run server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Notes

The `.env` file and database files should not be pushed to GitHub.
