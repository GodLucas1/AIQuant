import { get, post, put, del } from '../utils/request'

/**
 * 获取回测列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @param {string} params.strategyId - 策略ID（可选）
 * @param {string} params.keyword - 搜索关键词
 * @returns {Promise<Object>} - 回测列表和分页信息
 */
export function getBacktests(params) {
  return get('/backtest/list', params)
}

/**
 * 获取回测详情
 * @param {string} id - 回测ID
 * @returns {Promise<Object>} - 回测详情
 */
export function getBacktestById(id) {
  return get(`/backtest/${id}`)
}

/**
 * 创建新回测
 * @param {Object} data - 回测配置
 * @param {string} data.strategyId - 策略ID
 * @param {string} data.name - 回测名称
 * @param {string} data.description - 回测描述
 * @param {string} data.symbol - 交易对
 * @param {string} data.exchange - 交易所
 * @param {string} data.interval - K线间隔
 * @param {number} data.startTime - 开始时间戳
 * @param {number} data.endTime - 结束时间戳
 * @param {Object} data.parameters - 策略参数
 * @param {Object} data.capital - 资金配置
 * @returns {Promise<Object>} - 创建结果
 */
export function createBacktest(data) {
  return post('/backtest', data)
}

/**
 * 获取回测结果
 * @param {string} id - 回测ID
 * @returns {Promise<Object>} - 回测结果
 */
export function getBacktestResult(id) {
  return get(`/backtest/${id}/result`)
}

/**
 * 获取回测交易记录
 * @param {string} id - 回测ID
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @returns {Promise<Object>} - 交易记录列表
 */
export function getBacktestTrades(id, params) {
  return get(`/backtest/${id}/trades`, params)
}

/**
 * 删除回测
 * @param {string} id - 回测ID
 * @returns {Promise<Object>} - 删除结果
 */
export function deleteBacktest(id) {
  return del(`/backtest/${id}`)
}

/**
 * 停止正在运行的回测
 * @param {string} id - 回测ID
 * @returns {Promise<Object>} - 操作结果
 */
export function stopBacktest(id) {
  return post(`/backtest/${id}/stop`)
}

/**
 * 导出回测结果
 * @param {string} id - 回测ID
 * @param {string} format - 导出格式，如 "csv", "excel", "pdf"
 * @returns {Promise<Blob>} - 导出的文件数据
 */
export function exportBacktestResult(id, format) {
  return get(`/backtest/${id}/export?format=${format}`, {}, { responseType: 'blob' })
}

/**
 * 获取回测对比数据
 * @param {Array} ids - 回测ID数组
 * @returns {Promise<Object>} - 对比数据
 */
export function compareBacktests(ids) {
  return post('/backtest/compare', { ids })
} 