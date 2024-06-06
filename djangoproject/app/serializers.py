from rest_framework import serializers
from .models import User, UserProfile, Post, Comment, Like, Following, Event

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_on', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Hide password field in responses

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['user', 'created_on']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['user', 'created_on']


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = ['follower', 'followed', 'created_on']
        read_only_fields = ['follower', 'created_on']

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['user', 'id', 'content', 'image', 'created_on', 'comments', 'likes']
    
    def validate_user(self, value):
        request = self.context['request']
        if value != request.user:
            raise serializers.ValidationError("User ID does not match token")
        return value

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'event_sponsor', 'price', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

