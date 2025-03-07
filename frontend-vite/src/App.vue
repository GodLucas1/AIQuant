<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'

// 检查是否已登录
const isLoggedIn = ref(!!localStorage.getItem('token'))

// 获取当前路由
const route = useRoute()

// 检查是否是登录或注册页
const isAuthPage = computed(() => {
  return ['Login', 'Register', 'NotFound'].includes(route.name)
})

// 监听登录状态变化
onMounted(() => {
  window.addEventListener('storage', (e) => {
    if (e.key === 'token') {
      isLoggedIn.value = !!e.newValue
    }
  })
})
</script>

<template>
  <div class="app-container">
    <template v-if="!isAuthPage">
      <div class="layout-container">
        <!-- 当用户登录时才显示侧边栏和头部 -->
        <Sidebar v-if="isLoggedIn" />
        <div class="main-content">
          <Header v-if="isLoggedIn" />
          <div class="content">
            <router-view />
          </div>
        </div>
      </div>
    </template>
    <template v-else>
      <!-- 对于登录、注册等页面，直接显示内容 -->
      <router-view />
    </template>
  </div>
</template>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.app-container {
  height: 100vh;
  width: 100%;
  overflow: hidden; /* 防止内容溢出导致页面大小变化 */
  position: fixed; /* 固定页面大小 */
  top: 0;
  left: 0;
}

.layout-container {
  display: flex;
  height: 100%;
  width: 100%;
  overflow: hidden; /* 防止内容溢出 */
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative; /* 确保子元素能够相对于它定位 */
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden; /* 防止水平滚动 */
  background-color: #f5f7fa;
  position: absolute; /* 使内容区域绝对定位 */
  top: 60px; /* 头部高度 */
  left: 0;
  right: 0;
  bottom: 0;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
