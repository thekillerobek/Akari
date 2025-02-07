from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('manga/<str:original_title>/', views.manga_detail, name='manga_detail'),
    path('bookmark/add/<int:manga_id>/', views.add_Bookmark, name='add_bookmark'),
    path('bookmark/manga', views.BookmarkView, name='bookmark_view'),
    path('signup/', views.signup_view, name='signup'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/update/',views.profile_update , name='update'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('manga/<int:manga_id>/<int:chapter_id>/', views.manga_reader, name='manga_reader'),
    path('api/chapters/<int:manga_id>/', views.api_chapters, name='api_chapters'),
    path('api/rate_manga/<int:manga_id>/', views.rate_manga, name='rate_manga'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('upload/manga/', views.upload_manga, name='upload_manga'),
    path('upload/chapter/', views.upload_chapter, name='upload_chapter'),
    path('upload/image/', views.upload_image, name='upload_image'),
    path('donation/', views.donationView, name='donation')
]