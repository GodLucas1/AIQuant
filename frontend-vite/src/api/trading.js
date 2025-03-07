import { get, post, put, del } from '../utils/request'

/**
 * 获取交易账户列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Array>} - 账户列表
 */
export function getAccounts(params) {
  return get('/trading/accounts', params)
}

/**
 * 获取账户详情
 * @param {string} id - 账户ID
 * @returns {Promise<Object>} - 账户详情
 */
export function getAccountById(id) {
  return get(`/trading/accounts/${id}`)
}

/**
 * 添加交易账户
 * @param {Object} data - 账户信息
 * @param {string} data.name - 账户名称
 * @param {string} data.exchange - 交易所
 * @param {string} data.apiKey - API Key
 * @param {string} data.apiSecret - API Secret
 * @param {string} data.passphrase - 密码（部分交易所需要）
 * @returns {Promise<Object>} - 添加结果
 */
export function addAccount(data) {
  return post('/trading/accounts', data)
}

/**
 * 更新交易账户
 * @param {string} id - 账户ID
 * @param {Object} data - 更新信息
 * @returns {Promise<Object>} - 更新结果
 */
export function updateAccount(id, data) {
  return put(`/trading/accounts/${id}`, data)
}

/**
 * 删除交易账户
 * @param {string} id - 账户ID
 * @returns {Promise<Object>} - 删除结果
 */
export function deleteAccount(id) {
  return del(`/trading/accounts/${id}`)
}

/**
 * 获取账户余额
 * @param {string} id - 账户ID
 * @returns {Promise<Object>} - 余额信息
 */
export function getAccountBalance(id) {
  return get(`/trading/accounts/${id}/balance`)
}

/**
 * 获取当前持仓
 * @param {Object} params - 查询参数
 * @param {string} params.accountId - 账户ID
 * @returns {Promise<Array>} - 持仓列表
 */
export function getPositions(params) {
  return get('/trading/positions', params)
}

/**
 * 获取订单列表
 * @param {Object} params - 查询参数
 * @param {string} params.accountId - 账户ID
 * @param {string} params.status - 订单状态
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @returns {Promise<Object>} - 订单列表和分页信息
 */
export function getOrders(params) {
  return get('/trading/orders', params)
}

/**
 * 创建订单
 * @param {Object} data - 订单信息
 * @param {string} data.accountId - 账户ID
 * @param {string} data.symbol - 交易对
 * @param {string} data.type - 订单类型，如 "limit", "market"
 * @param {string} data.side - 买卖方向，如 "buy", "sell"
 * @param {number} data.price - 价格（限价单）
 * @param {number} data.amount - 数量
 * @returns {Promise<Object>} - 创建结果
 */
export function createOrder(data) {
  return post('/trading/orders', data)
}

/**
 * 取消订单
 * @param {string} id - 订单ID
 * @returns {Promise<Object>} - 取消结果
 */
export function cancelOrder(id) {
  return post(`/trading/orders/${id}/cancel`)
}

/**
 * 获取交易任务列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Array>} - 任务列表
 */
export function getTradingTasks(params) {
  return get('/trading/tasks', params)
}

/**
 * 创建交易任务
 * @param {Object} data - 任务信息
 * @param {string} data.name - 任务名称
 * @param {string} data.accountId - 账户ID
 * @param {string} data.strategyId - 策略ID
 * @param {Object} data.parameters - 策略参数
 * @param {Object} data.config - 任务配置
 * @returns {Promise<Object>} - 创建结果
 */
export function createTradingTask(data) {
  return post('/trading/tasks', data)
}

/**
 * 停止交易任务
 * @param {string} id - 任务ID
 * @returns {Promise<Object>} - 操作结果
 */
export function stopTradingTask(id) {
  return post(`/trading/tasks/${id}/stop`)
}

/**
 * 启动交易任务
 * @param {string} id - 任务ID
 * @returns {Promise<Object>} - 操作结果
 */
export function startTradingTask(id) {
  return post(`/trading/tasks/${id}/start`)
}

/**
 * 获取交易统计数据
 * @param {Object} params - 查询参数
 * @param {string} params.accountId - 账户ID
 * @param {number} params.startTime - 开始时间戳
 * @param {number} params.endTime - 结束时间戳
 * @returns {Promise<Object>} - 统计数据
 */
export function getTradingStats(params) {
  return get('/trading/stats', params)
} 