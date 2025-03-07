import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const accounts = ref([])

// 账户数据
const fetchAccounts = async () => {
  loading.value = true
  try {
    // 模拟API请求延迟
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 模拟数据
    accounts.value = [
      {
        id: 1,
        name: '主账户',
        type: 'stock',
        broker: '智能量化',
        status: 'active',
        balance: 100000,
        profit_loss: 5280,
        profit_loss_percentage: 5.28,
        created_at: '2023-04-01'
      },
      {
        id: 2,
        name: '美股账户',
        type: 'stock',
        broker: '智能量化',
        status: 'active',
        balance: 50000,
        profit_loss: 1250,
        profit_loss_percentage: 2.5,
        created_at: '2023-04-15'
      },
      {
        id: 3,
        name: '期货账户',
        type: 'futures',
        broker: '智能量化',
        status: 'inactive',
        balance: 30000,
        profit_loss: 0,
        profit_loss_percentage: 0,
        created_at: '2023-04-20'
      }
    ]
  } catch (error) {
    console.error('获取账户数据失败:', error)
    ElMessage.error('获取账户数据失败')
  } finally {
    loading.value = false
  }
}

// 创建新账户
const createAccount = () => {
  router.push('/trading/accounts/create')
}

// 编辑账户
const editAccount = (accountId) => {
  router.push(`/trading/accounts/${accountId}/edit`)
}

// 查看账户详情
const viewAccountDetail = (accountId) => {
  router.push(`/trading/accounts/${accountId}`)
}

// 删除账户
const deleteAccount = (accountId) => {
  ElMessageBox.confirm('确定要删除该账户吗？账户下的所有资产和交易记录将被删除', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 模拟API请求
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 更新本地数据
      accounts.value = accounts.value.filter(account => account.id !== accountId)
      
      ElMessage.success('账户删除成功')
    } catch (error) {
      console.error('删除账户失败:', error)
      ElMessage.error('删除账户失败')
    }
  }).catch(() => {
    // 用户取消删除操作
  })
}

// 切换账户状态
const toggleAccountStatus = async (account) => {
  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 更新本地数据
    account.status = account.status === 'active' ? 'inactive' : 'active'
    
    ElMessage.success(`账户状态已更新为${account.status === 'active' ? '启用' : '禁用'}`)
  } catch (error) {
    console.error('更新账户状态失败:', error)
    ElMessage.error('更新账户状态失败')
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchAccounts()
})
</script>

<template>
  <div class="trading-accounts-container">
    <div class="page-header">
      <h1 class="page-title">交易账户管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="createAccount">
          <el-icon><el-icon-Plus /></el-icon>
          创建新账户
        </el-button>
      </div>
    </div>
    
    <el-card v-loading="loading">
      <el-table :data="accounts" style="width: 100%">
        <el-table-column prop="name" label="账户名称" min-width="150"></el-table-column>
        <el-table-column prop="type" label="账户类型" width="120">
          <template #default="scope">
            <el-tag>
              {{ 
                scope.row.type === 'stock' ? '股票账户' : 
                scope.row.type === 'futures' ? '期货账户' : 
                scope.row.type === 'crypto' ? '加密货币' : 
                scope.row.type 
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="broker" label="券商" width="120"></el-table-column>
        <el-table-column prop="balance" label="账户余额" width="150" align="right">
          <template #default="scope">
            ¥ {{ scope.row.balance.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="profit_loss" label="盈亏" width="150" align="right">
          <template #default="scope">
            <span :class="scope.row.profit_loss >= 0 ? 'success' : 'danger'">
              {{ scope.row.profit_loss >= 0 ? '+' : '' }}¥ {{ scope.row.profit_loss.toLocaleString() }} 
              ({{ scope.row.profit_loss_percentage }}%)
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'" size="small">
              {{ scope.row.status === 'active' ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="120"></el-table-column>
        <el-table-column label="操作" width="250" align="right">
          <template #default="scope">
            <el-button 
              size="small" 
              :type="scope.row.status === 'active' ? 'warning' : 'success'"
              @click="toggleAccountStatus(scope.row)"
            >
              {{ scope.row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              size="small" 
              type="primary"
              @click="viewAccountDetail(scope.row.id)"
            >
              详情
            </el-button>
            <el-button 
              size="small"
              @click="editAccount(scope.row.id)"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger"
              @click="deleteAccount(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.trading-accounts-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.success {
  color: #67C23A;
}

.danger {
  color: #F56C6C;
}
</style>