# AIQuant 配置管理指南

## 配置系统概述

配置系统采用分层设计，支持不同环境（开发、测试、生产）的配置分离，提高了系统的灵活性和安全性。

## 配置文件结构

### 环境变量文件 (.env)

`.env` 文件存储所有环境变量，包括：

- 数据库连接信息
- JWT 密钥和过期时间
- 应用运行环境设置
- 安全相关密钥
- 时区设置
- 日志配置

示例：
```
# 数据库配置
DATABASE_URI=postgresql://user:password@localhost:5432/aiquant
TEST_DATABASE_URI=postgresql://user:password@localhost:5432/aiquant_test

# JWT配置
JWT_SECRET_KEY=your_secret_key
JWT_ACCESS_TOKEN_EXPIRES=86400
```

### 配置类 (app/config.py)

配置类定义了不同环境的配置参数：

- `BaseConfig`: 所有环境共享的基础配置
- `DevelopmentConfig`: 开发环境特定配置
- `TestingConfig`: 测试环境特定配置
- `ProductionConfig`: 生产环境特定配置

## 使用方法

### 获取当前环境配置

系统会根据环境变量 `FLASK_ENV` 自动选择对应的配置类：

```python
from app.config import get_config

# 获取当前环境的配置类
config = get_config()
```

### 在应用中使用配置

应用初始化时会自动加载对应环境的配置：

```python
from app import create_app

# 创建应用实例（自动加载当前环境配置）
app = create_app()

# 或指定特定配置类
from app.config import ProductionConfig
app = create_app(ProductionConfig)
```

## 配置最佳实践

1. **敏感信息保护**：
   - 不要在代码中硬编码敏感信息
   - 生产环境使用环境变量或安全的密钥管理服务
   - 确保 `.env` 文件不被提交到版本控制系统

2. **环境隔离**：
   - 为不同环境（开发、测试、生产）使用不同的配置
   - 测试环境应使用独立的数据库

3. **配置验证**：
   - 应用启动时验证关键配置是否存在
   - 为必要的配置提供合理的默认值

4. **配置扩展**：
   - 需要添加新配置时，在 `BaseConfig` 或特定环境配置类中添加
   - 更新 `.env` 文件添加对应的环境变量

## 配置项说明

### 数据库配置
- `SQLALCHEMY_DATABASE_URI`: 主数据库连接URI
- `SQLALCHEMY_TRACK_MODIFICATIONS`: SQLAlchemy修改跟踪设置

### JWT配置
- `JWT_SECRET_KEY`: JWT签名密钥
- `JWT_ACCESS_TOKEN_EXPIRES`: 访问令牌过期时间（秒）

### 安全配置
- `SECRET_KEY`: Flask应用密钥
- `WTF_CSRF_SECRET_KEY`: CSRF保护密钥

### 应用配置
- `TIMEZONE`: 应用时区
- `DEBUG`: 调试模式开关
- `TESTING`: 测试模式开关

### 日志配置
- `LOG_LEVEL`: 日志级别
- `LOG_FILE_PATH`: 日志文件路径