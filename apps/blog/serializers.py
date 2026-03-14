from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Post, Category, Tag, Comment,CategoryTranslation
from django.utils import timezone, formats,translation



class CategoryTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryTranslation
        fields = ['language', 'name']

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    # Это поле позволяет принимать список переводов в JSON
    translations = CategoryTranslationSerializer(many=True, write_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'translations']

    def get_name(self, obj):
        # Используем метод, который мы исправили в моделях (через фильтрацию)
        return obj.get_name()

    def create(self, validated_data):
        # Извлекаем данные переводов
        translations_data = validated_data.pop('translations')
        # Создаем основную категорию
        category = Category.objects.create(**validated_data)
        # Создаем записи в таблице переводов
        for trans_data in translations_data:
            CategoryTranslation.objects.create(category=category, **trans_data)
        return category

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class PostSerializer(ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        source="tags",
        queryset=Tag.objects.all(),
        write_only=True,
        many=True,
        required=False,
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "slug",
            "body",
            "category",
            "tags",
            "category_id",
            "tag_ids",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at")

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        post = super().create(validated_data)
        if tags:
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        post = super().update(instance, validated_data)
        if tags is not None:
            post.tags.set(tags)
        return post
    def get_created_at_formatted(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            user_tz = timezone.get_current_timezone()
            local_time = obj.created_at.astimezone(user_tz)
        else:
            local_time = obj.created_at
        return formats.date_format(local_time, "DATETIME_FORMAT")   



class CommentSerializer(ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "post", "body", "created_at")  # updated_at только если он есть в модели
        read_only_fields = ("id", "author", "created_at")

    def get_created_at_formatted(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            user_tz = timezone.get_current_timezone()
            local_time = obj.created_at.astimezone(user_tz)
        else:
            local_time = obj.created_at
        return formats.date_format(local_time, "DATETIME_FORMAT")   