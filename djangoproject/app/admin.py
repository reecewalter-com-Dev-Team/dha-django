from django.contrib import admin
from .models import User, UserProfile, Post, Comment, Like, Following, FollowRequest, Event

# Register your models here.

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Following)
admin.site.register(FollowRequest)
admin.site.register(Event)
