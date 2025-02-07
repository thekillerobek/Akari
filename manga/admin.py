from django.contrib import admin
from .models import * # замените на имена своих моделей

admin.site.register(Manga)
admin.site.register(Chapter)
admin.site.register(Genres)
admin.site.register(Typr)
admin.site.register(Datte)
admin.site.register(Profile)
admin.site.register(MangaRating)
admin.site.register(Bookmark)
admin.site.register(ReadingHistory)
admin.site.register(Image)
admin.site.register(Tags)
admin.site.register(Comment)
# и т.д.