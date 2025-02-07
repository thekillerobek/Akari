from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, default='У меня нету био потому что мне лень писать о себе')
    join_date = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, default='avatars/default.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'
    
class Genres(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name



# Tiplar modeli
class Typr(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Datte(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Tags(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Manga modeli:
class Manga(models.Model):
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)
    cover = models.ImageField(upload_to='manga_cover/')
    genres = models.ManyToManyField(Genres, related_name='genres')
    tags = models.ManyToManyField(Tags, related_name='tags')
    typr = models.ForeignKey(Typr, on_delete=models.CASCADE)
    datte = models.ForeignKey(Datte, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="liked_manga", blank=True)
    bookmarks = models.ManyToManyField(User, related_name="bookmarked_manga", blank=True)
    uploader = models.CharField(max_length=255)
    bookmark_count = models.IntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[('Ожидание', 'Ожидание'), ('Продолжается', 'Продолжается'), ('Закончен', 'Закончен')])

    def total_likes(self):
        return self.likes.count()

    def total_bookmarks(self):
        return self.bookmarks.count()
    
    
    def __str__(self):
        return self.title


# Reyting modeli:
class MangaRating(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(1, 'Не советую'), (2, 'Ну такое'), (3, 'Нормально'), (4, 'Хорошо'), (5, 'Очень хорошо')])



class Chapter(models.Model):
    title = models.CharField(max_length=255)
    manga = models.ForeignKey(Manga, related_name="chapters", on_delete=models.CASCADE)
    number = models.IntegerField()  # Номер главы
    release_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.manga.title} - Глава {self.number}"
    

class Image(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='chapter_image/')

    def __str__(self):
        return f"{self.chapter.manga.title} - глава {self.chapter.number}"

    
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Исправлено
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='bookmarked_by')
    last_chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)
    last_page = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'manga')  # Исправлено

    def __str__(self):
        return f"{self.user.username} bookmarked {self.manga.title}"




# Kommentariylar
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manga = models.ForeignKey('Manga', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.chapter}"



# Foydalanuvchi oqigan tarixi
class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='read_by')
    last_read_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} read {self.manga.title}"
    
