from django.db import models

from django.db.models import (
    TextField,
    TextChoices,
    CASCADE,
    )
# Create your models here.
from apps.users.models import CustomUser

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
    
class Category(BaseModel):
    name = models.CharField(
        max_length=50,
        unique=True,

        )
    slug = models.SlugField(
        unique=True,
    )


    def __str__(self):
        return self.name
    
class Tag(BaseModel):
    name = models.CharField(
        max_length=50,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
    )

    def __str__(self):
        return self.name

class Post(BaseModel):
    class Status(TextChoices):
        DRAFT = "draft",
        PUBLISHED = "published"
    author = models.ForeignKey(
        to = CustomUser,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    title = models.CharField(
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
    )
    body = TextField()
    category = models.ForeignKey(
        to=Category,
        on_delete=models.SET_NULL,
        null=True,
    )
    tags = models.ManyToManyField(
        to=Tag,
        blank=True,
        related_name='posts',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

class Comment(BaseModel):
    post = models.ForeignKey(
        to = Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        to = CustomUser,
        on_delete = CASCADE,
        related_name="comments"
        )
    body = models.TextField()


