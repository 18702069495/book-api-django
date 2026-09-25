from rest_framework import serializers
from .models import Book,Author,Tag

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author_info = AuthorSerializer(source = 'author', read_only = True)
    tag_info = TagSerializer(source = 'tag', read_only = True, many = True)
    class Meta:
        model = Book
        fields = ['id','title','author','author_name','author_info','tag','tag_info','create_time','update_time']
