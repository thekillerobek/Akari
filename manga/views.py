from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Avg
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from .models import Profile, Manga, Bookmark, Genres, Typr, Comment, MangaRating, Chapter
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json


# Главная страница
def HomeView(request):
    # Получаем последние 5 манг по дате публикации
    new_manga = Manga.objects.all().order_by('-publication_date')[:5]
    
    # Получаем 10 самых популярных манг по среднему рейтингу
    popular_manga = Manga.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')[:10]
    
    # Получаем закладки пользователя, если он авторизован
    user_bookmarks = Bookmark.objects.filter(user=request.user) if request.user.is_authenticated else []
    
    # Составляем список манг, которые пользователь недавно читал
    continue_reading = [
        {'manga': bookmark.manga, 'last_chapter': bookmark.last_chapter, 'last_page': bookmark.last_page}
        for bookmark in user_bookmarks
    ]
    
    # Получаем профиль пользователя (если авторизован)
    profile = Profile.objects.filter(user=request.user).first()

    context = {
        'new_manga': new_manga,
        'best_rated_manga': popular_manga,
        'continue_reading': continue_reading,
        'profile': profile,
    }

    return render(request, 'home.html', context)


# Страница деталей манги
def manga_detail(request, original_title):
    manga = get_object_or_404(Manga, original_title=original_title)
    profile = Profile.objects.filter(user=request.user).first()

    # Создаем ключ для сессии, уникальный для каждой манги
    session_key = f'manga_viewed_{manga.id}'

    # Проверяем, был ли уже увеличен просмотр для этой манги в этой сессии
    if not request.session.get(session_key, False):
        manga.views += 1  # Увеличиваем количество просмотров манги
        manga.save()
        request.session[session_key] = True  # Устанавливаем флаг в сессии

    avg_rating = manga.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    similar = Manga.objects.filter(typr=manga.typr).exclude(id=manga.id)[:4]
    is_bookmarked = manga.bookmarked_by.filter(user=request.user).exists() if request.user.is_authenticated else False
    similar_with_genre = [
        sim for sim in similar if any(genre in manga.genres.all() for genre in sim.genres.all())
    ]
    comments = manga.comments.all().order_by('-created_at')

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.manga = manga
            comment.user = request.user
            comment.save()
            return redirect('manga_detail', original_title=original_title)
    else:
        form = CommentForm()

    context = {
        'manga': manga,
        'is_bookmarked': is_bookmarked,
        'similar_mangas': similar_with_genre,
        'comments': comments,
        'form': form,
        'profile': profile,
        'avg_rating': round(avg_rating, 1),
    }

    return render(request, 'manga_detail.html', context)


# Добавить/удалить мангу из закладок
def add_Bookmark(request, manga_id):
    manga = get_object_or_404(Manga, id=manga_id)
    user = request.user

    # Проверяем, есть ли манга в закладках
    bookmark = Bookmark.objects.filter(user=user, manga=manga).first()

    if bookmark:
        bookmark.delete()  # Удаляем закладку
        manga.bookmark_count -= 1
    else:
        Bookmark.objects.create(user=user, manga=manga)  # Добавляем в закладки
        manga.bookmark_count += 1
    
    manga.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# Каталог манги с фильтрами
def catalog(request):
    mangas = Manga.objects.all()
    genres = Genres.objects.all()
    typrs = Typr.objects.all()
    
    # Получаем профиль пользователя (если авторизован)
    profile = Profile.objects.filter(user=request.user).first()

    # Извлекаем параметры фильтрации из GET-запроса
    genre_id = request.GET.get('genres')
    typr_id = request.GET.get('typr')
    tags = request.GET.get('tags')
    status = request.GET.get('status')
    translate_status = request.GET.get('translate_status')
    age_rating = request.GET.get('age_rating')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Применяем фильтрацию по жанру
    if typr_id:
        mangas = mangas.filter(typr_id=typr_id)
    
    # Фильтрация по жанру
    if genre_id:
        mangas = mangas.filter(genre__id=genre_id)
    
    # Фильтрация по тегам
    if tags:
        mangas = mangas.filter(tags__icontains=tags)
    
    # Фильтрация по статусу
    if status:
        mangas = mangas.filter(status=status)

    # Фильтрация по статусу перевода
    if translate_status:
        mangas = mangas.filter(translate_status__icontains=translate_status)
    
    # Фильтрация по возрастному рейтингу
    if age_rating:
        mangas = mangas.filter(age_rating=age_rating)
    
    # Фильтрация по датам
    if date_from:
        mangas = mangas.filter(publication_date__year__gte=date_from)
    if date_to:
        mangas = mangas.filter(publication_date__year__lte=date_to)

    return render(request, 'catalog.html', {
        'mangas': mangas,
        'genres': genres,
        'typrs': typrs,
        'profile': profile,
    })


# Просмотр закладок пользователя
@login_required(login_url='login')
def BookmarkView(request):
    user = request.user
    
    # Получаем профиль пользователя (если авторизован)
    profile = Profile.objects.filter(user=request.user).first()
    
    # Получаем все закладки пользователя
    bookmarks = Bookmark.objects.filter(user=user) 
    context = {
        'bookmarks': bookmarks,
        'profile': profile,
    }
    return render(request, 'bookmark.html', context)


# Страница для редактирования профиля
def profile_update(request, username):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    # Обработка формы обновления профиля
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=username)
    else:
        form = UpdateProfileForm(instance=profile)
    
    return render(request, 'profile_update.html', {'form': form, 'profile': profile})


# Страница профиля пользователя
def profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    profile = get_object_or_404(Profile, user=user)
    context = {'profile': profile}
    return render(request, 'profile.html', context)


# Страница регистрации
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = Profile.objects.create(user=user)  # Создаём профиль для нового пользователя
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# Страница входа
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, "Неверный логин или пароль")
        else:
            messages.error(request, "Неправильный ввод")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


# Выход из аккаунта
def LogoutView(request):
    logout(request)
    return redirect('login')


# Чтение манги с главой
def manga_reader(request, manga_id, chapter_id):
    manga = get_object_or_404(Manga, pk=manga_id)
    chapter = get_object_or_404(Chapter, pk=chapter_id, manga=manga)
    images = chapter.images.all()
    
    # Получаем профиль пользователя (если авторизован)
    profile = Profile.objects.filter(user=request.user).first()

    # Пагинация по изображениям глав
    page = request.GET.get('page', 1)
    paginator = Paginator(images, 10)

    try:
        images_page = paginator.page(page)
    except PageNotAnInteger:
        images_page = paginator.page(1)
    except EmptyPage:
        images_page = paginator.page(paginator.num_pages)

    return render(request, 'manga_reader.html', {
        'manga': manga,
        'chapter': chapter,
        'images': images_page,
        'page_obj': images_page,
        'profile': profile,
    })


# API для получения глав манги
def api_chapters(request, manga_id):
    manga = get_object_or_404(Manga, pk=manga_id)
    chapters = manga.chapters.all()
    data = [{
        'manga': chapter.manga.pk,
        'id': chapter.id,
        'number': chapter.number,
        'title': chapter.title,
    } for chapter in chapters]
    return JsonResponse(data, safe=False)


# Оценка манги через API
@csrf_exempt
def rate_manga(request, manga_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rating_value = int(data.get('rating', 0))

            manga = Manga.objects.get(id=manga_id)
            MangaRating.objects.create(manga=manga, rating=rating_value)

            return JsonResponse({'success': True, 'message': 'Рейтинг сохранён'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Некорректный запрос'}, status=400)


# Редактирование комментария
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()

from django.shortcuts import get_object_or_404, redirect
from .models import Comment

# Удаление комментария
@login_required
def delete_comment(request, comment_id):
    # Ищем комментарий по ID
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    # Удаляем комментарий
    comment.delete()

    # Перенаправляем пользователя на предыдущую страницу (или на нужную)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def admin_required(user):
    return user.is_staff

# Представление для загрузки манги
@user_passes_test(admin_required)
def upload_manga(request):
    if request.method == "POST":
        form = MangaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Замените на нужный маршрут
    else:
        form = MangaForm()
    return render(request, 'manga_upload.html', {'form': form})

# Представление для загрузки главы
@user_passes_test(admin_required)
def upload_chapter(request):
    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ChapterForm()
    return render(request, 'chapter_upload.html', {'form': form})

# Представление для загрузки изображений в главу
@user_passes_test(admin_required)
def upload_image(request):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ImageForm()
    return render(request, 'image_upload.html', {'form': form})


def donationView(request):
    return render(request, 'donation.html')

def handler404(request, exception):
    return render(request, '404.html', status=404)