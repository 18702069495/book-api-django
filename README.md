# book-api-django



# test_django_1 启动说明

本项目基于 Django + DRF + MySQL + Redis + Celery + Nginx 实现，包含图书管理 API、Redis 缓存、Celery 异步任务、Nginx 静态文件与反向代理。

---

## 一、环境依赖

| 组件   | 版本要求                   | 用途                              |
| ------ | -------------------------- | --------------------------------- |
| Python | 3.12（虚拟环境`myvenv`） | 运行 Django / Celery              |
| MySQL  | 8.4 及以上                 | 业务数据库                        |
| Redis  | 任意稳定版本               | 缓存 + Celery 消息队列 + 结果存储 |
| Nginx  | 1.28.0                     | 静态文件 + 反向代理               |

---

## 二、配置概览（来自 `book_api/book_api/settings.py`）

| 服务                  | 配置值                                                                          | 说明         |
| --------------------- | ------------------------------------------------------------------------------- | ------------ |
| MySQL                 | `localhost:3306`，库 `book_db`，账号 `root/123456`                        | 业务数据库   |
| Redis 缓存            | `redis://localhost:6379/2`                                                    | Django 缓存  |
| Celery Broker         | `redis://localhost:6379/4`                                                    | 任务队列     |
| Celery Result Backend | `redis://localhost:6379/3`                                                    | 任务结果存储 |
| Django 开发服务器     | `0.0.0.0:8000`                                                                | API 服务     |
| Nginx                 | 监听`80` 端口，静态文件走 `/static`，动态请求反代到 `http://0.0.0.0:8000` | 入口网关     |

> Redis 不同 db 已做隔离：db2=缓存、db3=结果存储、db4=任务队列，禁止混用。

---

## 三、启动顺序

> 所有命令在 **PowerShell** 中执行。涉及系统服务的命令需用「管理员身份」运行。

### 1. 启动 MySQL

```powershell
net start MySQL84
```

验证连接：

```powershell
mysql -u root -p -e "SHOW DATABASES;"
```

> 首次使用需先建库（已存在可跳过）：
>
> ```sql
> CREATE DATABASE book_db DEFAULT CHARSET utf8mb4;
> ```

### 2. 启动 Redis

切换到 Redis 安装目录（按实际路径替换，如 `C:\Redis`），执行：

```powershell
redis-server.exe
```

> 如需注册为 Windows 服务后台运行：
>
> ```powershell
> redis-server.exe --service-install redis.windows.conf --service-name Redis
> redis-server.exe --service-start --service-name Redis
> ```

验证：

```powershell
redis-cli.exe ping
# 返回 PONG 即正常
```

### 3. 激活 Python 虚拟环境

```powershell
cd C:\Users\admin\Desktop\AI-project\test_django_1
.\myvenv\Scripts\Activate.ps1
```

> 若提示执行策略错误，先执行以下命令再重试：
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```
>
> 激活成功后，命令行前缀会出现 `(myvenv)`。

### 4. 首次启动：迁移数据库

```powershell
cd .\book_api
python manage.py migrate
```

> 后续如需根据模型变更重新生成迁移文件：
>
> ```powershell
> python manage.py makemigrations
> python manage.py migrate
> ```

### 5. 收集静态文件（Nginx 使用前必做）

```powershell
python manage.py collectstatic --noinput
```

> 默认收集到项目根目录 `static/`，Nginx 已配置好指向该目录。

### 6. 启动 Celery Worker（**新开一个终端**，保持前台运行）

```powershell
cd C:\Users\admin\Desktop\AI-project\test_django_1
.\myvenv\Scripts\Activate.ps1
cd .\book_api
celery -A book_api worker -l info -P solo
```

> **Windows 下必须加 `-P solo`**，否则 Celery 5.x 会因并发模型报错（`kombu.exceptions.EncodeError` 或 `Event loop is closed`）。

### 7. 启动 Django 开发服务器

```powershell
cd C:\Users\admin\Desktop\AI-project\test_django_1
.\myvenv\Scripts\Activate.ps1
cd .\book_api
python manage.py runserver 0.0.0.0:8000
```

### 8. 启动 Nginx（可选，用于前端整合访问）

```powershell
cd C:\Users\admin\Desktop\AI-project\test_django_1\nginx\nginx-1.28.0
.\nginx.exe
```

常用控制命令：

```powershell
.\nginx.exe -t          # 检查配置语法（启动前建议先跑一次）
.\nginx.exe -s reload   # 重载配置（修改 nginx.conf 后热更新）
.\nginx.exe -s stop     # 停止 Nginx
```

---

## 四、访问验证

| 访问方式        | URL                          | 说明                              |
| --------------- | ---------------------------- | --------------------------------- |
| 直连 Django     | http://localhost:8000/books/ | 走 DRF 接口                       |
| 走 Nginx        | http://localhost/books/      | Nginx 反代到 Django               |
| 静态文件        | http://localhost/static/     | 由 Nginx 直接返回                 |
| Celery 任务验证 | 新增图书后查看 Worker 终端   | 应打印「图书 xxx 新增通知已发送」 |

---

## 五、常见问题

### 1. MySQL 报 `MySQL 8.4 or later is required`

Django 6.1 要求 MySQL ≥ 8.4，请升级 MySQL 至 8.4+。

### 2. Navicat 报 `Plugin 'mysql_native_password' is not loaded`

在 MySQL 的 `my.ini` 的 `[mysqld]` 下加一行：

```ini
mysql_native_password=ON
```

然后重启 `MySQL84` 服务：

```powershell
net stop MySQL84
net start MySQL84
```

### 3. Celery 报 `RuntimeError: Event loop is closed` 或 `kombu.exceptions.EncodeError`

- 确认启动命令带了 `-P solo`（Windows 必加）；
- 确认 Redis 已启动且 db4 可写（`redis-cli -n 4 ping`）。

### 4. Nginx 静态文件 404

- 先执行 `python manage.py collectstatic`；
- 确认 `static/` 目录下确实有文件；
- 检查 `nginx.conf` 中 `alias` 路径是否为当前项目的绝对路径。

### 5. Nginx 接口 502 Bad Gateway

- 确认 Django `runserver 0.0.0.0:8000` 已启动；
- 确认 Nginx 的 `proxy_pass` 端口与 Django 一致；
- 防火墙未拦截 8000 端口。

### 6. 缓存不生效 / 数据不一致

Django 缓存走 Redis db2。数据变更后需手动清缓存：

```powershell
redis-cli.exe -n 2 FLUSHDB
```

### 7. 端口被占用

```powershell
# 查看占用 8000 端口的进程
netstat -ano | findstr :8000
# 结束该进程（PID 替换为上一步查到的数字）
taskkill /PID <PID> /F
```

---

## 六、停止顺序

1. Nginx：`.\nginx.exe -s stop`
2. Django / Celery：在对应终端按 `Ctrl + C`
3. Redis：前台进程按 `Ctrl + C`，或服务模式用 `redis-server.exe --service-stop`
4. MySQL：`net stop MySQL84`
