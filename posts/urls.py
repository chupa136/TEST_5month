from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.post_list_create_api_view),
    path('posts/<int:id>/', views.post_detail_api_view),
    path('posts/<int:id>/comments/', views.post_comments_api_view),
    path('comments/<int:comment_id>/', views.comment_manage_api_view),
]