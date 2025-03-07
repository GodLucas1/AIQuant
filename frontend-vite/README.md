# AIQuant - 量化交易平台前端

这是AIQuant量化交易平台的前端项目，基于Vue 3和Vite开发，使用Element Plus作为UI组件库。

## 项目结构

```
frontend-vite/
├── public/             # 静态资源
├── src/                # 源代码
│   ├── api/            # API请求模块
│   ├── assets/         # 资源文件
│   ├── components/     # 公共组件
│   ├── router/         # 路由配置
│   ├── utils/          # 工具函数
│   ├── views/          # 页面视图组件
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── .env                # 环境变量
├── index.html          # HTML模板
├── package.json        # 项目配置
└── vite.config.js      # Vite配置
```

## 主要功能模块

1. **用户认证** - 登录、注册和用户管理
2. **市场数据** - 股票行情查询和数据分析
3. **策略管理** - 创建、编辑和管理交易策略
4. **回测分析** - 策略回测和性能评估
5. **交易中心** - 实盘交易和持仓管理

## 技术栈

- **Vue 3** - 前端框架
- **Vite** - 构建工具
- **Vue Router** - 路由管理
- **Element Plus** - UI组件库
- **ECharts** - 图表库
- **Axios** - HTTP客户端
- **Pinia** - 状态管理

## 快速启动

确保已安装Node.js (版本14+)和npm，然后执行以下步骤：

1. **安装依赖**
   ```bash
   cd frontend-vite
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

3. **在浏览器中访问**
   ```
   http://localhost:5173
   ```

## 构建生产版本

```bash
npm run build
```

构建后的文件将生成在`dist`目录中，可以部署到任何静态文件服务器。

## 后端API

前端通过以下API接口与后端通信：

- `/api/auth/*` - 用户认证相关接口
- `/api/market-data/*` - 市场数据相关接口
- `/api/strategy/*` - 策略管理相关接口
- `/api/backtest/*` - 回测分析相关接口
- `/api/trading/*` - 交易相关接口

## 开发指南

### 配置API地址

默认情况下，前端应用会假定后端API位于同一域的`/api`路径下。如果需要更改API地址，请修改`.env`文件中的`VITE_API_BASE_URL`变量。
