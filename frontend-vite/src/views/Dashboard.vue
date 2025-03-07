<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getTradingStats } from '../api/trading.js'
import { getPositions } from '../api/trading.js'
import { getTradingTasks } from '../api/trading.js'
import { getStrategies } from '../api/strategy.js'

// 日期范围
const dateRange = ref([
  new Date(new Date().setMonth(new Date().getMonth() - 1)),
  new Date()
])

// 仪表盘数据
const accountValue = ref(0)
const accountTrend = ref(0)
const availableFunds = ref(0)
const positionValue = ref(0)

const dailyProfit = ref(0)
const dailyProfitTrend = ref(0)
const realizedProfit = ref(0)
const unrealizedProfit = ref(0)

const positionsCount = ref(0)
const runningStrategies = ref(0)

// 图表实例
let accountValueChart = null
let strategyComparisonChart = null

// 日期范围变更事件
const handleDateChange = () => {
  fetchDashboardData()
}

// 获取仪表盘数据
const fetchDashboardData = async () => {
  try {
    // 获取交易统计数据
    const params = {
      startTime: dateRange.value[0].getTime(),
      endTime: dateRange.value[1].getTime()
    }
    
    const statsData = await getTradingStats(params)
    
    // 更新仪表盘数据
    accountValue.value = statsData.accountValue || 0
    accountTrend.value = statsData.accountTrend || 0
    availableFunds.value = statsData.availableFunds || 0
    positionValue.value = statsData.positionValue || 0
    
    dailyProfit.value = statsData.dailyProfit || 0
    dailyProfitTrend.value = statsData.dailyProfitTrend || 0
    realizedProfit.value = statsData.realizedProfit || 0
    unrealizedProfit.value = statsData.unrealizedProfit || 0
    
    // 获取持仓数量
    const positionsData = await getPositions({})
    positionsCount.value = positionsData.length || 0
    
    // 获取运行中策略
    const tasksData = await getTradingTasks({ status: 'running' })
    runningStrategies.value = tasksData.length || 0
    
    // 更新图表数据
    updateCharts(statsData)
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    // 通知用户出错
    ElMessage.error('获取数据失败，请稍后重试')
  }
}

// 更新图表数据
const updateCharts = (statsData) => {
  // 更新账户净值图表
  if (accountValueChart) {
    accountValueChart.setOption({
      xAxis: {
        data: statsData.dates || []
      },
      series: [
        {
          data: statsData.accountValues || []
        }
      ]
    })
  }
  
  // 更新策略对比图表
  if (strategyComparisonChart) {
    getStrategies({ limit: 3 }).then(strategies => {
      strategyComparisonChart.setOption({
        legend: {
          data: strategies.map(strategy => strategy.name) || []
        },
        xAxis: {
          data: statsData.dates || []
        },
        series: strategies.map((strategy, index) => ({
          name: strategy.name,
          type: 'line',
          data: statsData.strategyReturns?.[index] || []
        }))
      })
    }).catch(error => {
      console.error('获取策略数据失败:', error)
    })
  }
}

// 初始化图表
const initCharts = () => {
  // 账户净值图表
  accountValueChart = echarts.init(document.getElementById('accountValueChart'))
  accountValueChart.setOption({
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
      data: []
    },
    yAxis: {
      type: 'value',
      name: '账户净值',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '账户净值',
        type: 'line',
        smooth: true,
        data: [],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(58, 77, 233, 0.8)' },
            { offset: 1, color: 'rgba(58, 77, 233, 0.1)' }
          ])
        },
        markPoint: {
          data: [
            { type: 'max', name: '最高值' },
            { type: 'min', name: '最低值' }
          ]
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
  
  // 策略对比图表
  strategyComparisonChart = echarts.init(document.getElementById('strategyComparisonChart'))
  strategyComparisonChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: [],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: []
    },
    yAxis: {
      type: 'value',
      name: '收益率',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: []
  })
  
  // 窗口大小变化时重新调整图表
  window.addEventListener('resize', () => {
    accountValueChart.resize()
    strategyComparisonChart.resize()
  })
}

// 组件挂载后初始化图表并获取数据
onMounted(() => {
  // 为了确保DOM已渲染，延迟初始化图表
  setTimeout(() => {
    initCharts()
    fetchDashboardData()
  }, 100)
})
</script>

<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1 class="page-title">量化交易平台 - 仪表盘</h1>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        @change="handleDateChange"
      />
    </div>
    
    <!-- 概览卡片 -->
    <div class="dashboard-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-title">账户总资产</div>
            <div class="card-value">¥ {{ accountValue.toLocaleString() }}</div>
            <div class="card-trend" :class="accountTrend > 0 ? 'trend-up' : 'trend-down'">
              {{ accountTrend > 0 ? '+' : '' }}{{ accountTrend }}%
            </div>
            <div class="card-details">
              <div class="detail-item">
                <span class="label">可用资金：</span>
                <span class="value">¥ {{ availableFunds.toLocaleString() }}</span>
              </div>
              <div class="detail-item">
                <span class="label">持仓市值：</span>
                <span class="value">¥ {{ positionValue.toLocaleString() }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-title">当日盈亏</div>
            <div class="card-value" :class="dailyProfit > 0 ? 'profit' : 'loss'">
              ¥ {{ dailyProfit.toLocaleString() }}
            </div>
            <div class="card-trend" :class="dailyProfitTrend > 0 ? 'trend-up' : 'trend-down'">
              {{ dailyProfitTrend > 0 ? '+' : '' }}{{ dailyProfitTrend }}%
            </div>
            <div class="profit-breakdown">
              <div class="detail-item">
                <span class="label">已实现：</span>
                <span class="value profit">¥ {{ realizedProfit.toLocaleString() }}</span>
              </div>
              <div class="detail-item">
                <span class="label">未实现：</span>
                <span class="value">¥ {{ unrealizedProfit.toLocaleString() }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-title">持仓数量</div>
            <div class="card-value">{{ positionsCount }}</div>
            <div class="card-tag">
              <el-tag v-if="positionsCount > 0" size="small" type="success">{{ positionsCount }}个品种</el-tag>
              <el-tag v-else size="small" type="info">无持仓</el-tag>
            </div>
            <el-button size="small" type="primary" class="action-button" @click="$router.push('/trading/positions')">查看持仓</el-button>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-title">运行中策略</div>
            <div class="card-value">{{ runningStrategies }}</div>
            <div class="card-tag">
              <el-tag size="small" type="primary">自动交易中</el-tag>
            </div>
            <el-button size="small" type="success" class="action-button" @click="$router.push('/trading/tasks')">管理策略</el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 图表区域 -->
    <div class="dashboard-charts">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" class="chart-card">
            <div class="card-title">账户净值走势</div>
            <div id="accountValueChart" class="chart-container"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card shadow="hover" class="chart-card">
            <div class="card-title">策略收益对比</div>
            <div id="strategyComparisonChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 22px;
  font-weight: 500;
}

.dashboard-overview {
  margin-bottom: 20px;
}

.dashboard-charts {
  margin-bottom: 20px;
}

.card-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.card-value {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 5px;
}

.profit {
  color: #67c23a;
}

.loss {
  color: #f56c6c;
}

.card-trend {
  font-size: 14px;
  margin-bottom: 10px;
}

.trend-up {
  color: #67c23a;
}

.trend-down {
  color: #f56c6c;
}

.card-details, .profit-breakdown {
  margin-top: 10px;
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 13px;
}

.detail-item .label {
  color: #909399;
}

.card-tag {
  margin: 10px 0;
}

.action-button {
  width: 100%;
  margin-top: 10px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 350px;
}
</style> 