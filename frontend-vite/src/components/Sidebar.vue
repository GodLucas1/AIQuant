<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 是否折叠侧边栏
const isCollapsed = ref(false)

// 根据当前路由路径计算活动菜单
const activeMenu = computed(() => {
  return route.path
})

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <div :class="['sidebar', isCollapsed ? 'sidebar-collapsed' : '']">
    <div class="logo-container">
      <img v-if="isCollapsed" src="/small-logo.png" alt="Logo" class="logo-small">
      <img v-else src="/logo.png" alt="Logo" class="logo">
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapsed"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      unique-opened
      router
    >
      <el-sub-menu index="/dashboard">
        <template #title>
          <el-icon><el-icon-Monitor /></el-icon>
          <span>仪表盘</span>
        </template>
        <el-menu-item index="/dashboard">概览</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="/market-data">
        <template #title>
          <el-icon><el-icon-DataLine /></el-icon>
          <span>市场数据</span>
        </template>
        <el-menu-item index="/market-data">行情查询</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="/strategy">
        <template #title>
          <el-icon><el-icon-SetUp /></el-icon>
          <span>策略管理</span>
        </template>
        <el-menu-item index="/strategy">我的策略</el-menu-item>
        <el-menu-item index="/strategy/create">创建策略</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="/backtest">
        <template #title>
          <el-icon><el-icon-PieChart /></el-icon>
          <span>回测分析</span>
        </template>
        <el-menu-item index="/backtest">回测列表</el-menu-item>
        <el-menu-item index="/backtest/create">新建回测</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="/trading">
        <template #title>
          <el-icon><el-icon-TrendCharts /></el-icon>
          <span>交易中心</span>
        </template>
        <el-menu-item index="/trading">交易概览</el-menu-item>
        <el-menu-item index="/trading/accounts">账户管理</el-menu-item>
        <el-menu-item index="/trading/tasks">自动交易</el-menu-item>
        <el-menu-item index="/trading/orders">订单管理</el-menu-item>
        <el-menu-item index="/trading/positions">持仓查询</el-menu-item>
      </el-sub-menu>
    </el-menu>
    
    <div class="sidebar-footer">
      <el-button type="text" @click="toggleCollapse">
        <el-icon v-if="isCollapsed"><el-icon-ArrowRight /></el-icon>
        <el-icon v-else><el-icon-ArrowLeft /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  width: 250px;
  height: 100%;
  background-color: #304156;
  color: #fff;
  transition: width 0.3s;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-collapsed {
  width: 64px;
}

.logo-container {
  height: 60px;
  padding: 10px 0;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

.logo {
  height: 40px;
}

.logo-small {
  height: 32px;
}

.sidebar-footer {
  margin-top: auto;
  padding: 10px;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu--collapse) {
  width: 64px;
}

/* 修复子菜单缩进问题 */
:deep(.el-menu-item) {
  padding-left: 48px !important;
}

:deep(.el-sub-menu .el-sub-menu__title) {
  padding-left: 20px !important;
}

:deep(.el-sub-menu .el-menu--inline .el-menu-item) {
  min-width: 200px;
}
</style> 