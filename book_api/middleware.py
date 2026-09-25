import time 

class ResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        cost = time.time() - start_time
        # 打印请求路径和耗时
        print(f"中间件路径：{request.path}，耗时：{cost:.4f}秒")
        return response
