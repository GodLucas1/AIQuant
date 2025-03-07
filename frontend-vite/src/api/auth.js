import { get, post, put } from '../utils/request'

/**
 * 用户登录
 * @param {Object} data - 登录信息
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @returns {Promise<Object>} - 登录结果
 */
export function login(data) {
  return post('/auth/login', data)
}

/**
 * 用户注册
 * @param {Object} data - 注册信息
 * @param {string} data.username - 用户名
 * @param {string} data.email - 邮箱
 * @param {string} data.password - 密码
 * @returns {Promise<Object>} - 注册结果
 */
export function register(data) {
  return post('/auth/register', data)
}

/**
 * 获取用户个人资料
 * @returns {Promise<Object>} - 用户资料
 */
export function getProfile() {
  return get('/auth/profile')
}

/**
 * 更新用户个人资料
 * @param {Object} data - 更新的用户资料
 * @returns {Promise<Object>} - 更新结果
 */
export function updateProfile(data) {
  return put('/auth/profile', data)
} 