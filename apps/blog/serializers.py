from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Post, Category, Tag,Comment


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
class PostSerializer(ModelSerializer):
    author = serializers.StringRelatedField()
    category = CategorySerializer()
    tags = TagSerializer(many=True)

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
            "id"
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
        read_only_fields = ("id","author", "created_at", "updated_at")
    
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
    
class CommentSerializer(ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "post",
            "body",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at")