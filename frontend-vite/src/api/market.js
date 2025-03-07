import { get } from '../utils/request'

/**
 * 获取市场行情数据
 * @param {Object} params - 查询参数
 * @param {string} params.symbol - 交易对符号，如 "BTC/USDT"
 * @param {string} params.exchange - 交易所，如 "binance"
 * @param {string} params.interval - 时间间隔，如 "1m", "5m", "1h", "1d"
 * @param {number} params.limit - 返回数据条数
 * @param {number} params.from - 开始时间戳
 * @param {number} params.to - 结束时间戳
 * @returns {Promise<Object>} - 市场行情数据
 */
export function getMarketData(params) {
  return get('/market/klines', params)
}

/**
 * 获取交易对列表
 * @param {Object} params - 查询参数
 * @param {string} params.exchange - 交易所名称
 * @returns {Promise<Array>} - 交易对列表
 */
export function getSymbols(params) {
  return get('/market/symbols', params)
}

/**
 * 获取交易所列表
 * @returns {Promise<Array>} - 交易所列表
 */
export function getExchanges() {
  return get('/market/exchanges')
}

/**
 * 获取市场深度数据
 * @param {Object} params - 查询参数
 * @param {string} params.symbol - 交易对
 * @param {string} params.exchange - 交易所
 * @param {number} params.limit - 返回数据深度
 * @returns {Promise<Object>} - 深度数据，包含bids和asks
 */
export function getDepth(params) {
  return get('/market/depth', params)
}

/**
 * 获取最近成交记录
 * @param {Object} params - 查询参数
 * @param {string} params.symbol - 交易对
 * @param {string} params.exchange - 交易所
 * @param {number} params.limit - 返回数据条数
 * @returns {Promise<Array>} - 成交记录列表
 */
export function getTrades(params) {
  return get('/market/trades', params)
} 