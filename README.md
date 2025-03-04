# AIQuant 量化交易平台

## 项目介绍

AIQuant是一个功能完善的量化交易平台，集成了市场数据获取、策略开发、回测分析和自动化交易等功能。平台基于Python Flask框架开发，提供RESTful API接口，支持多种交易策略的开发和回测。

### 主要功能

- **用户认证**：支持用户注册、登录和权限管理
- **市场数据**：集成多种数据源，提供实时和历史市场数据
- **策略管理**：支持策略的创建、编辑和管理
- **回测系统**：提供完整的策略回测功能，包括性能分析和可视化
- **交易执行**：支持实时交易和自动化交易任务

## 系统架构

```
AIQuant/
├── app/                    # 应用主目录
│   ├── auth/              # 用户认证模块
│   ├── market_data/       # 市场数据模块
│   ├── strategy/          # 策略管理模块
│   ├── backtest/          # 回测系统模块
│   ├── trading/           # 交易执行模块
│   ├── models/            # 数据模型
│   └── tasks.py           # 定时任务
├── .env                   # 环境变量配置
├── requirements.txt       # 依赖包列表
└── run.py                 # 应用入口
```

## 安装与部署

### 环境要求

- Python 3.9+
- PostgreSQL 12+
- TA-Lib (技术分析库)

### 安装步骤

1. **克隆代码库**

```bash
git clone https://github.com/yourusername/aiquant.git
cd aiquant
```

2. **创建并激活虚拟环境**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **安装依赖包**

```bash
pip install -r requirements.txt
```

4. **配置环境变量**

复制`.env.example`文件为`.env`，并根据实际情况修改配置：

```
# 数据库配置
DATABASE_URI=postgresql://username:password@localhost:5432/aiquant
TEST_DATABASE_URI=postgresql://username:password@localhost:5432/aiquant_test

# JWT配置
JWT_SECRET_KEY=your_super_secret_key_change_in_production
JWT_ACCESS_TOKEN_EXPIRES=86400

# 应用配置
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=True

# 安全配置
SECRET_KEY=dev_secret_key_change_in_production
WTF_CSRF_SECRET_KEY=csrf_dev_secret_key_change_in_production

# 其他配置
TIMEZONE=Asia/Shanghai

# 日志配置
LOG_LEVEL=DEBUG
LOG_FILE_PATH=logs/aiquant.log
```

5. **初始化数据库**

```bash
flask db init
flask db migrate
flask db upgrade
```

6. **启动应用**

```bash
flask run
```

或者直接运行：

```bash
python run.py
```

### 生产环境部署

对于生产环境，建议使用Gunicorn作为WSGI服务器，并配合Nginx作为反向代理：

```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"
```

## 配置管理

### 配置项说明

#### 数据库配置
- `DATABASE_URI`: 主数据库连接URI
- `TEST_DATABASE_URI`: 测试数据库连接URI

#### JWT配置
- `JWT_SECRET_KEY`: JWT签名密钥
- `JWT_ACCESS_TOKEN_EXPIRES`: 访问令牌过期时间（秒）

#### 安全配置
- `SECRET_KEY`: Flask应用密钥
- `WTF_CSRF_SECRET_KEY`: CSRF保护密钥

#### 日志配置
- `LOG_LEVEL`: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- `LOG_FILE_PATH`: 日志文件路径

### 配置最佳实践

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

## API接口文档

### 认证接口

#### 用户注册

```
POST /api/auth/register
```

请求参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| email | string | 是 | 邮箱 |
| password | string | 是 | 密码 |

响应示例：

```json
{
  "message": "注册成功",
  "user_id": 1
}
```

#### 用户登录

```
POST /api/auth/login
```

请求参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| email | string | 是 | 邮箱 |
| password | string | 是 | 密码 |

响应示例：

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### 市场数据接口

#### 获取数据源列表

```
GET /api/market-data/sources
```

响应示例：

```json
{
  "sources": [
    {
      "id": 1,
      "name": "Yahoo Finance",
      "description": "Yahoo金融数据源",
      "is_active": true
    }
  ]
}
```

#### 搜索股票

```
GET /api/market-data/stocks/search?q=AAPL
```

响应示例：

```json
{
  "stocks": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ",
      "last_price": 150.25,
      "last_update": "2023-08-01T15:30:00Z"
    }
  ]
}
```

#### 获取股票价格数据

```
GET /api/market-data/stocks/AAPL/price?interval=1d&period=1mo
```

响应示例：

```json
{
  "symbol": "AAPL",
  "interval": "1d",
  "period": "1mo",
  "data": [
    {
      "date": "2023-07-01T00:00:00Z",
      "open": 148.5,
      "high": 152.3,
      "low": 147.8,
      "close": 150.25,
      "volume": 75000000
    }
  ]
}
```

#### 同步股票数据

```
POST /api/market-data/stocks/sync
```

请求参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| symbols | array | 是 | 股票代码列表 |

响应示例：

```json
{
  "results": [
    {
      "symbol": "AAPL",
      "status": "success",
      "message": "数据同步成功"
    }
  ]
}
```

### 策略管理接口

#### 获取策略列表

```
GET /api/strategy/list
```

响应示例：

```json
{
  "strategies": [
    {
      "id": 1,
      "name": "移动平均线交叉策略",
      "description": "基于短期和长期移动平均线交叉的交易策略",
      "created_at": "2023-07-15T10:30:00Z"
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1
}
```

#### 创建新策略

```
POST /api/strategy/create
```

请求参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 是 | 策略名称 |
| description | string | 否 | 策略描述 |
| code | string | 是 | 策略代码 |

响应示例：

```json
{
  "message": "策略创建成功",
  "strategy_id": 1
}
```

### 回测系统接口

#### 获取回测列表

```
GET /api/backtest/list
```

响应示例：

```json
{
  "backtests": [
    {
      "id": 1,
      "name": "AAPL移动平均线策略回测",
      "description": "苹果股票的移动平均线策略回测",
      "strategy_id": 1,
      "strategy_name": "移动平均线交叉策略",
      "start_date": "2023-01-01T00:00:00Z",
      "end_date": "2023-06-30T00:00:00Z",
      "initial_capital": 100000,
      "status": "completed",
      "created_at": "2023-07-15T11:30:00Z"
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1
}
```

#### 创建新回测

```
POST /api/backtest/create
```

请求参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 是 | 回测名称 |
| description | string | 否 | 回测描述 |
| strategy_id | integer | 是 | 策略ID |
| start_date | string | 是 | 开始日期 (ISO格式) |
| end_date | string | 是 | 结束日期 (ISO格式) |
| initial_capital | number | 是 | 初始资金 |
| parameters | object | 否 | 策略参数 |

响应示例：

```json
{
  "message": "回测创建成功",
  "backtest_id": 1
}
```

#### 运行回测

```
POST /api/backtest/1/run
```

响应示例：

```json
{
  "message": "回测执行成功",
  "results": {
    "final_value": 120000,
    "return": 20.0,
    "sharpe_ratio": 1.5,
    "max_drawdown": 5.0,
    "total_trades": 10,
    "won_trades": 7,
    "lost_trades": 3,
    "win_rate": 70.0
  }
}
```

### 交易执行接口

#### 获取交易账户列表

```
GET /api/trading/accounts
```

响应示例：

```json
{
  "accounts": [
    {
      "id": 1,
      "name": "主交易账户",
      "broker": "Interactive Brokers",
      "account_type": "margin",
      "balance": 100000,
      "status": "active",
      "created_at": "2023-07-01T10:00:00Z"
    }
  ]
}
```

#### 创建交易账户

```
POST /api/trading/accounts
```

请求参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 是 | 账户名称 |
| broker | string | 是 | 券商名称 |
| account_type | string | 是 | 账户类型 |
| api_key | string | 是 | API密钥 |
| api_secret | string | 是 | API密钥 |

响应示例：

```json
{
  "message": "交易账户创建成功",
  "account_id": 1
}
```

#### 获取交易任务列表

```
GET /api/trading/tasks
```

响应示例：

```json
{
  "tasks": [
    {
      "id": 1,
      "name": "AAPL日内交易",
      "strategy_id": 1,
      "account_id": 1,
      "status": "running",
      "created_at": "2023-07-15T14:30:00Z"
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1
}
```

#### 创建交易任务

```
POST /api/trading/tasks
```

请求参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 是 | 任务名称 |
| strategy_id | integer | 是 | 策略ID |
| account_id | integer | 是 | 交易账户ID |
| parameters | object | 是 | 策略参数 |

响应示例：

```json
{
  "message": "交易任务创建成功",
  "task_id": 1
}
```

#### 启动交易任务

```
POST /api/trading/tasks/1/start
```

响应示例：

```json
{
  "message": "交易任务已启动"
}
```

#### 停止交易任务

```
POST /api/trading/tasks/1/stop
```

响应示例：

```json
{
  "message": "交易任务已停止"
}
```

#### 获取持仓列表

```
GET /api/trading/positions
```

响应示例：

```json
{
  "positions": [
    {
      "id": 1,
      "account_id": 1,
      "account_name": "主交易账户",
      "symbol": "AAPL",
      "quantity": 100,
      "average_cost": 150.25,
      "current_price": 155.75,
      "market_value": 15575.0,
      "unrealized_pnl": 550.0,
      "realized_pnl": 0.0,
      "open_date": "2023-07-20T10:30:00Z",
      "last_update": "2023-07-21T15:45:00Z"
    }
  ]
}
```

## 策略开发指南

### 策略结构

策略代码需要包含一个名为`generate_signals`的函数，该函数接收价格数据和策略参数，返回交易信号。

```python
def generate_signals(data, parameters):
    """
    生成交易信号
    
    参数:
        data (DataFrame): 包含OHLCV数据的DataFrame
        parameters (dict): 策略参数
        
    返回:
        DataFrame: 包含交易信号的DataFrame
    """
    # 计算指标
    short_window = parameters.get('short_window', 10)
    long_window = parameters.get('long_window', 30)
    
    # 计算短期和长期移动平均线
    data['short_ma'] = data['close'].rolling(window=short_window).mean()
    data['long_ma'] = data['close'].rolling(window=long_window).mean()
    
    # 生成信号
    data['signal'] = 0
    data.loc[data['short_ma'] > data['long_ma'], 'signal'] = 1  # 买入信号
    data.loc[data['short_ma'] < data['long_ma'], 'signal'] = -1  # 卖出信号
    
    # 生成交易动作
    data['action'] = data['signal'].diff()
    data.loc[data['action'] == 2, 'action'] = 'buy'  # 由-1变为1，买入
    data.loc[data['action'] == -2, 'action'] = 'sell'  # 由1变为-1，卖出
    
    return data
```

### 回测策略

使用回测系统评估策略性能：

1. 创建新策略并编写策略代码
2. 创建回测任务，设置回测参数
3. 运行回测并分析结果
4. 优化策略参数

### 部署到实盘

1. 创建交易账户并配置API密钥
2. 创建交易任务，选择策略和参数
3. 启动交易任务
4. 监控交易执行和持仓情况

## 常见问题

### 如何安装TA-Lib？

TA-Lib是一个技术分析库，安装可能比较复杂：

**Windows:**

1. 下载预编译的二进制文件：https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. 使用pip安装下载的文件：`pip install TA_Lib-0.4.28-cp39-cp39-win_amd64.whl`

**Linux:**

```bash
# 安装依赖
sudo apt-get install build-essential

# 下载并编译TA-Lib
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# 安装Python包装器
pip install ta-lib
```

**Mac:**

```bash
brew install ta-lib
pip install ta-lib
```

### 数据库迁移问题

如果遇到数据库迁移错误，可以尝试：

```bash
flask db stamp head  # 将数据库标记为最新版本
flask db migrate     # 创建新的迁移脚本
flask db upgrade     # 应用迁移
```

## 贡献指南

1. Fork项目仓库
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature-name`
5. 提交Pull Request

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。