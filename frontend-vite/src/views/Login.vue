<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loginForm = reactive({
  username: '',
  password: ''
})
const rememberMe = ref(false)
const loading = ref(false)
const loginFormRef = ref(null)

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度应为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度应为6-20个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      const response = await login(loginForm)
      
      // 保存token到本地存储
      localStorage.setItem('token', response.access_token)
      
      // 如果勾选了记住我，保存用户名
      if (rememberMe.value) {
        localStorage.setItem('rememberedUsername', loginForm.username)
      } else {
        localStorage.removeItem('rememberedUsername')
      }
      
      ElMessage.success('登录成功')
      
      // 跳转到仪表盘
      router.push('/dashboard')
    } catch (error) {
      console.error('登录失败:', error)
      ElMessage.error(error.response?.data?.error || '登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  })
}

// 在组件加载时检查是否有保存的用户名
const rememberedUsername = localStorage.getItem('rememberedUsername')
if (rememberedUsername) {
  loginForm.username = rememberedUsername
  rememberMe.value = true
}
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img src="/logo.png" alt="AIQuant Logo" class="login-logo">
        <h2 class="login-title">AIQuant量化交易平台</h2>
      </div>
      
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名">
            <template #prefix>
              <el-icon><el-icon-User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码" 
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon><el-icon-Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <div class="login-options">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <el-button type="text">忘记密码？</el-button>
        </div>
        
        <el-button 
          type="primary" 
          class="login-button" 
          :loading="loading" 
          @click="handleLogin"
        >
          登录
        </el-button>
        
        <div class="register-link">
          还没有账号？ <router-link to="/register">立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.login-box {
  width: 400px;
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-logo {
  height: 60px;
  margin-bottom: 15px;
}

.login-title {
  margin: 0;
  font-size: 22px;
  color: #303133;
  font-weight: 600;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  margin-bottom: 20px;
}

.register-link {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.register-link a {
  color: #409eff;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style> 