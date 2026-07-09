from .models import Quote, Author, Tag
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import AuthorForm, QuoteForm
from django.db.models import Count
from django.core.paginator import Paginator
from django.contrib import messages
from .services.scraper import scrape_quotes

def index(request):
    quotes_list = Quote.objects.all()
    paginator = Paginator(quotes_list, 10)

    page_number = request.GET.get("page")
    quotes = paginator.get_page(page_number)

    top_tags = Tag.objects.annotate(num_quotes=Count("quote")).order_by("-num_quotes")[:10]

    return render(request, "quotes/index.html", {
        "quotes": quotes,
        "top_tags": top_tags,
    })

def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return render(request, "quotes/author_detail.html", {"author": author})

def quotes_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    quotes = Quote.objects.filter(tags=tag)
    return render(request, "quotes/tag_quotes.html", {
        "tag": tag,
        "quotes": quotes,
    })

@login_required
def add_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:index")
    else:
        form = AuthorForm()

    return render(request, "quotes/add_author.html", {"form": form})

@login_required
def add_quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:index")
    else:
        form = QuoteForm()

    return render(request, "quotes/add_quote.html", {"form": form})

@login_required
def scrape_data(request):
    created_quotes = scrape_quotes()
    messages.success(request, f"Scraping finished. New quotes added: {created_quotes}")
    return redirect("quotes:index")