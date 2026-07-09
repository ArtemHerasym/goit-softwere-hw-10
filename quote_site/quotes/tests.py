from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from quotes.models import Author, Quote, Tag


class QuoteSiteTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            fullname="Albert Einstein",
            born_date="March 14, 1879",
            born_location="Ulm, Germany",
            description="Physicist.",
        )
        self.life_tag = Tag.objects.create(name="life")
        self.simile_tag = Tag.objects.create(name="simile")
        self.quote = Quote.objects.create(
            text="Life is like riding a bicycle. To keep your balance, you must keep moving.",
            author=self.author,
        )
        self.quote.tags.add(self.life_tag, self.simile_tag)
        self.user = User.objects.create_user(username="tester", password="secret-pass-123")

    def test_homepage_loads_and_shows_quote_data(self):
        response = self.client.get(reverse("quotes:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Latest quotes")
        self.assertContains(response, self.quote.text)
        self.assertContains(response, self.author.fullname)
        self.assertContains(response, self.life_tag.name)

    def test_homepage_pagination_works(self):
        for index in range(2, 13):
            quote = Quote.objects.create(text=f"Quote number {index}", author=self.author)
            quote.tags.add(self.life_tag)

        response = self.client.get(reverse("quotes:index"), {"page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["quotes"].number, 2)
        self.assertContains(response, "Page 2 of 2")

    def test_author_detail_page_loads(self):
        response = self.client.get(reverse("quotes:author_detail", args=[self.author.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.author.fullname)

    def test_tag_page_loads_and_keeps_author_link(self):
        response = self.client.get(reverse("quotes:quotes_by_tag", args=[self.life_tag.name]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.quote.text)
        self.assertContains(response, self.author.fullname)

    def test_register_creates_user(self):
        response = self.client.post(
            reverse("users:signup"),
            {
                "username": "new-user",
                "password1": "strong-pass-123",
                "password2": "strong-pass-123",
            },
        )

        self.assertRedirects(response, reverse("quotes:index"))
        self.assertTrue(User.objects.filter(username="new-user").exists())

    def test_login_shows_errors_for_invalid_credentials(self):
        response = self.client.post(
            reverse("users:login"),
            {
                "username": self.user.username,
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")

    def test_login_and_logout_work(self):
        login_response = self.client.post(
            reverse("users:login"),
            {
                "username": self.user.username,
                "password": "secret-pass-123",
            },
        )
        logout_response = self.client.get(reverse("users:logout"))

        self.assertRedirects(login_response, reverse("quotes:index"))
        self.assertRedirects(logout_response, reverse("quotes:index"))

    def test_add_author_requires_login(self):
        response = self.client.get(reverse("quotes:add_author"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_add_author_works_for_logged_in_user(self):
        self.client.login(username="tester", password="secret-pass-123")

        response = self.client.post(
            reverse("quotes:add_author"),
            {
                "fullname": "Jane Austen",
                "born_date": "December 16, 1775",
                "born_location": "Steventon, Hampshire, England",
                "description": "Novelist.",
            },
        )

        self.assertRedirects(response, reverse("quotes:index"))
        self.assertTrue(Author.objects.filter(fullname="Jane Austen").exists())

    def test_add_quote_normalizes_text_and_saves(self):
        self.client.login(username="tester", password="secret-pass-123")
        wisdom = Tag.objects.create(name="wisdom")

        response = self.client.post(
            reverse("quotes:add_quote"),
            {
                "text": "“Keep moving.”",
                "author": self.author.id,
                "tags": [wisdom.id],
            },
        )

        self.assertRedirects(response, reverse("quotes:index"))
        self.assertTrue(Quote.objects.filter(text="Keep moving.").exists())

    def test_scrape_view_keeps_login_protection_and_redirects(self):
        protected_response = self.client.get(reverse("quotes:scrape_data"))
        self.client.login(username="tester", password="secret-pass-123")

        with patch("quotes.views.scrape_quotes", return_value=3):
            success_response = self.client.get(reverse("quotes:scrape_data"), follow=True)

        self.assertEqual(protected_response.status_code, 302)
        self.assertIn(reverse("users:login"), protected_response.url)
        self.assertEqual(success_response.status_code, 200)
        self.assertContains(success_response, "Scraping finished. New quotes added: 3")

    def test_dedupe_quotes_command_keeps_canonical_tags(self):
        science = Tag.objects.create(name="science")
        plain_quote = Quote.objects.create(text="Same quote.", author=self.author)
        plain_quote.tags.add(self.life_tag, self.simile_tag, science)

        quoted_quote = Quote.objects.create(text="“Same quote.”", author=self.author)
        quoted_quote.tags.add(self.life_tag, self.simile_tag)

        call_command("dedupe_quotes", "--apply", stdout=StringIO())

        remaining = Quote.objects.filter(text="Same quote.")

        self.assertEqual(remaining.count(), 1)
        self.assertEqual(
            set(remaining.get().tags.values_list("name", flat=True)),
            {"life", "simile"},
        )
