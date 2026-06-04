from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Document, DocumentShare


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class DocumentShareSerializer(serializers.ModelSerializer):
    shared_with_username = serializers.ReadOnlyField(source='shared_with.username')

    class Meta:
        model = DocumentShare
        fields = ['id', 'shared_with', 'shared_with_username', 'permission']


class DocumentSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    shares = DocumentShareSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'owner', 'owner_username', 'shares', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class ShareDocumentSerializer(serializers.Serializer):
    """Used for the share endpoint: accepts a username and permission level."""
    username = serializers.CharField()
    permission = serializers.ChoiceField(choices=['view', 'edit'])

    def validate_username(self, value):
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User '{value}' does not exist.")
        return value
