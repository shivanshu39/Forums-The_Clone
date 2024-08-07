from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'),
    path('chat/', views.chat, name='chat'),
    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('user-profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('register/', views.registerPage, name='register'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    path('edit-user/<str:pk>/', views.editUser, name='edit-user'),
    path('topics-page/', views.topicPage, name='topics-page'),
    path('activity-page/', views.activityPage, name='activity-page')
    
]




