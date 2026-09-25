from celery import shared_task
import time


@shared_task
def send_notify_task(book_name):
    # 模拟耗时任务：消息推送
    time.sleep(2)
    print(f"【Celery异步任务】图书 {book_name} 新增通知已发送")
    return "ok"



