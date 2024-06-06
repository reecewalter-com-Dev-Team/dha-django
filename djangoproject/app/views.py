from django.contrib.auth.hashers import make_password
from rest_framework import status, viewsets
from rest_framework.response import Response
from .serializers import UserSerializer, ProfileSerializer, PostSerializer, CommentSerializer, LikeSerializer, FollowSerializer, EventSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import UserProfile, User, Post, Comment, Like, Following, FollowRequest, Event
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
from .permissions import IsOwnerOrReadOnly, IsOwnerOrPostOwner, IsAdminOrReadOnly
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404


class SignupViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(password=make_password(serializer.validated_data['password']))  # Hashing the password
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': serializer.data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user:
            # If authentication successful, generate token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        # Get the user ID from the URL
        user_id = self.kwargs.get('pk')
        # Get or create the UserProfile for the given user ID
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            # Handle the case where the UserProfile does not exist
            user = User.objects.get(pk=user_id)
            user_profile = UserProfile.objects.create(user=user)
        return user_profile

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        # Ensure the user in the token matches the user in the request data
        if serializer.validated_data['user'] != self.request.user:
            return Response({'detail': 'User ID does not match token'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Ensure the user in the token matches the user in the request data
        if serializer.validated_data.get('user') and serializer.validated_data['user'] != self.request.user:
            return Response({'detail': 'User ID does not match token'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPostOwner]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly])
    def like(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response(status=status.HTTP_201_CREATED)
        return Response({"detail": "Already liked."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly])
    def unlike(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Not liked yet."}, status=status.HTTP_400_BAD_REQUEST)
    
class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Following.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        followed_user_id = request.data.get('user_id')
        if not followed_user_id:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            followed_user = User.objects.get(id=followed_user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Access UserProfile to check account_privacy 
        try:
            followed_user_profile = followed_user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"detail": "User Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
        if followed_user_profile.account_private:
            # Handle follow request for private account
            follow_request, created = FollowRequest.objects.get_or_create(requester=request.user, receiver=followed_user)
            if created:
                return Response({"detail": "Follow request sent."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "Follow request already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Handle direct follow for public account
            follow_instance = Following.objects.filter(follower=request.user, followed=followed_user).first()
            if follow_instance:
                return Response({"detail": "Already Following."}, status=status.HTTP_204_NO_CONTENT)
            else:
                follow_instance = Following(follower=request.user, followed=followed_user)
                follow_instance.save()
                return Response({"detail": "Followed successfully."}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if 'followers' in request.query_params:
            # View a user's followers
            followers = Following.objects.filter(followed=user)
            serializer = self.get_serializer(followers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif 'following' in request.query_params:
            # View who a user is following
            following = Following.objects.filter(follower=user)
            serializer = self.get_serializer(following, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:
            return Response({"detail": "Specify either 'followers' or 'following' in the query parameters."}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')  # Get the user_id from the URL
        if not user_id:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check for an existing follow request
        follow_request = FollowRequest.objects.filter(requester=request.user, receiver=user).first()
        if follow_request:
            follow_request.delete()
            return Response({"detail": "Follow request deleted."}, status=status.HTTP_204_NO_CONTENT)
        
        # Check for an existing follow instance
        follow_instance = Following.objects.filter(follower=request.user, followed=user).first()
        if follow_instance:
            follow_instance.delete()
            return Response({"detail": "Unfollowed successfully."}, status=status.HTTP_204_NO_CONTENT)

        # If neither follow request nor follow instance exists
        return Response({"detail": "No follow request or follow instance found."}, status=status.HTTP_404_NOT_FOUND)
    
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)