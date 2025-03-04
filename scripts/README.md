# 数据初始化脚本

这个目录包含用于初始化测试数据的脚本。

## init_test_data.py

这个脚本用于生成测试数据并导入到数据库中，包括：

- 测试用户
- 数据源
- 股票数据和历史价格
- 策略模板和用户策略
- 回测记录和交易记录
- 交易账户、交易任务和持仓信息

### 使用方法

确保已经设置好数据库连接并创建了数据库表结构后，运行以下命令：

```bash
# 激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 运行初始化脚本
python -m scripts.init_test_data
```

### 注意事项

- 脚本会创建一个测试用户，用户名为`test_user`，密码为`password123`
- 脚本会生成过去30天的股票价格数据
- 所有生成的数据仅用于测试和开发目的