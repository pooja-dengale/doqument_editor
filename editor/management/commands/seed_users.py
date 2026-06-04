"""
Management command: python manage.py seed_users

Creates three test users (Alice, Bob, Charlie) and their API tokens.
Safe to run multiple times — skips existing users.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


SEED_USERS = [
    {'username': 'alice', 'email': 'alice@example.com', 'password': 'alice1234'},
    {'username': 'bob',   'email': 'bob@example.com',   'password': 'bob12345'},
    {'username': 'charlie', 'email': 'charlie@example.com', 'password': 'charlie1'},
]


class Command(BaseCommand):
    help = 'Seed the database with Alice, Bob, and Charlie test users.'

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

            token, _ = Token.objects.get_or_create(user=user)
            self.stdout.write(f"  Token: {token.key}")
