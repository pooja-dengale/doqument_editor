from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, UserListView

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserListView.as_view(), name='user-list'),
]
