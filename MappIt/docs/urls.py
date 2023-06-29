from django.urls import path
from . import views
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView

urlpatterns = [
    path('', views.home, name='docs-home'),
    path('main/', views.docs_content, name='docs-page'),
    path('questions/', PostListView.as_view(), name='docs-questions'),
    path('questions/<int:pk>/', PostDetailView.as_view(), name='docs-questions-detail'),
    path('questions/<int:pk>/update/', PostUpdateView.as_view(), name='docs-questions-update'),
    path('questions/<int:pk>/delete/', PostDeleteView.as_view(), name='docs-questions-delete'),
    path('questions/new/', PostCreateView.as_view(), name='docs-questions-create'),
    path('profile/', views.profile , name='docs-profile'),
]
