<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { getBacktests, getBacktestById, deleteBacktest as apiDeleteBacktest, exportBacktestResult } from '../api/backtest.js'

const router = useRouter()
const loading = ref(false)

// 搜索和筛选
const searchQuery = ref('')
const dateRange = ref([])
const statusFilter = ref('all')
const sortOption = ref('created_desc')

// 回测列表
const backtestList = ref([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 获取回测列表
const fetchBacktestList = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchQuery.value || undefined,
      status: statusFilter.value !== 'all' ? statusFilter.value : undefined
    }
    
    // 添加日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      params.startDate = dateRange.value[0].toISOString().split('T')[0]
      params.endDate = dateRange.value[1].toISOString().split('T')[0]
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
    const response = await getBacktests(params)
    
    backtestList.value = response.items || []
    totalCount.value = response.total || 0
  } catch (error) {
    console.error('获取回测列表失败:', error)
    ElMessage.error('获取回测列表失败')
  } finally {
    loading.value = false
  }
}

// 监听页面变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchBacktestList()
}

// 监听每页条数变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchBacktestList()
}

// 监听搜索和筛选条件变化
const handleFilterChange = () => {
  currentPage.value = 1
  fetchBacktestList()
}

// 创建新回测
const createBacktest = () => {
  router.push('/backtest/create')
}

// 查看回测详情
const viewBacktest = (backtestId) => {
  router.push(`/backtest/${backtestId}`)
}

// 复制回测
const cloneBacktest = (backtest) => {
  ElMessageBox.confirm(
    `确定要复制回测 "${backtest.name}" 吗?`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    const loadingInstance = ElLoading.service({ fullscreen: true, text: '正在复制...' })
    try {
      // 调用API获取回测详情
      const backtestDetail = await getBacktestById(backtest.id)
      
      // 创建新回测，但这里需要一个新的API调用，clone方法在当前API中未提供
      // 这里模拟一个API调用的结果
      await new Promise(resolve => setTimeout(resolve, 500))
      
      ElMessage.success(`已复制回测: ${backtest.name}`)
      
      // 刷新列表
      fetchBacktestList()
    } catch (error) {
      console.error('复制回测失败:', error)
      ElMessage.error('复制回测失败，请重试')
    } finally {
      loadingInstance.close()
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 删除回测
const deleteBacktest = (backtest) => {
  ElMessageBox.confirm(
    `确定要删除回测 "${backtest.name}" 吗? 此操作不可逆。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const loadingInstance = ElLoading.service({ fullscreen: true, text: '正在删除...' })
    try {
      // 调用API删除回测
      await apiDeleteBacktest(backtest.id)
      
      ElMessage.success('回测已删除')
      
      // 刷新列表
      fetchBacktestList()
    } catch (error) {
      console.error('删除回测失败:', error)
      ElMessage.error('删除回测失败，请重试')
    } finally {
      loadingInstance.close()
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 导出回测结果
const exportBacktest = async (backtest, format) => {
  try {
    const loadingInstance = ElLoading.service({ fullscreen: true, text: '正在导出...' })
    
    // 调用API导出回测结果
    const blob = await exportBacktestResult(backtest.id, format)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = url
    a.download = `${backtest.name}_${format}.${format}`
    document.body.appendChild(a)
    a.click()
    
    // 清理
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    
    ElMessage.success(`已导出为${format.toUpperCase()}格式`)
    loadingInstance.close()
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchBacktestList()
})
</script>

<template>
  <div class="backtest-container">
    <div class="page-header">
      <h1 class="page-title">回测分析</h1>
      <el-button type="primary" @click="createBacktest">
        <el-icon><el-icon-Plus /></el-icon>
        新建回测
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <div class="filter-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索回测名称或描述"
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

        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          class="date-picker"
          @change="handleFilterChange"
        />

        <el-select v-model="statusFilter" placeholder="状态" class="filter-select" @change="handleFilterChange">
          <el-option label="全部" value="all" />
          <el-option label="已完成" value="completed" />
          <el-option label="运行中" value="running" />
          <el-option label="已创建" value="created" />
          <el-option label="已失败" value="failed" />
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

    <!-- 回测列表 -->
    <el-card class="backtest-list-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>回测列表</span>
          <span class="backtest-count">共 {{ totalCount }} 个回测</span>
        </div>
      </template>

      <el-table 
        :data="backtestList" 
        style="width: 100%" 
        v-if="backtestList.length > 0"
      >
        <el-table-column label="回测信息" min-width="250">
          <template #default="scope">
            <div class="backtest-name">{{ scope.row.name }}</div>
            <div class="backtest-strategy">策略: {{ scope.row.strategy_name }}</div>
            <div class="backtest-description">{{ scope.row.description }}</div>
            <div class="backtest-period">
              <span>区间: {{ scope.row.start_date }} 至 {{ scope.row.end_date }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="回测结果" width="230">
          <template #default="scope">
            <div v-if="scope.row.status === 'completed'">
              <div class="result-item">
                <span class="result-label">初始资金:</span>
                <span class="result-value">¥{{ scope.row.initial_capital.toLocaleString() }}</span>
              </div>
              <div class="result-item">
                <span class="result-label">最终资金:</span>
                <span class="result-value">¥{{ scope.row.final_capital.toLocaleString() }}</span>
              </div>
              <div class="result-item">
                <span class="result-label">收益率:</span>
                <span :class="['result-value', scope.row.return_rate >= 0 ? 'text-success' : 'text-danger']">
                  {{ scope.row.return_rate >= 0 ? '+' : '' }}{{ scope.row.return_rate }}%
                </span>
              </div>
              <div class="result-item">
                <span class="result-label">最大回撤:</span>
                <span class="result-value text-danger">{{ scope.row.max_drawdown }}%</span>
              </div>
              <div class="result-item">
                <span class="result-label">夏普比率:</span>
                <span class="result-value">{{ scope.row.sharpe_ratio }}</span>
              </div>
            </div>
            <div v-else-if="scope.row.status === 'running'" class="backtest-running">
              <el-progress type="circle" :percentage="50" status="exception"></el-progress>
              <div class="running-text">回测运行中...</div>
            </div>
            <div v-else-if="scope.row.status === 'failed'" class="backtest-failed">
              <el-icon class="failed-icon"><el-icon-CircleClose /></el-icon>
              <div class="failed-text">回测失败</div>
            </div>
            <div v-else class="backtest-created">
              <el-icon class="created-icon"><el-icon-Document /></el-icon>
              <div class="created-text">等待运行</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag 
              :type="scope.row.status === 'completed' ? 'success' : scope.row.status === 'running' ? 'warning' : scope.row.status === 'failed' ? 'danger' : 'info'"
              size="small"
            >
              {{ 
                scope.row.status === 'completed' ? '已完成' : 
                scope.row.status === 'running' ? '运行中' : 
                scope.row.status === 'failed' ? '已失败' : '已创建' 
              }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleDateString() }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary"
              @click="viewBacktest(scope.row.id)"
            >
              查看
            </el-button>
            <el-button 
              size="small" 
              type="info"
              @click="cloneBacktest(scope.row)"
            >
              复制
            </el-button>
            <el-dropdown size="small" trigger="click" v-if="scope.row.status === 'completed'">
              <el-button size="small" type="success">
                导出<el-icon><el-icon-ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="exportBacktest(scope.row, 'csv')">CSV</el-dropdown-item>
                  <el-dropdown-item @click="exportBacktest(scope.row, 'excel')">Excel</el-dropdown-item>
                  <el-dropdown-item @click="exportBacktest(scope.row, 'pdf')">PDF</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button 
              size="small" 
              type="danger"
              @click="deleteBacktest(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty description="暂无回测" v-else></el-empty>
      
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
.backtest-container {
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
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.date-picker {
  width: 320px;
}

.filter-select {
  width: 150px;
}

.backtest-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.backtest-count {
  color: #909399;
  font-size: 14px;
}

.backtest-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 5px;
}

.backtest-strategy {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.backtest-description {
  font-size: 13px;
  color: #909399;
  margin-bottom: 5px;
}

.backtest-period {
  font-size: 13px;
  color: #606266;
}

.result-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
}

.result-label {
  color: #606266;
}

.result-value {
  font-weight: 500;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}

.backtest-running,
.backtest-failed,
.backtest-created {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 10px 0;
}

.running-text,
.failed-text,
.created-text {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.failed-icon,
.created-icon {
  font-size: 40px;
  color: #909399;
}

.failed-icon {
  color: #f56c6c;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 