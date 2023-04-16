from django.contrib import admin
from django.urls import path, include
from admin_panel import views
from django.contrib.auth import views as authViews

urlpatterns = [
    path('exit/', authViews.LogoutView.as_view(next_page='/login')),
    path('login/', views.loginuser),
    path('invalid/', views.invalid_login),
    path('poster/', views.poster),
    path('createposter/', views.createposter),
    path('deleteposter/<int:id>/', views.deleteposter),
    path('editposter/<int:id>/', views.editposter),
    path('geo/', views.geo),
    path('creategeo/', views.creategeo), 
    path('deletegeo/<int:id>/', views.deletegeo),
    path('editgeo/<int:id>/', views.editgeo),
    path('quest/', views.quest),
    path('addquiz/', views.add_quiz),
    path('delete_quiz/<int:id>/', views.delete_quiz),
    path('', views.index),
    path('admin/', admin.site.urls),
]
