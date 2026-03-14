from django.db import models

from django.db.models import (
    TextField,
    TextChoices,
    CASCADE,
    )
# Create your models here.
from apps.users.models import CustomUser
from django.utils.translation import gettext_lazy as _

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
    # Ошибка была тут: language_code -> language
        translation = self.translation.filter(language='en').first()
        if translation:
            return translation.name
        return self.name
    
    def get_name(self, language: str = None):
        if language is None:
            from django.utils.translation import get_language
            raw_lang = get_language() or 'en'
            language = raw_lang.split("-")[0]
        
        # Здесь тоже меняем на language
        translation = self.translation.filter(language=language).first()
        if translation:
            return translation.name
            
        en_translation = self.translation.filter(language='en').first()
        return en_translation.name if en_translation else self.name
    
class CategoryTranslation(models.Model):
    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        related_name='translation',
    )
    language = models.CharField(
        max_length=10,
        choices=[('en', _('English')), ('ru', _('Russian')), ('kk', _('Kazakh'))],
        verbose_name=_('Language'),
    )
    name = models.CharField(
        max_length=50,
    )
    class Meta:
        unique_together = ('category', 'language')  
        verbose_name = _('Category Translation')
        verbose_name_plural = _('Category Translations')


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
        max_length=255,
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


