<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)
const registerFormRef = ref(null)

// 表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度应为3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度应为6-20个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      // 移除确认密码字段，后端不需要
      const registerData = {
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password
      }
      
      await register(registerData)
      
      ElMessage.success('注册成功，请登录')
      
      // 跳转到登录页
      router.push('/login')
    } catch (error) {
      console.error('注册失败:', error)
      ElMessage.error(error.response?.data?.error || '注册失败，请稍后重试')
    } finally {
      loading.value = false
    }
  })
}
</script>

<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <img src="/logo.png" alt="AIQuant Logo" class="register-logo">
        <h2 class="register-title">AIQuant量化交易平台</h2>
      </div>
      
      <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名">
            <template #prefix>
              <el-icon><el-icon-User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱">
            <template #prefix>
              <el-icon><el-icon-Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码"
          >
            <template #prefix>
              <el-icon><el-icon-Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            @keyup.enter="handleRegister"
          >
            <template #prefix>
              <el-icon><el-icon-Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-button 
          type="primary" 
          class="register-button" 
          :loading="loading" 
          @click="handleRegister"
        >
          注册
        </el-button>
        
        <div class="login-link">
          已有账号？ <router-link to="/login">立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.register-box {
  width: 400px;
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-logo {
  height: 60px;
  margin-bottom: 15px;
}

.register-title {
  margin: 0;
  font-size: 22px;
  color: #303133;
  font-weight: 600;
}

.register-button {
  width: 100%;
  margin-bottom: 20px;
}

.login-link {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.login-link a {
  color: #409eff;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style> 