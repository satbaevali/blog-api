# Python modules
import logging

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

# Project modules
from apps.blog.models import Category, Tag, Post, Comment

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with test data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting database seed..."))

        # --- Users ---
        admin, created = User.objects.get_or_create(
            email="admin@blog.com",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("✓ Admin user created"))
        else:
            self.stdout.write("  Admin user already exists")

        user1, created = User.objects.get_or_create(
            email="alice@blog.com",
            defaults={
                "first_name": "Alice",
                "last_name": "Smith",
            },
        )
        if created:
            user1.set_password("alice123")
            user1.save()
            self.stdout.write(self.style.SUCCESS("✓ User Alice created"))

        user2, created = User.objects.get_or_create(
            email="bob@blog.com",
            defaults={
                "first_name": "Bob",
                "last_name": "Jones",
            },
        )
        if created:
            user2.set_password("bob123")
            user2.save()
            self.stdout.write(self.style.SUCCESS("✓ User Bob created"))

        # --- Categories ---
        cat1, _ = Category.objects.get_or_create(
            name="Technology",
            defaults={"slug": "technology"},
        )
        cat2, _ = Category.objects.get_or_create(
            name="Science",
            defaults={"slug": "science"},
        )
        self.stdout.write(self.style.SUCCESS("✓ Categories created"))

        # --- Tags ---
        tag1, _ = Tag.objects.get_or_create(
            name="Python",
            defaults={"slug": "python"},
        )
        tag2, _ = Tag.objects.get_or_create(
            name="Django",
            defaults={"slug": "django"},
        )
        tag3, _ = Tag.objects.get_or_create(
            name="API",
            defaults={"slug": "api"},
        )
        self.stdout.write(self.style.SUCCESS("✓ Tags created"))

        # --- Posts ---
        post1, created = Post.objects.get_or_create(
            slug="getting-started-with-django",
            defaults={
                "title": "Getting Started with Django",
                "body": "Django is a high-level Python web framework...",
                "author": user1,
                "category": cat1,
                "status": Post.Status.PUBLISHED,
            },
        )
        if created:
            post1.tags.set([tag1, tag2])
            self.stdout.write(self.style.SUCCESS("✓ Post 1 created"))

        post2, created = Post.objects.get_or_create(
            slug="building-rest-apis",
            defaults={
                "title": "Building REST APIs",
                "body": "REST APIs are the backbone of modern web apps...",
                "author": user2,
                "category": cat1,
                "status": Post.Status.PUBLISHED,
            },
        )
        if created:
            post2.tags.set([tag2, tag3])
            self.stdout.write(self.style.SUCCESS("✓ Post 2 created"))

        post3, created = Post.objects.get_or_create(
            slug="draft-post-example",
            defaults={
                "title": "Draft Post Example",
                "body": "This post is still in draft...",
                "author": user1,
                "status": Post.Status.DRAFT,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✓ Post 3 (draft) created"))

        # --- Comments ---
        if not Comment.objects.filter(post=post1).exists():
            Comment.objects.create(
                post=post1,
                author=user2,
                body="Great post! Very helpful for beginners.",
            )
            Comment.objects.create(
                post=post1,
                author=admin,
                body="Thanks for sharing this knowledge!",
            )
            self.stdout.write(self.style.SUCCESS("✓ Comments created"))

        self.stdout.write(
            self.style.SUCCESS("\n✅ Database seeded successfully!")
        )
        self.stdout.write("  Users: admin@blog.com / alice@blog.com / bob@blog.com")
        self.stdout.write("  Passwords: admin123 / alice123 / bob123")