"""
Management command: python manage.py seed_users

Creates three test users (Alice, Bob, Charlie) with FIXED tokens.
Fixed tokens mean the frontend never needs updating after a redeploy.
Safe to run multiple times — skips existing users/tokens.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


SEED_USERS = [
    {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'alice1234',
        'token': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',  # fixed token
    },
    {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'bob12345',
        'token': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',  # fixed token
    },
    {
        'username': 'charlie',
        'email': 'charlie@example.com',
        'password': 'charlie1',
        'token': 'cccccccccccccccccccccccccccccccccccccccc',  # fixed token
    },
]


class Command(BaseCommand):
    help = 'Seed the database with Alice, Bob, and Charlie with fixed tokens.'

    def handle(self, *args, **options):
        for data in SEED_USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': data['email']},
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))
            else:
                self.stdout.write(f"User already exists: {user.username}")

            # Delete any existing token and recreate with fixed key
            Token.objects.filter(user=user).delete()
            Token.objects.create(user=user, key=data['token'])
            self.stdout.write(f"  Token: {data['token']}")
