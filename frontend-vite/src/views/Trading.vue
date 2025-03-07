<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import * as echarts from 'echarts'
import { getAccounts, getAccountBalance, getPositions, getOrders, getTradingTasks, getTradingStats } from '../api/trading.js'

const router = useRouter()
const loading = ref(true)

// 账户概览数据
const accountSummary = reactive({
  total_balance: 0,
  available_funds: 0,
  margin_used: 0,
  total_profit_loss: 0,
  daily_profit_loss: 0,
  total_assets: 0,
  open_positions: 0,
  pending_orders: 0
})

// 持仓数据
const positions = ref([])

// 最近订单
const recentOrders = ref([])

// 运行中的策略任务
const runningTasks = ref([])

// 账户列表
const accounts = ref([])
const selectedAccountId = ref(null)

// 图表实例
let accountValueChart = null
let assetAllocationChart = null

// 获取账户列表
const fetchAccounts = async () => {
  try {
    const data = await getAccounts()
    accounts.value = data || []
    
    if (accounts.value.length > 0) {
      selectedAccountId.value = accounts.value[0].id
      await fetchAccountData(selectedAccountId.value)
    }
  } catch (error) {
    console.error('获取账户列表失败:', error)
    ElMessage.error('获取账户列表失败')
  }
}

// 获取账户数据
const fetchAccountData = async (accountId) => {
  if (!accountId) return
  
  loading.value = true
  const loadingInstance = ElLoading.service({ fullscreen: true, text: '加载数据中...' })
  
  try {
    // 1. 获取账户余额
    const balanceData = await getAccountBalance(accountId)
    
    // 更新账户概览数据
    Object.assign(accountSummary, {
      total_balance: balanceData.total_balance || 0,
      available_funds: balanceData.available_funds || 0,
      margin_used: balanceData.margin_used || 0,
      total_profit_loss: balanceData.total_profit_loss || 0,
      daily_profit_loss: balanceData.daily_profit_loss || 0
    })
    
    // 2. 获取持仓列表
    const positionsData = await getPositions({ accountId })
    positions.value = positionsData || []
    accountSummary.open_positions = positions.value.length
    
    // 3. 获取最近订单
    const ordersData = await getOrders({ 
      accountId,
      limit: 5,
      sort: 'created_at',
      order: 'desc'
    })
    recentOrders.value = ordersData.items || []
    accountSummary.pending_orders = recentOrders.value.filter(order => order.status === 'pending').length
    
    // 4. 获取运行中的任务
    const tasksData = await getTradingTasks({
      accountId,
      status: 'running'
    })
    runningTasks.value = tasksData || []
    
    // 5. 获取交易统计数据和图表数据
    const statsData = await getTradingStats({
      accountId,
      startTime: new Date(new Date().setMonth(new Date().getMonth() - 1)).getTime(),
      endTime: new Date().getTime()
    })
    
    // 初始化图表
    setTimeout(() => {
      initCharts(statsData)
    }, 100)
  } catch (error) {
    console.error('获取交易数据失败:', error)
    ElMessage.error('获取交易数据失败，请重试')
  } finally {
    loading.value = false
    loadingInstance.close()
  }
}

// 计算持仓总盈亏
const totalPositionProfitLoss = computed(() => {
  return positions.value.reduce((sum, position) => sum + position.profit_loss, 0)
})

// 计算总持仓市值
const totalPositionValue = computed(() => {
  return positions.value.reduce((sum, position) => sum + position.market_value, 0)
})

// 切换账户
const handleAccountChange = () => {
  fetchAccountData(selectedAccountId.value)
}

// 下单
const placeOrder = () => {
  router.push('/trading/orders/create')
}

// 查看账户
const viewAccounts = () => {
  router.push('/trading/accounts')
}

// 查看任务
const viewTasks = () => {
  router.push('/trading/tasks')
}

// 查看订单
const viewOrders = () => {
  router.push('/trading/orders')
}

// 查看持仓
const viewPositions = () => {
  router.push('/trading/positions')
}

// 初始化图表
const initCharts = (statsData) => {
  // 1. 初始化账户价值图表
  initAccountValueChart(statsData)
  
  // 2. 初始化资产分配图表
  initAssetAllocationChart(statsData)
}

// 初始化账户价值图表
const initAccountValueChart = (statsData) => {
  if (accountValueChart) {
    accountValueChart.dispose()
  }
  
  accountValueChart = echarts.init(document.getElementById('account-value-chart'))
  
  // 使用从API获取的数据
  const dates = statsData?.dates || []
  const values = statsData?.accountValues || []
  
  accountValueChart.setOption({
    title: {
      text: '账户价值走势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>{a}: ¥{c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '账户价值',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '账户价值',
        type: 'line',
        data: values,
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(58, 77, 233, 0.8)' },
            { offset: 1, color: 'rgba(58, 77, 233, 0.1)' }
          ])
        },
        itemStyle: {
          color: '#3a4de9'
        },
        lineStyle: {
          width: 3
        }
      }
    ]
  })
  
  // 调整窗口大小时重新绘制图表
  window.addEventListener('resize', () => {
    accountValueChart.resize()
  })
}

// 初始化资产分配图表
const initAssetAllocationChart = (statsData) => {
  if (assetAllocationChart) {
    assetAllocationChart.dispose()
  }
  
  assetAllocationChart = echarts.init(document.getElementById('asset-allocation-chart'))
  
  // 使用从API获取的数据
  const assetData = statsData?.assetAllocation || []
  
  assetAllocationChart.setOption({
    title: {
      text: '资产分配',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        name: '资产分配',
        type: 'pie',
        radius: '70%',
        center: ['60%', '50%'],
        data: assetData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: false
        }
      }
    ]
  })
  
  // 调整窗口大小时重新绘制图表
  window.addEventListener('resize', () => {
    assetAllocationChart.resize()
  })
}

// 组件挂载时获取数据
onMounted(() => {
  fetchAccounts()
})
</script>

<template>
  <div class="trading-container" v-loading="loading">
    <div class="page-header">
      <h1 class="page-title">交易中心</h1>
      <div class="header-actions">
        <el-select 
          v-model="selectedAccountId" 
          placeholder="选择账户" 
          class="account-select"
          @change="handleAccountChange"
        >
          <el-option 
            v-for="account in accounts" 
            :key="account.id" 
            :label="account.name" 
            :value="account.id"
          />
        </el-select>
        <el-button type="primary" @click="placeOrder">
          <el-icon><el-icon-Plus /></el-icon>
          新建订单
        </el-button>
      </div>
    </div>
    
    <!-- 账户概览 -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-title">账户总资产</div>
          <div class="summary-value">¥ {{ accountSummary.total_balance.toLocaleString() }}</div>
          <div class="summary-detail">
            <div class="detail-item">
              <span class="detail-label">可用资金:</span>
              <span class="detail-value">¥ {{ accountSummary.available_funds.toLocaleString() }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">已用保证金:</span>
              <span class="detail-value">¥ {{ accountSummary.margin_used.toLocaleString() }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-title">账户盈亏</div>
          <div class="summary-value" :class="accountSummary.total_profit_loss >= 0 ? 'text-success' : 'text-danger'">
            ¥ {{ accountSummary.total_profit_loss.toLocaleString() }}
          </div>
          <div class="summary-detail">
            <div class="detail-item">
              <span class="detail-label">日内盈亏:</span>
              <span :class="accountSummary.daily_profit_loss >= 0 ? 'text-success' : 'text-danger'">
                ¥ {{ accountSummary.daily_profit_loss.toLocaleString() }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">持仓盈亏:</span>
              <span :class="totalPositionProfitLoss >= 0 ? 'text-success' : 'text-danger'">
                ¥ {{ totalPositionProfitLoss.toLocaleString() }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-title">持仓摘要</div>
          <div class="summary-value">{{ accountSummary.open_positions }} 个持仓</div>
          <div class="summary-detail">
            <div class="detail-item">
              <span class="detail-label">总市值:</span>
              <span class="detail-value">¥ {{ totalPositionValue.toLocaleString() }}</span>
            </div>
            <div class="detail-item">
              <el-button type="text" size="small" class="view-btn" @click="viewPositions">查看全部持仓</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-title">订单摘要</div>
          <div class="summary-value">{{ accountSummary.pending_orders }} 个待成交订单</div>
          <div class="summary-detail">
            <div class="detail-item">
              <span class="detail-label">运行中策略:</span>
              <span class="detail-value">{{ runningTasks.length }}</span>
            </div>
            <div class="detail-item">
              <el-button type="text" size="small" class="view-btn" @click="viewOrders">查看全部订单</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <div id="account-value-chart" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <div id="asset-allocation-chart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 持仓和订单 -->
    <el-row :gutter="20" class="data-row">
      <el-col :span="12">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>当前持仓</span>
              <el-button type="text" @click="viewPositions">查看更多</el-button>
            </div>
          </template>
          
          <el-table :data="positions.slice(0, 5)" style="width: 100%">
            <el-table-column prop="symbol" label="代码" width="100"></el-table-column>
            <el-table-column prop="name" label="名称" width="120"></el-table-column>
            <el-table-column prop="direction" label="方向" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.direction === 'long' ? 'success' : 'danger'" size="small">
                  {{ scope.row.direction === 'long' ? '多' : '空' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="current_price" label="现价"></el-table-column>
            <el-table-column prop="profit_loss" label="盈亏">
              <template #default="scope">
                <span :class="scope.row.profit_loss >= 0 ? 'text-success' : 'text-danger'">
                  {{ scope.row.profit_loss >= 0 ? '+' : '' }}{{ scope.row.profit_loss.toLocaleString() }}
                </span>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="empty-placeholder" v-if="positions.length === 0">
            <el-empty description="暂无持仓" :image-size="100"></el-empty>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>最近订单</span>
              <el-button type="text" @click="viewOrders">查看更多</el-button>
            </div>
          </template>
          
          <el-table :data="recentOrders" style="width: 100%">
            <el-table-column prop="symbol" label="代码" width="100"></el-table-column>
            <el-table-column prop="direction" label="方向" width="80">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.direction === 'buy' ? 'success' : 'danger'"
                  size="small"
                >
                  {{ scope.row.direction === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="80">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.type === 'market' ? 'warning' : 'info'"
                  size="small"
                >
                  {{ scope.row.type === 'market' ? '市价' : '限价' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格"></el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="scope">
                <el-tag 
                  :type="
                    scope.row.status === 'filled' ? 'success' : 
                    scope.row.status === 'pending' ? 'warning' : 
                    scope.row.status === 'canceled' ? 'info' : 'danger'
                  "
                  size="small"
                >
                  {{ 
                    scope.row.status === 'filled' ? '已成交' : 
                    scope.row.status === 'pending' ? '待成交' : 
                    scope.row.status === 'canceled' ? '已取消' : '已失败' 
                  }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="empty-placeholder" v-if="recentOrders.length === 0">
            <el-empty description="暂无订单" :image-size="100"></el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 运行中的策略 -->
    <el-row :gutter="20" class="data-row">
      <el-col :span="24">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>运行中的策略</span>
              <el-button type="text" @click="viewTasks">管理策略</el-button>
            </div>
          </template>
          
          <el-table :data="runningTasks" style="width: 100%">
            <el-table-column prop="name" label="策略名称" min-width="150"></el-table-column>
            <el-table-column prop="account_name" label="账户" width="120"></el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag type="success" size="small" v-if="scope.row.status === 'running'">
                  运行中
                </el-tag>
                <el-tag type="info" size="small" v-else>
                  已暂停
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="100">
              <template #default="scope">
                {{ new Date(scope.row.created_at).toLocaleDateString() }}
              </template>
            </el-table-column>
            <el-table-column prop="last_trade" label="最近交易" width="100">
              <template #default="scope">
                {{ scope.row.last_trade ? new Date(scope.row.last_trade).toLocaleDateString() : '无' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" @click="router.push(`/trading/tasks/${scope.row.id}`)">查看</el-button>
                <el-button size="small" type="warning" v-if="scope.row.status === 'running'">暂停</el-button>
                <el-button size="small" type="success" v-else>启动</el-button>
                <el-button size="small" type="info">修改</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="empty-placeholder" v-if="runningTasks.length === 0">
            <el-empty description="暂无运行中的策略" :image-size="100">
              <el-button type="primary" @click="router.push('/trading/tasks/create')">创建策略任务</el-button>
            </el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.trading-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.account-select {
  width: 200px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.summary-row,
.charts-row,
.data-row {
  margin-bottom: 20px;
}

.summary-card {
  height: 150px;
  display: flex;
  flex-direction: column;
}

.summary-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.summary-value {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
}

.detail-label {
  color: #909399;
}

.view-btn {
  padding: 0;
  margin-top: 5px;
}

.chart-card {
  height: 350px;
}

.chart-container {
  height: 100%;
  width: 100%;
}

.data-card {
  min-height: 350px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}

.empty-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
</style> 