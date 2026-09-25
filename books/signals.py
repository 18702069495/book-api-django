from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Book

@receiver(post_save, sender=Book)
def book_post_save(sender, instance, created, **kwargs):
    if created:
        print(f'新图书创建成功：{instance.title}')
    else:
        print(f'图书更新成功：{instance.title}')
    # 更新缓存，清除旧数据
    cache.delete('book_list_cache')