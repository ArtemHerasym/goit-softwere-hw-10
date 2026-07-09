from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from quotes.models import Quote
from quotes.utils import has_curly_quote_wrapping, normalize_quote_text


def quote_priority(quote):
    return (1 if has_curly_quote_wrapping(quote.text) else 0, -quote.id)


def console_safe(text):
    return text.encode("ascii", "backslashreplace").decode("ascii")


class Command(BaseCommand):
    help = "Deduplicate quotes that only differ by wrapping quote characters."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the changes. Without this flag the command runs in dry-run mode.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        grouped_quotes = defaultdict(list)

        for quote in Quote.objects.select_related("author").prefetch_related("tags").order_by("id"):
            grouped_quotes[normalize_quote_text(quote.text)].append(quote)

        duplicate_groups = [quotes for quotes in grouped_quotes.values() if len(quotes) > 1]
        self.stdout.write(f"Found {len(duplicate_groups)} duplicate text groups.")

        if not duplicate_groups:
            return

        deleted_ids = []
        normalized_ids = []

        for quotes in duplicate_groups:
            canonical = max(quotes, key=quote_priority)
            duplicates = [quote for quote in quotes if quote.pk != canonical.pk]
            normalized_text = normalize_quote_text(canonical.text)

            duplicate_summary = ", ".join(
                f"id={quote.id}, tags={list(quote.tags.values_list('name', flat=True))}"
                for quote in duplicates
            )
            self.stdout.write(
                f"Keep id={canonical.id} text={console_safe(normalized_text)!r}; delete [{duplicate_summary}]"
            )

            if not apply_changes:
                continue

            with transaction.atomic():
                Quote.objects.filter(pk__in=[quote.pk for quote in duplicates]).delete()
                deleted_ids.extend(quote.pk for quote in duplicates)

                if canonical.text != normalized_text:
                    canonical.text = normalized_text
                    canonical.save(update_fields=["text"])
                    normalized_ids.append(canonical.pk)

        if apply_changes:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Applied dedupe. Deleted {len(deleted_ids)} duplicate rows and normalized {len(normalized_ids)} quote texts."
                )
            )
        else:
            self.stdout.write(self.style.WARNING("Dry run only. Re-run with --apply to modify the database."))
