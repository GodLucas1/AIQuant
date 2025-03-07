import { get, post, put, del } from '../utils/request'

/**
 * 获取策略列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @param {string} params.keyword - 搜索关键词
 * @returns {Promise<Object>} - 策略列表和分页信息
 */
export function getStrategies(params) {
  return get('/strategy/list', params)
}

/**
 * 获取策略详情
 * @param {string} id - 策略ID
 * @returns {Promise<Object>} - 策略详情
 */
export function getStrategyById(id) {
  return get(`/strategy/${id}`)
}

/**
 * 创建新策略
 * @param {Object} data - 策略数据
 * @param {string} data.name - 策略名称
 * @param {string} data.description - 策略描述
 * @param {string} data.code - 策略代码
 * @param {Array} data.parameters - 策略参数
 * @returns {Promise<Object>} - 创建结果
 */
export function createStrategy(data) {
  return post('/strategy', data)
}

/**
 * 更新策略
 * @param {string} id - 策略ID
 * @param {Object} data - 更新的策略数据
 * @returns {Promise<Object>} - 更新结果
 */
export function updateStrategy(id, data) {
  return put(`/strategy/${id}`, data)
}

/**
 * 删除策略
 * @param {string} id - 策略ID
 * @returns {Promise<Object>} - 删除结果
 */
export function deleteStrategy(id) {
  return del(`/strategy/${id}`)
}

/**
 * 获取策略模板列表
 * @returns {Promise<Array>} - 策略模板列表
 */
export function getStrategyTemplates() {
  return get('/strategy/templates')
}

/**
 * 测试策略语法
 * @param {Object} data - 策略代码
 * @param {string} data.code - 策略代码
 * @returns {Promise<Object>} - 测试结果
 */
export function testStrategyCode(data) {
  return post('/strategy/test', data)
}

/**
 * 获取策略运行日志
 * @param {string} id - 策略ID
 * @returns {Promise<Array>} - 日志列表
 */
export function getStrategyLogs(id) {
  return get(`/strategy/${id}/logs`)
} 