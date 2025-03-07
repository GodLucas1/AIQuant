<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as authApi from '../api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const username = ref('用户')
const userAvatar = ref('')
const notificationCount = ref(0)

// 计算页面标题
const pageTitle = computed(() => {
  const routeName = route.name
  const titleMap = {
    'Dashboard': '仪表盘',
    'MarketData': '市场数据',
    'Strategy': '策略管理',
    'StrategyDetail': '策略详情',
    'Backtest': '回测分析',
    'BacktestDetail': '回测详情',
    'Trading': '交易中心',
    'TradingAccounts': '账户管理',
    'TradingTasks': '自动交易',
    'Profile': '个人信息'
  }
  return titleMap[routeName] || '量化交易平台'
})

// 计算用户名缩写
const userInitials = computed(() => {
  if (username.value) {
    return username.value.substring(0, 1).toUpperCase()
  }
  return 'U'
})

// 获取用户信息
const fetchUserProfile = async () => {
  try {
    const response = await authApi.getProfile()
    username.value = response.username
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 处理下拉菜单命令
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      logout()
      break
  }
}

// 退出登录
const logout = () => {
  localStorage.removeItem('token')
  ElMessage.success('已成功退出登录')
  router.push('/login')
}

// 组件挂载时获取用户信息
onMounted(fetchUserProfile)
</script>

<template>
  <header class="header">
    <div class="flex-row align-center">
      <h2 class="page-title">{{ pageTitle }}</h2>
    </div>
    
    <div class="flex-row align-center gap-20">
      <!-- 通知图标 -->
      <el-badge :value="notificationCount" class="notification-badge" v-if="notificationCount > 0">
        <el-button circle>
          <el-icon><el-icon-Bell /></el-icon>
        </el-button>
      </el-badge>
      <el-button v-else circle>
        <el-icon><el-icon-Bell /></el-icon>
      </el-button>
      
      <!-- 用户菜单 -->
      <el-dropdown @command="handleCommand" trigger="click">
        <div class="user-info flex-row align-center gap-10">
          <el-avatar size="small" :src="userAvatar">{{ userInitials }}</el-avatar>
          <span>{{ username }}</span>
          <el-icon><el-icon-ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人信息</el-dropdown-item>
            <el-dropdown-item command="settings">设置</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<style scoped>
.header {
  height: 60px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: relative;
  z-index: 10;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.user-info {
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.flex-row {
  display: flex;
  flex-direction: row;
}

.align-center {
  align-items: center;
}

.gap-10 {
  gap: 10px;
}

.gap-20 {
  gap: 20px;
}
</style> 