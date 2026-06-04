from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Document, DocumentShare
from .serializers import DocumentSerializer, DocumentShareSerializer, ShareDocumentSerializer, UserSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    CRUD for Documents.

    List/retrieve: returns documents the user owns OR has been shared with.
    Create: automatically sets the requesting user as the owner.
    Update/Delete: restricted to the document owner only.
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Documents the user owns OR has been shared with
        return Document.objects.filter(
            Q(owner=user) | Q(shares__shared_with=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def _assert_write_permission(self, request, document):
        """
        Raises a 403 Response if the requesting user is not allowed to write.
        Returns None if the user has write access.

        Rules:
          - Owner: always has write access.
          - Shared user with 'edit' permission: can update content/title.
          - Shared user with 'view' permission: read-only, 403 on any write.
          - Any other user: cannot even see the document (404 from get_queryset).
        """
        if document.owner == request.user:
            return None  # owner is always allowed

        share = DocumentShare.objects.filter(
            document=document, shared_with=request.user, permission='edit'
        ).first()
        if share:
            return None  # edit-share is allowed

        return Response(
            {'detail': 'You do not have permission to edit this document.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    def update(self, request, *args, **kwargs):
        document = self.get_object()
        denial = self._assert_write_permission(request, document)
        if denial:
            return denial
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        document = self.get_object()
        denial = self._assert_write_permission(request, document)
        if denial:
            return denial
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        if document.owner != request.user:
            return Response(
                {'detail': 'Only the document owner can delete this document.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='share')
    def share(self, request, pk=None):
        """
        POST /api/documents/{id}/share/
        Body: { "username": "bob", "permission": "edit" }

        Only the document owner can share.
        """
        document = self.get_object()

        if document.owner != request.user:
            return Response(
                {'detail': 'Only the document owner can share this document.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ShareDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        target_user = User.objects.get(username=serializer.validated_data['username'])

        if target_user == request.user:
            return Response(
                {'detail': 'You cannot share a document with yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        share, created = DocumentShare.objects.update_or_create(
            document=document,
            shared_with=target_user,
            defaults={'permission': serializer.validated_data['permission']}
        )

        return Response(
            DocumentShareSerializer(share).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['delete'], url_path='share/(?P<username>[^/.]+)')
    def revoke_share(self, request, pk=None, username=None):
        """
        DELETE /api/documents/{id}/share/{username}/

        Only the document owner can revoke access.
        """
        document = self.get_object()

        if document.owner != request.user:
            return Response(
                {'detail': 'Only the document owner can revoke access.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            target_user = User.objects.get(username=username)
            share = DocumentShare.objects.get(document=document, shared_with=target_user)
            share.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (User.DoesNotExist, DocumentShare.DoesNotExist):
            return Response({'detail': 'Share not found.'}, status=status.HTTP_404_NOT_FOUND)


class UserListView(generics.ListAPIView):
    """
    GET /api/users/
    Returns a list of all users (useful for the share UI to pick recipients).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
