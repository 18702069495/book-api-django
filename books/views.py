from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Q,F,Count
from .models import Book,Author,Tag
from .serializers import BookSerializer,AuthorSerializer,TagSerializer
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    def get_queryset(self):
        # 统计每个作者的书籍数量
        return Author.objects.annotate(book_count = Count('book'))

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class BookViewSet(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle] # 限制匿名用户和登录用户请求频率
    throttle_scope = 'book'
    serializer_class = BookSerializer
    def get_queryset(self):
        # ========== ORM高级用法 JD重点 ==========
        # select_related：一对多连表查询，减少SQL查询次数
        # prefetch_related：多对多连表查询，减少SQL查询次数
        queryset = Book.objects.select_related('author').prefetch_related('tag')

        # 搜索过滤：Q 多条件复杂查询
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(Q(title__contains = keyword) | Q(author__name__contains = keyword) | Q(tag__name__contains = keyword))
        
        return queryset

    def list(self, request):
        # Redis缓存：缓存图书列表
        cache_key = 'book_list_cache'
        cache_data = cache.get(cache_key)
        if cache_data:
            print('从缓存中获取图书列表')
            return Response(cache_data)
        
        # 从数据库查询图书列表
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        # 缓存图书列表，过期时间为60s
        cache.set(cache_key, serializer.data, timeout = 60)
        print('从数据库查询图书列表')
        return Response(serializer.data)

    def create(self, request):
        from .tasks import send_notify_task
        # 调用父类的create方法，创建图书（默认会调用模型的save方法）
        resp = super().create(request)
        print(f'创建图书成功，返回数据：{resp.data}')
        # 提交异步任务到消息队列
        send_notify_task.delay(request.data.get('title'))
        return resp



        



