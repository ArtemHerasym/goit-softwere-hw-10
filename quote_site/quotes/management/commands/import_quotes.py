import os
from dotenv import load_dotenv
from pymongo import MongoClient
from django.core.management.base import BaseCommand

from quotes.models import Author, Tag, Quote


class Command(BaseCommand):
    help = "Import authors and quotes from MongoDB"

    def handle(self, *args, **kwargs):
        load_dotenv()

        client = MongoClient(os.getenv("MONGO_URI"))
        db = client[os.getenv("MONGO_DB")]

        authors_collection = db["authors"]
        quotes_collection = db["quotes"]

        authors_map = {}

        for author_data in authors_collection.find():
            author, _ = Author.objects.get_or_create(
                fullname=author_data.get("fullname"),
                defaults={
                    "born_date": author_data.get("born_date", ""),
                    "born_location": author_data.get("born_location", ""),
                    "description": author_data.get("description", ""),
                }
            )

            authors_map[author_data["_id"]] = author
            authors_map[author.fullname] = author

        imported_quotes = 0

        for quote_data in quotes_collection.find():
            author_ref = quote_data.get("author")

            if hasattr(author_ref, "id"):  # DBRef case
                author_ref = author_ref.id

            author = authors_map.get(author_ref)

            if not author:
                self.stdout.write(f"Skipped quote, author not found: {author_ref}")
                continue

            quote_text = quote_data.get("quote") or quote_data.get("text")

            if not quote_text:
                continue

            quote, _ = Quote.objects.get_or_create(
                text=quote_text,
                defaults={"author": author}
            )

            for tag_name in quote_data.get("tags", []):
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                quote.tags.add(tag)

            imported_quotes += 1

        self.stdout.write(self.style.SUCCESS(f"Imported quotes: {imported_quotes}"))