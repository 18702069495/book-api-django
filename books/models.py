from django.db import models

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='作者姓名')
    age = models.IntegerField(verbose_name='作者年龄')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'author'
        verbose_name = '作者'
        verbose_name_plural = '作者'
        ordering = ['id']
        indexes = [
            models.Index(fields=['name','age'])
        ]

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name='标签名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'tag'
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['id']
        indexes = [
            models.Index(fields=['name'])
        ]

class Book(models.Model):
    title = models.CharField(max_length=50, unique=True, verbose_name='图书名称')
    tag = models.ManyToManyField(Tag, verbose_name='图书标签')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='图书作者')
    author_name = models.CharField(max_length=20, verbose_name='作者姓名')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'book'
        verbose_name = '图书'
        verbose_name_plural = '图书'
        ordering = ['id']
        indexes = [
            models.Index(fields=['title','author_name'])
        ]

