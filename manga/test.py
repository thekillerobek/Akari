from .models import Manga 

manga = Manga.objects.first()  # Получаем первую мангу
print(manga.genres.all())  # Вывод всех жанров
print(manga.tags.all())  # Вывод всех тегов
