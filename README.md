# python-fastapi-admin

一个面向“快速落地后台接口”的 FastAPI 项目骨架：自带统一响应结构、统一异常处理、请求链路 TraceId、结构化日志、登录鉴权依赖（RBAC 扩展点）、以及清晰的分层目录，适合小白上手和团队推广。

## 特性（为什么值得用）

- 统一响应协议：所有接口返回同一结构 `{code, message, data, error, trace_id}`
- 统一异常处理：校验错误/业务错误/HTTP 错误/系统错误统一落在一个地方，减少重复 try/except
- TraceId 全链路：支持从请求头 `X-Trace-Id` 透传；不传则自动生成并回写到响应头
- 生产级日志：Loguru + JSON 文件日志；按大小轮转（50MB）+ 保留策略；控制台可读日志
- 清晰架构：api / services / repositorys / models / schemas / core / middlewares / exceptions
- 权限扩展点：通过依赖注入实现 “未登录/无权限” 的标准返回与 RBAC 入口

## 快速开始（小白 3 步跑起来）

### 1) 安装依赖

```bash
poetry install
```

### 2) 配置

配置文件在 `config/config.toml`：

- 数据库：`[database]`（需要 MySQL 可连通）
- JWT：`[secret]`（生产环境务必修改 `secret_key`）
- 日志：`[logger]`

### 3) 启动

本地开发启动：

```bash
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8003 --reload
```

生产启动（示例，Dockerfile 默认使用 gunicorn）：

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8080
```

健康检查：

- `GET /healthz` -> `{"status":"ok"}`

## 项目架构（读完就能改）

### 分层说明

- `app/main.py`：应用入口，注册中间件、异常处理、路由；lifespan 里初始化资源
- `app/core/`：核心能力（配置、DB、日志、响应、鉴权工具）
- `app/middlewares/`：中间件（trace/logging）
- `app/exceptions/`：异常与错误码（业务异常 + 统一异常处理）
- `app/api/`：路由层（HTTP 协议适配）
  - `public/`：公开接口（例如登录）
  - `private/`：需要登录才能访问的接口（通过 dependencies 保护）
- `app/services/`：业务编排（做“业务规则”，不直接写 SQL）
- `app/repositorys/`：数据访问层（写 SQLModel/SQLAlchemy 查询）
- `app/models/`：ORM 模型
- `app/schemas/`：请求/响应 Schema（Pydantic/SQLModel）
- `app/utils/`：通用工具（context/校验等）

### 请求流（从进来到出去）

1. `trace_middleware` 处理 `X-Trace-Id`：写入上下文并回写响应头
2. `logging_middleware` 记录访问日志：读取响应体里的 `code` 决定 info/warn
3. 路由处理：`api -> service -> repository -> db`
4. 异常统一落地：`app/exceptions/handlers.py` 输出统一 `Response.fail`
5. `Response` 自动填充 `trace_id`：默认从上下文获取，无需每个接口手动传

可以把它理解成下面这条链路：

```
Client
  -> Middlewares(trace -> logging)
  -> Router(api/public & api/private)
  -> Service
  -> Repository
  -> DB
  <- Response(success/fail + trace_id)
```

## 登录与权限（怎么保护接口）

### Token 约定

- 登录接口：`POST /api/public/auth/login`
- 请求头：`Authorization: Bearer <jwt>`

JWT 的生成/解析在：

- `app/core/security.py`

### 保护 private 路由

`private` 路由默认通过依赖保护（示例）：

- `app/api/private/auth.py`
- `app/core/deps.py`

如果你新增私有接口，建议放在 `app/api/private/` 并加 `Depends(get_current_user)` 或更细粒度的 `require_role/require_permission`。

## 日志怎么用

日志初始化在应用启动时自动完成（见 `lifespan`），一般业务代码这样打日志：

```python
from app.core.logging import logger

logger.info("创建用户 user_id=%s", user_id)
logger.warning("权限不足")
logger.exception("系统异常")
```

日志配置在 `[logger]`：

- `dir`：日志目录（默认 `logs`）
- `file`：日志文件名
- `rotation`：轮转大小（默认 `50 MB`）
- `retention`：保留策略（示例为保留最近 N 个）

## 常见问题（排坑）

- 401/403/404/422 不是“随机报错”：项目采用统一异常处理，返回体里看 `code/message/error/trace_id`（错误码在 `app/exceptions/codes.py`）
- `trace_id` 为 `-`：检查请求是否经过 trace 中间件，以及是否传入 `X-Trace-Id`
- 数据库连不上：确认 `config/config.toml` 的 `[database]` 配置与 MySQL 可用
- Docker 构建失败：如果你的 Dockerfile 依赖 `requirements.txt`，需要先在本地生成（或改用 Poetry 镜像方案）
