from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

# Create your models here.

# User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_on = models.DateTimeField(default=timezone.now)

    
#Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True) #sent as user id
    name = models.CharField(max_length=100)
    pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    home_lake = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    prostaff_or_sponsor = models.CharField(choices=[('Prostaff', 'Prostaff'), ('Sponsor', 'Sponsor')], max_length=20)
    company = models.CharField(max_length=100)
    tournaments_fished = models.TextField(blank=True)
    career_stats_and_earnings = models.TextField(blank=True)
    diehard_anglers_affiliate_link = models.URLField(blank=True)
    calendar_privacy = models.BooleanField(default=False)  # True for private, False for public
    account_private = models.BooleanField(default=False)  # True for private, False for public



    def __str__(self):
        return self.user.username
    
#Followers model
class Following(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('follower', 'followed')
    
    def __str__(self):
        return f'{self.follower.username} follows {self.followed.username}'

#Follow Requests
class FollowRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_follow_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_follow_requests')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')])

    class Meta:
        unique_together = ('requester', 'receiver')

    def __str__(self):
        return f'{self.requester.username} requests to follow {self.receiver.username}'
    
# Post model
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Post by {self.user.username} on {self.created_on}'

# Comment model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post}'

# Like model
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'post')  # Ensure a user can like a post only once

    def __str__(self):
        return f'Like by {self.user.username} on {self.post}'
    
# Event Model
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    event_sponsor = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} created by {self.user}'