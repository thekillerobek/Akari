from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Profile,Comment,Manga,Chapter,Image


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Напишите комментарий...'}),
        }


class MangaForm(forms.ModelForm):
    class Meta:
        model = Manga
        fields = ['title','original_title', 'author', 'description', 'cover', 'genres', 'typr','tags','uploader','status','datte']


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['title', 'number', 'manga']


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'chapter']