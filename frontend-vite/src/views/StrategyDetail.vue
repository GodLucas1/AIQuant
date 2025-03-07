<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()
const strategyId = computed(() => route.params.id)
const loading = ref(false)

// 策略数据
const strategy = reactive({
  id: null,
  name: '',
  description: '',
  status: '',
  return_rate: 0,
  created_at: '',
  is_public: false,
  code: '',
  parameters: {},
  backtest_count: 0,
  trade_count: 0,
  last_run: null
})

// 策略绩效数据
const performanceData = ref({
  total_return: 0,
  annual_return: 0, 
  max_drawdown: 0,
  sharpe_ratio: 0,
  volatility: 0,
  win_rate: 0,
  profit_factor: 0,
  avg_profit: 0,
  avg_loss: 0
})

// 策略回测历史
const backtestHistory = ref([
  {
    id: 1,
    start_date: '2022-01-01',
    end_date: '2022-12-31',
    initial_capital: 100000,
    final_capital: 112350,
    return_rate: 12.35,
    status: 'completed',
    created_at: '2023-01-05'
  },
  {
    id: 2,
    start_date: '2022-06-01',
    end_date: '2022-12-31',
    initial_capital: 100000,
    final_capital: 108750,
    return_rate: 8.75,
    status: 'completed',
    created_at: '2023-01-10'
  },
  {
    id: 3,
    start_date: '2023-01-01',
    end_date: '2023-02-28',
    initial_capital: 100000,
    final_capital: 105200,
    return_rate: 5.2,
    status: 'completed',
    created_at: '2023-03-05'
  }
])

// 最近交易记录
const recentTrades = ref([
  { 
    id: 1, 
    date: '2023-04-12', 
    symbol: '000001', 
    name: '平安银行', 
    direction: 'buy', 
    price: 15.23, 
    quantity: 1000, 
    status: 'completed' 
  },
  { 
    id: 2, 
    date: '2023-04-15', 
    symbol: '600036', 
    name: '招商银行', 
    direction: 'buy', 
    price: 38.56, 
    quantity: 500, 
    status: 'completed' 
  },
  { 
    id: 3, 
    date: '2023-04-20', 
    symbol: '000001', 
    name: '平安银行', 
    direction: 'sell', 
    price: 16.08, 
    quantity: 1000, 
    status: 'completed' 
  },
  { 
    id: 4, 
    date: '2023-04-28', 
    symbol: '600036', 
    name: '招商银行', 
    direction: 'sell', 
    price: 40.32, 
    quantity: 500, 
    status: 'completed' 
  }
])

// 获取策略详情
const fetchStrategyDetail = async () => {
  loading.value = true
  try {
    // 实际项目中应该调用API
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟数据
    Object.assign(strategy, {
      id: strategyId.value,
      name: '均线突破策略',
      description: '基于短期和长期移动平均线交叉信号的趋势跟踪策略。当短期移动平均线从下方穿过长期移动平均线时产生买入信号，反之产生卖出信号。',
      status: 'active',
      return_rate: 8.5,
      created_at: '2023-01-15',
      is_public: true,
      code: `
def initialize(context):
    context.stocks = ['000001.XSHE', '600036.XSHG']
    context.short_period = 5
    context.long_period = 20
    
def handle_data(context, data):
    for stock in context.stocks:
        # 获取历史数据
        hist = data.history(stock, 'close', context.long_period + 1, '1d')
        
        # 计算移动平均线
        short_ma = hist[-context.short_period:].mean()
        long_ma = hist[-context.long_period:].mean()
        
        # 计算昨日移动平均线
        prev_short_ma = hist[-context.short_period-1:-1].mean()
        prev_long_ma = hist[-context.long_period-1:-1].mean()
        
        # 交易信号
        if prev_short_ma < prev_long_ma and short_ma > long_ma:
            # 买入信号
            order_target_percent(stock, 0.5)
        elif prev_short_ma > prev_long_ma and short_ma < long_ma:
            # 卖出信号
            order_target_percent(stock, 0)
      `,
      parameters: {
        'short_period': 5,
        'long_period': 20,
        'universe': ['000001', '600036']
      },
      backtest_count: 3,
      trade_count: 12,
      last_run: '2023-04-28'
    })
    
    // 模拟绩效数据
    performanceData.value = {
      total_return: 22.5,
      annual_return: 15.8, 
      max_drawdown: -12.3,
      sharpe_ratio: 1.2,
      volatility: 18.5,
      win_rate: 58.3,
      profit_factor: 1.8,
      avg_profit: 2.5,
      avg_loss: -1.4
    }
    
    // 初始化图表
    initCharts()
  } catch (error) {
    console.error('获取策略详情失败:', error)
    ElMessage.error('获取策略详情失败')
  } finally {
    loading.value = false
  }
}

// 编辑策略
const editStrategy = () => {
  router.push(`/strategy/edit/${strategyId.value}`)
}

// 运行回测
const runBacktest = () => {
  router.push({
    path: '/backtest/create',
    query: { strategy_id: strategyId.value }
  })
}

// 启动/停止策略
const toggleStrategyStatus = () => {
  const newStatus = strategy.status === 'active' ? 'inactive' : 'active'
  const actionText = newStatus === 'active' ? '启动' : '停止'
  
  ElMessageBox.confirm(
    `确定要${actionText}策略"${strategy.name}"吗?`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 实际项目中应该调用API
    strategy.status = newStatus
    ElMessage.success(`策略已${actionText}`)
  }).catch(() => {
    // 用户取消操作
  })
}

// 初始化图表
const initCharts = () => {
  // 创建收益率图表
  const returnsChart = echarts.init(document.getElementById('returns-chart'))
  
  // 生成模拟数据
  const dates = []
  const returns = []
  const benchmarkReturns = []
  
  const startDate = new Date('2023-01-01')
  let cumReturn = 0
  let benchmarkReturn = 0
  
  for (let i = 0; i < 90; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)
    
    // 模拟每日收益率
    const dailyReturn = (Math.random() - 0.45) * 1.5
    const benchmarkDailyReturn = (Math.random() - 0.48) * 1.2
    
    cumReturn += dailyReturn
    benchmarkReturn += benchmarkDailyReturn
    
    returns.push(cumReturn.toFixed(2))
    benchmarkReturns.push(benchmarkReturn.toFixed(2))
  }
  
  returnsChart.setOption({
    title: {
      text: '策略收益表现',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['策略收益', '基准收益'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLabel: {
        rotate: 30,
        interval: 15
      }
    },
    yAxis: {
      type: 'value',
      name: '收益率(%)',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '策略收益',
        type: 'line',
        data: returns,
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#409EFF'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.4)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ]
          }
        }
      },
      {
        name: '基准收益',
        type: 'line',
        data: benchmarkReturns,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#909399'
        }
      }
    ]
  })
  
  // 窗口大小变化时重新调整图表
  window.addEventListener('resize', () => {
    returnsChart.resize()
  })
}

// 组件挂载时获取数据
onMounted(() => {
  fetchStrategyDetail()
})
</script>

<template>
  <div class="strategy-detail-container">
    <el-skeleton :loading="loading" animated>
      <template #template>
        <div class="skeleton-content">
          <el-skeleton-item variant="h1" style="width: 50%" />
          <el-skeleton-item variant="text" style="margin-top: 20px; width: 80%" />
          <el-skeleton-item variant="text" style="margin-top: 10px; width: 70%" />
          <el-skeleton-item variant="text" style="margin-top: 10px; width: 60%" />
          <div style="margin-top: 30px; display: flex; gap: 20px;">
            <el-skeleton-item variant="button" style="width: 100px" />
            <el-skeleton-item variant="button" style="width: 100px" />
            <el-skeleton-item variant="button" style="width: 100px" />
          </div>
          <div style="margin-top: 30px; height: 300px">
            <el-skeleton-item variant="p" style="height: 100%" />
          </div>
        </div>
      </template>
      
      <template #default>
        <!-- 策略头部信息 -->
        <div class="strategy-header">
          <div class="strategy-title-area">
            <div class="flex-row align-center">
              <h1 class="strategy-title">{{ strategy.name }}</h1>
              <el-tag 
                :type="strategy.status === 'active' ? 'success' : 'info'"
                size="small"
                class="status-tag"
              >
                {{ strategy.status === 'active' ? '运行中' : '已停止' }}
              </el-tag>
              <el-tag 
                type="info" 
                size="small"
                v-if="strategy.is_public"
              >公开</el-tag>
            </div>
            <p class="strategy-description">{{ strategy.description }}</p>
            <div class="strategy-meta">
              <span class="meta-item">创建时间: {{ strategy.created_at }}</span>
              <span class="meta-item">最近运行: {{ strategy.last_run || '未运行' }}</span>
              <span class="meta-item">回测次数: {{ strategy.backtest_count }}</span>
              <span class="meta-item">交易次数: {{ strategy.trade_count }}</span>
            </div>
          </div>
          
          <div class="strategy-actions">
            <el-button 
              type="primary" 
              @click="editStrategy"
            >
              <el-icon><el-icon-Edit /></el-icon>
              编辑策略
            </el-button>
            
            <el-button 
              :type="strategy.status === 'active' ? 'danger' : 'success'"
              @click="toggleStrategyStatus"
            >
              <el-icon v-if="strategy.status === 'active'"><el-icon-VideoPause /></el-icon>
              <el-icon v-else><el-icon-VideoPlay /></el-icon>
              {{ strategy.status === 'active' ? '停止策略' : '启动策略' }}
            </el-button>
            
            <el-button 
              type="warning" 
              @click="runBacktest"
            >
              <el-icon><el-icon-DataLine /></el-icon>
              运行回测
            </el-button>
          </div>
        </div>
        
        <!-- 绩效概览 -->
        <el-card class="performance-card">
          <template #header>
            <div class="card-header">
              <span>绩效概览</span>
              <span 
                class="return-rate" 
                :class="performanceData.total_return >= 0 ? 'text-success' : 'text-danger'"
              >
                {{ performanceData.total_return >= 0 ? '+' : '' }}{{ performanceData.total_return }}%
              </span>
            </div>
          </template>
          
          <div class="performance-grid">
            <div class="performance-item">
              <div class="item-label">年化收益</div>
              <div 
                class="item-value" 
                :class="performanceData.annual_return >= 0 ? 'text-success' : 'text-danger'"
              >
                {{ performanceData.annual_return >= 0 ? '+' : '' }}{{ performanceData.annual_return }}%
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">最大回撤</div>
              <div class="item-value text-danger">
                {{ performanceData.max_drawdown }}%
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">夏普比率</div>
              <div class="item-value">
                {{ performanceData.sharpe_ratio }}
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">波动率</div>
              <div class="item-value">
                {{ performanceData.volatility }}%
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">胜率</div>
              <div class="item-value">
                {{ performanceData.win_rate }}%
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">盈亏比</div>
              <div class="item-value">
                {{ performanceData.profit_factor }}
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">平均盈利</div>
              <div class="item-value text-success">
                {{ performanceData.avg_profit }}%
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">平均亏损</div>
              <div class="item-value text-danger">
                {{ performanceData.avg_loss }}%
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 收益图表 -->
        <el-card class="chart-card">
          <div id="returns-chart" class="returns-chart"></div>
        </el-card>
        
        <!-- 策略参数和代码 -->
        <div class="strategy-details-row">
          <el-card class="params-card">
            <template #header>
              <div class="card-header">
                <span>策略参数</span>
                <el-button type="text" @click="editStrategy">修改参数</el-button>
              </div>
            </template>
            
            <el-descriptions :column="1" border>
              <el-descriptions-item 
                v-for="(value, key) in strategy.parameters" 
                :key="key" 
                :label="key"
              >
                {{ Array.isArray(value) ? value.join(', ') : value }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
          
          <el-card class="code-card">
            <template #header>
              <div class="card-header">
                <span>策略代码</span>
                <el-button type="text" @click="editStrategy">编辑代码</el-button>
              </div>
            </template>
            
            <pre class="code-block">{{ strategy.code }}</pre>
          </el-card>
        </div>
        
        <!-- 回测和交易记录 -->
        <div class="strategy-details-row">
          <!-- 回测历史记录 -->
          <el-card class="backtest-card">
            <template #header>
              <div class="card-header">
                <span>回测历史</span>
                <el-button type="text" @click="router.push('/backtest')">查看全部</el-button>
              </div>
            </template>
            
            <el-table :data="backtestHistory" style="width: 100%" size="small">
              <el-table-column prop="start_date" label="开始日期" width="100"></el-table-column>
              <el-table-column prop="end_date" label="结束日期" width="100"></el-table-column>
              <el-table-column prop="return_rate" label="收益率">
                <template #default="scope">
                  <span 
                    :class="scope.row.return_rate >= 0 ? 'text-success' : 'text-danger'"
                  >
                    {{ scope.row.return_rate >= 0 ? '+' : '' }}{{ scope.row.return_rate }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="scope">
                  <el-button 
                    size="small"
                    type="primary"
                    plain
                    @click="router.push(`/backtest/${scope.row.id}`)"
                  >
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
          
          <!-- 交易记录 -->
          <el-card class="trades-card">
            <template #header>
              <div class="card-header">
                <span>交易记录</span>
                <el-button type="text" @click="router.push('/trading/orders')">查看全部</el-button>
              </div>
            </template>
            
            <el-table :data="recentTrades" style="width: 100%" size="small">
              <el-table-column prop="date" label="日期" width="100"></el-table-column>
              <el-table-column prop="symbol" label="代码" width="80"></el-table-column>
              <el-table-column prop="name" label="名称" width="100"></el-table-column>
              <el-table-column prop="direction" label="方向">
                <template #default="scope">
                  <span :class="scope.row.direction === 'buy' ? 'text-success' : 'text-danger'">
                    {{ scope.row.direction === 'buy' ? '买入' : '卖出' }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="价格"></el-table-column>
              <el-table-column prop="quantity" label="数量"></el-table-column>
            </el-table>
          </el-card>
        </div>
      </template>
    </el-skeleton>
  </div>
</template>

<style scoped>
.strategy-detail-container {
  padding: 20px;
}

.skeleton-content {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
}

.strategy-header {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.strategy-title-area {
  flex: 1;
}

.flex-row {
  display: flex;
  flex-direction: row;
}

.align-center {
  align-items: center;
}

.strategy-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  margin-right: 10px;
}

.status-tag {
  margin-right: 10px;
}

.strategy-description {
  margin: 10px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.strategy-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #909399;
}

.strategy-actions {
  display: flex;
  gap: 10px;
}

.performance-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.return-rate {
  font-size: 18px;
  font-weight: 600;
}

.performance-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.performance-item {
  text-align: center;
}

.item-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.item-value {
  font-size: 20px;
  font-weight: 600;
}

.chart-card {
  margin-bottom: 20px;
}

.returns-chart {
  height: 400px;
}

.strategy-details-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.params-card, .backtest-card {
  width: 40%;
}

.code-card, .trades-card {
  flex: 1;
}

.code-block {
  white-space: pre-wrap;
  font-family: monospace;
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.5;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}
</style> 