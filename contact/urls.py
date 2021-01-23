from django.urls import path
from .views import home, create, read, update, delete, search, logIn, logOut, register, readAll

urlpatterns = [
    path('', home),
    path('login/', logIn),
    path('logout/', logOut),
    path('register/', register),
    # CRUD
    path('create/', create),
    path('read/<str:email>', read),
    path('readAll/', readAll),
    path('update/', update),
    path('delete/<str:email>', delete),
    # Search
    path('search/', search),
]