from django import forms
from django.forms import ModelForm, TextInput, Textarea
from .models import Geo

class LoginForm(forms.Form):
    username = forms.CharField(label="",widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя', "class":"form-control mb-2"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль',"class":"password form-control mb-2"}), label="")

class GeoForm(forms.Form):
    name = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Название локации', "class":"form-control mb-3"}))
    desc = forms.CharField(label="", widget=forms.Textarea(attrs={'placeholder': 'Описание локации', "class":"form-control mb-3"}))
    link = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Ссылка на локацию', "class":"form-control mb-3"}))