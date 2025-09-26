from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Post, Comment
from .serializer import (PostSerializer, CommentSerializer, PostCreateSerializer,
CommentCreateSerializer)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
def post_list_create_api_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            my_posts = Post.objects.filter(author=request.user)
            other_posts = Post.objects.filter(is_published=True).exclude(author=request.user)
            posts = my_posts | other_posts
        else:
            posts = Post.objects.filter(is_published=True).order_by('-created_at')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def post_detail_api_view(request, id):
    try:
        post = Post.objects.get(id=id, is_published=True)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'DELETE']:
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if post.author != request.user:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'PUT':
            serializer = PostCreateSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(PostSerializer(post).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            post.delete()
            return Response({'message': 'Post deleted successfully'})


@api_view(['GET', 'POST'])
def post_comments_api_view(request, id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not post.is_published and post.author != request.user:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        comments = Comment.objects.filter(post=post, is_approved=True)
        
        if request.user.is_authenticated:
            my_unapproved_comments = Comment.objects.filter(
                post=post, author=request.user, is_approved=False
            )
            comments = comments | my_unapproved_comments
        
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(post=post, author=request.user)
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(
        {'error': 'Method not allowed'}, 
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_manage_api_view(request,comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    if not comment.post.is_published and comment.post.author != request.user:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        if comment.author != request.user:
            return Response(
                {'error': 'You can only edit your own comments'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CommentCreateSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            updated_comment = serializer.save()
            return Response(CommentSerializer(updated_comment).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if comment.author != request.user and comment.post.author != request.user:
            return Response(
                {'error': 'You can only delete your own comments or comments on your posts'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()   
        return Response({'message': 'Comment deleted successfully'},
        status=status.HTTP_204_NO_CONTENT)