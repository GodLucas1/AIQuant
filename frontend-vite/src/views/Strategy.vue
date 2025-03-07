<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { getStrategies, deleteStrategy as apiDeleteStrategy, updateStrategy, getStrategyTemplates as apiGetTemplates } from '../api/strategy.js'

const router = useRouter()

// 策略列表
const strategies = ref([])
const loading = ref(false)
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 策略模板选项
const strategyTemplates = ref([])

// 搜索和筛选
const searchQuery = ref('')
const statusFilter = ref('all')
const sortOption = ref('created_desc')

// 获取策略列表
const fetchStrategies = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchQuery.value || undefined,
      status: statusFilter.value !== 'all' ? statusFilter.value : undefined
    }
    
    // 设置排序
    switch (sortOption.value) {
      case 'name_asc':
        params.sort = 'name'
        params.order = 'asc'
        break
      case 'name_desc':
        params.sort = 'name'
        params.order = 'desc'
        break
      case 'return_asc':
        params.sort = 'return_rate'
        params.order = 'asc'
        break
      case 'return_desc':
        params.sort = 'return_rate'
        params.order = 'desc'
        break
      case 'created_asc':
        params.sort = 'created_at'
        params.order = 'asc'
        break
      case 'created_desc':
        params.sort = 'created_at'
        params.order = 'desc'
        break
    }
    
    // 调用API获取数据
    const response = await getStrategies(params)
    strategies.value = response.strategies || []
    totalCount.value = response.strategies.length || 0
  } catch (error) {
    console.error('获取策略列表失败:', error)
    ElMessage.error('获取策略列表失败，请重试')
  } finally {
    loading.value = false
  }
}

// 获取策略模板
const fetchStrategyTemplates = async () => {
  try {
    const templates = await apiGetTemplates()
    strategyTemplates.value = templates.map(template => ({
      value: template.id,
      label: template.name
    }))
  } catch (error) {
    console.error('获取策略模板失败:', error)
  }
}

// 监听页面变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchStrategies()
}

// 监听每页条数变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchStrategies()
}

// 监听搜索和筛选条件变化
const handleFilterChange = () => {
  currentPage.value = 1
  fetchStrategies()
}

// 创建新策略
const createStrategy = () => {
  router.push('/strategy/create')
}

// 查看策略详情
const viewStrategy = (strategyId) => {
  router.push(`/strategy/${strategyId}`)
}

// 启用/禁用策略
const toggleStrategyStatus = (strategy) => {
  const newStatus = strategy.status === 'active' ? 'inactive' : 'active'
  const actionText = newStatus === 'active' ? '启用' : '停用'
  
  ElMessageBox.confirm(
    `确定要${actionText}策略 "${strategy.name}" 吗?`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const loadingInstance = ElLoading.service({ fullscreen: true, text: '正在处理...' })
    try {
      // 调用API更新策略
      await updateStrategy(strategy.id, { status: newStatus })
      
      // 更新本地数据
      const index = strategies.value.findIndex(s => s.id === strategy.id)
      if (index !== -1) {
        strategies.value[index].status = newStatus
      }
      ElMessage.success(`策略已${actionText}`)
    } catch (error) {
      console.error(`${actionText}策略失败:`, error)
      ElMessage.error(`${actionText}策略失败，请重试`)
    } finally {
      loadingInstance.close()
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 删除策略
const deleteStrategy = (strategy) => {
  ElMessageBox.confirm(
    `确定要删除策略 "${strategy.name}" 吗? 此操作不可逆。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'danger'
    }
  ).then(async () => {
    const loadingInstance = ElLoading.service({ fullscreen: true, text: '正在删除...' })
    try {
      // 调用API删除策略
      await apiDeleteStrategy(strategy.id)
      
      // 更新本地数据
      strategies.value = strategies.value.filter(s => s.id !== strategy.id)
      totalCount.value--
      ElMessage.success('策略已删除')
    } catch (error) {
      console.error('删除策略失败:', error)
      ElMessage.error('删除策略失败，请重试')
    } finally {
      loadingInstance.close()
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 组件挂载时获取数据
onMounted(() => {
  fetchStrategies()
  fetchStrategyTemplates()
})
</script>

<template>
  <div class="strategy-container">
    <div class="page-header">
      <h1 class="page-title">策略管理</h1>
      <el-button type="primary" @click="createStrategy">
        <el-icon><el-icon-Plus /></el-icon>
        创建策略
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <div class="filter-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索策略名称或描述"
          class="search-input"
          clearable
          @clear="handleFilterChange"
          @keyup.enter="handleFilterChange"
        >
          <template #prefix>
            <el-icon><el-icon-Search /></el-icon>
          </template>
          <template #append>
            <el-button @click="handleFilterChange">搜索</el-button>
          </template>
        </el-input>

        <el-select v-model="statusFilter" placeholder="状态" class="filter-select" @change="handleFilterChange">
          <el-option label="全部" value="all" />
          <el-option label="已启用" value="active" />
          <el-option label="已停用" value="inactive" />
        </el-select>

        <el-select v-model="sortOption" placeholder="排序" class="filter-select" @change="handleFilterChange">
          <el-option label="创建时间 (新→旧)" value="created_desc" />
          <el-option label="创建时间 (旧→新)" value="created_asc" />
          <el-option label="名称 (A→Z)" value="name_asc" />
          <el-option label="名称 (Z→A)" value="name_desc" />
          <el-option label="收益率 (高→低)" value="return_desc" />
          <el-option label="收益率 (低→高)" value="return_asc" />
        </el-select>
      </div>
    </el-card>

    <!-- 策略列表 -->
    <el-card class="strategy-list-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>我的策略</span>
          <span class="strategy-count">共 {{ totalCount }} 个策略</span>
        </div>
      </template>

      <el-table 
        :data="strategies" 
        style="width: 100%" 
        v-if="strategies.length > 0"
      >
        <el-table-column prop="name" label="策略名称" min-width="180">
          <template #default="scope">
            <div class="strategy-name-cell">
              <span class="strategy-name">{{ scope.row.name }}</span>
              <el-tag 
                size="small" 
                type="info" 
                v-if="scope.row.is_public"
              >公开</el-tag>
            </div>
            <div class="strategy-description">{{ scope.row.description }}</div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag 
              :type="scope.row.status === 'active' ? 'success' : 'info'"
              size="small"
            >
              {{ scope.row.status === 'active' ? '已启用' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="return_rate" label="收益率" width="120">
          <template #default="scope">
            <span :class="scope.row.return_rate >= 0 ? 'text-success' : 'text-danger'">
              {{ scope.row.return_rate >= 0 ? '+' : '' }}{{ scope.row.return_rate }}%
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleDateString() }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              @click="viewStrategy(scope.row.id)"
            >
              查看
            </el-button>
            <el-button 
              size="small" 
              :type="scope.row.status === 'active' ? 'warning' : 'success'"
              @click="toggleStrategyStatus(scope.row)"
            >
              {{ scope.row.status === 'active' ? '停用' : '启用' }}
            </el-button>
            <el-button 
              size="small" 
              type="danger"
              @click="deleteStrategy(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty description="暂无策略" v-else></el-empty>
      
      <!-- 分页 -->
      <div class="pagination-container" v-if="totalCount > 0">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalCount"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :current-page="currentPage"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.strategy-container {
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

.filter-card {
  margin-bottom: 20px;
}

.filter-container {
  display: flex;
  gap: 15px;
}

.search-input {
  flex: 1;
}

.filter-select {
  width: 150px;
}

.strategy-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strategy-count {
  color: #909399;
  font-size: 14px;
}

.strategy-name-cell {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.strategy-name {
  font-weight: 500;
  margin-right: 8px;
}

.strategy-description {
  color: #606266;
  font-size: 13px;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 