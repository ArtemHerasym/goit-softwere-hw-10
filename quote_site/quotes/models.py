from django.db import models

class Author(models.Model):
    fullname = models.CharField(max_length=100, unique=True)
    born_date = models.CharField(max_length=100)
    born_location = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.fullname

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Quote(models.Model):
    text = models.TextField(unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    def __str__(self):
        return self.text[:50]
