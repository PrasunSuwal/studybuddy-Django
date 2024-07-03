from django.urls import path 
from base.api import views

urlpatterns = [
    path('solo/',views.getRooms),
    path('solo/<str:id>',views.getRoom),
]
