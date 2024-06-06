"""dha_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views import SignupViewSet, LoginViewSet, ProfileViewSet, PostViewSet, CommentViewSet, LikeViewSet, FollowerViewSet, EventViewSet

'''
Usage:
Create: Send request to /endpoint/, and include user id in body
Read/Update/Delete: Send request to /endpoint/<id>/, don't include user id in body

'''
router = DefaultRouter()
router.register(r'signup', SignupViewSet, basename='signup')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'profile', ProfileViewSet) 
router.register(r'posts', PostViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'like', LikeViewSet, basename='like') # /like/<post-id>/like/ or /like/<post-id>/unlike/
router.register(r'follow', FollowerViewSet) #To view followers/ following: http://localhost:8000/follow/?user_id=<user_id>&followers / http://localhost:8000/follow/?user_id=<user_id>&followingrouter.register(r'event', EventViewSet)
router.register(r'events', EventViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),  # Include the default admin URLs
    path('', include(router.urls)),
]
