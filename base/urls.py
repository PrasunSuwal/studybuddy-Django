from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name = 'index'), 
    path('topics/', views.topics, name = 'topics'),
    path('activity/', views.activity, name='activity'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('login/', views.userLogin, name = 'login'),
    path('signup/', views.signUp, name = 'signup'),
    path('room/<slug:slug>/', views.room, name = 'room'),
    path('create-room/', views.createRoom, name = 'create-room'),
    path('edit-user/', views.editUser, name = 'edit-user'),
    path('delete/', views.delete, name = 'delete'),
    path('logout/',views.userLogout, name='logout'),
    path('edit-room/<slug:slug>', views.editRoom, name='editRoom'),
    path('delete-room/<slug:slug>', views.deleteRoom, name='deleteRoom'),
    path('delete-message/<slug:slug>', views.deleteMessage, name='deleteMessage'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
