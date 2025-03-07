import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/market-data',
    name: 'MarketData',
    component: () => import('../views/MarketData.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/strategy',
    name: 'Strategy',
    component: () => import('../views/Strategy.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/strategy/:id',
    name: 'StrategyDetail',
    component: () => import('../views/StrategyDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/backtest',
    name: 'Backtest',
    component: () => import('../views/Backtest.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/backtest/:id',
    name: 'BacktestDetail',
    component: () => import('../views/BacktestDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/trading',
    name: 'Trading',
    component: () => import('../views/Trading.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/trading/accounts',
    name: 'TradingAccounts',
    component: () => import('../views/TradingAccounts.vue'),
    meta: { requiresAuth: true }
  }
]
const routerHistory = createWebHistory()
const router = createRouter({
  history: routerHistory,
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    // 如果需要认证但没有token，重定向到登录页
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router 