from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import Document, DocumentShare


class DocumentAccessControlTests(APITestCase):
    """Tests for document ownership and sharing access control."""

    def setUp(self):
        # Create three users mirroring the production seed data
        self.alice = User.objects.create_user(username='alice', password='pass1234')
        self.bob = User.objects.create_user(username='bob', password='pass1234')
        self.charlie = User.objects.create_user(username='charlie', password='pass1234')

        # Create tokens for API auth
        self.alice_token = Token.objects.create(user=self.alice)
        self.bob_token = Token.objects.create(user=self.bob)
        self.charlie_token = Token.objects.create(user=self.charlie)

        # Alice creates a document
        self.doc = Document.objects.create(
            title='Alice Private Doc',
            content='<p>Secret content</p>',
            owner=self.alice,
        )

    # ------------------------------------------------------------------ #
    # Core access-control test                                            #
    # ------------------------------------------------------------------ #

    def test_unauthorized_user_cannot_access_document(self):
        """
        Charlie has no ownership or share on Alice's document.
        Attempting to retrieve it must return 404 (not leak its existence).
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.charlie_token.key}')
        url = reverse('document-detail', kwargs={'pk': self.doc.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_access_own_document(self):
        """Alice can read her own document."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.alice_token.key}')
        url = reverse('document-detail', kwargs={'pk': self.doc.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Alice Private Doc')

    def test_shared_user_can_access_document(self):
        """Bob gains access once Alice shares the document with him."""
        DocumentShare.objects.create(document=self.doc, shared_with=self.bob, permission='view')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.bob_token.key}')
        url = reverse('document-detail', kwargs={'pk': self.doc.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_shared_viewer_cannot_delete_document(self):
        """Bob has view access but cannot delete Alice's document."""
        DocumentShare.objects.create(document=self.doc, shared_with=self.bob, permission='view')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.bob_token.key}')
        url = reverse('document-detail', kwargs={'pk': self.doc.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_share_endpoint_grants_access(self):
        """
        Alice uses the share endpoint to grant Charlie view access.
        Charlie should then be able to retrieve the document.
        """
        # Alice shares with Charlie
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.alice_token.key}')
        share_url = reverse('document-share', kwargs={'pk': self.doc.pk})
        response = self.client.post(share_url, {'username': 'charlie', 'permission': 'view'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Charlie can now read the doc
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.charlie_token.key}')
        detail_url = reverse('document-detail', kwargs={'pk': self.doc.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_permission_user_cannot_edit_document(self):
        """
        Bob has 'view' access to Alice's document.
        A PATCH request to update the content must be rejected with 403.
        This validates the _assert_write_permission guard on partial_update.
        """
        DocumentShare.objects.create(document=self.doc, shared_with=self.bob, permission='view')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.bob_token.key}')
        url = reverse('document-detail', kwargs={'pk': self.doc.pk})
        response = self.client.patch(url, {'content': '<p>Injected content</p>'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_permission_user_can_update_document(self):
        """
        Bob has 'edit' access — a PATCH request must succeed with 200.
        """
        DocumentShare.objects.create(document=self.doc, shared_with=self.bob, permission='edit')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.bob_token.key}')
        url = reverse('document-detail', kwargs={'pk': self.doc.pk})
        response = self.client.patch(url, {'content': '<p>Bob edited this</p>'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cannot_share_document(self):
        """Bob cannot share Alice's document, even if he has edit access."""
        DocumentShare.objects.create(document=self.doc, shared_with=self.bob, permission='edit')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.bob_token.key}')
        share_url = reverse('document-share', kwargs={'pk': self.doc.pk})
        response = self.client.post(share_url, {'username': 'charlie', 'permission': 'view'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_request_is_rejected(self):
        """No credentials → 401 Unauthorized."""
        self.client.credentials()  # clear credentials
        url = reverse('document-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
