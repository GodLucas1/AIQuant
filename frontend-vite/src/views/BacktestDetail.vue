<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()
const backtestId = computed(() => route.params.id)
const loading = ref(true)

// 回测数据
const backtest = reactive({
  id: null,
  name: '',
  strategy_id: null,
  strategy_name: '',
  description: '',
  start_date: '',
  end_date: '',
  initial_capital: 0,
  final_capital: 0,
  return_rate: 0,
  annual_return: 0,
  max_drawdown: 0,
  sharpe_ratio: 0,
  volatility: 0,
  win_rate: 0,
  profit_factor: 0,
  max_profit_trade: 0,
  max_loss_trade: 0,
  avg_profit_trade: 0,
  avg_loss_trade: 0,
  avg_holding_period: 0,
  total_trades: 0,
  winning_trades: 0,
  losing_trades: 0,
  status: '',
  created_at: '',
  parameters: {}
})

// 交易记录
const trades = ref([])

// 获取回测详情
const fetchBacktestDetail = async () => {
  loading.value = true
  try {
    // 实际项目中应该调用API
    // 模拟API请求延迟
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 模拟回测数据
    Object.assign(backtest, {
      id: backtestId.value,
      name: '均线突破策略回测(2022全年)',
      strategy_id: 1,
      strategy_name: '均线突破策略',
      description: '测试均线策略在2022年完整行情中的表现，使用5日和20日均线交叉信号',
      start_date: '2022-01-01',
      end_date: '2022-12-31',
      initial_capital: 100000,
      final_capital: 112350,
      return_rate: 12.35,
      annual_return: 12.35,
      max_drawdown: -8.5,
      sharpe_ratio: 1.2,
      volatility: 15.7,
      win_rate: 58.3,
      profit_factor: 1.75,
      max_profit_trade: 4.2,
      max_loss_trade: -2.8,
      avg_profit_trade: 2.1,
      avg_loss_trade: -1.5,
      avg_holding_period: 12,
      total_trades: 48,
      winning_trades: 28,
      losing_trades: 20,
      status: 'completed',
      created_at: '2023-01-05',
      parameters: {
        'short_period': 5,
        'long_period': 20,
        'universe': ['000001', '600036', '601318', '600519', '000651']
      }
    })
    
    // 模拟交易记录
    trades.value = generateTrades()
    
    // 初始化图表
    setTimeout(() => {
      initCharts()
    }, 100)
  } catch (error) {
    console.error('获取回测详情失败:', error)
    ElMessage.error('获取回测详情失败')
  } finally {
    loading.value = false
  }
}

// 生成模拟交易记录
const generateTrades = () => {
  const result = []
  const symbols = ['000001', '600036', '601318', '600519', '000651']
  const symbolNames = {
    '000001': '平安银行',
    '600036': '招商银行',
    '601318': '中国平安',
    '600519': '贵州茅台',
    '000651': '格力电器'
  }
  
  const startDate = new Date('2022-01-01')
  const endDate = new Date('2022-12-31')
  
  for (let i = 0; i < 48; i++) {
    const tradeDate = new Date(startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime()))
    const symbol = symbols[Math.floor(Math.random() * symbols.length)]
    const direction = Math.random() > 0.5 ? 'buy' : 'sell'
    const price = (Math.random() * 100 + 10).toFixed(2)
    const quantity = Math.floor(Math.random() * 1000 + 100)
    const profitLoss = direction === 'buy' 
      ? Math.random() > 0.4 ? (Math.random() * 5).toFixed(2) : -(Math.random() * 3).toFixed(2)
      : Math.random() > 0.4 ? (Math.random() * 5).toFixed(2) : -(Math.random() * 3).toFixed(2)
    
    result.push({
      id: i + 1,
      date: tradeDate.toISOString().split('T')[0],
      symbol,
      name: symbolNames[symbol],
      direction,
      price,
      quantity,
      total_value: (price * quantity).toFixed(2),
      profit_loss: profitLoss,
      profit_loss_percentage: (profitLoss / (price * quantity) * 100).toFixed(2)
    })
  }
  
  // 按日期排序
  result.sort((a, b) => new Date(a.date) - new Date(b.date))
  
  return result
}

// 导出回测结果
const exportBacktest = (format) => {
  // 实际项目中应该调用API下载文件
  ElMessage.success(`已导出回测结果: ${backtest.name}.${format}`)
}

// 删除回测
const deleteBacktest = () => {
  ElMessageBox.confirm(
    `确定要删除回测 "${backtest.name}" 吗? 此操作不可逆。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 实际项目中应该调用API
    ElMessage.success('回测已删除')
    router.push('/backtest')
  }).catch(() => {
    // 用户取消操作
  })
}

// 重新运行回测
const rerunBacktest = () => {
  ElMessageBox.confirm(
    `确定要重新运行回测 "${backtest.name}" 吗?`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    // 实际项目中应该调用API
    ElMessage.success('已开始重新运行回测')
    backtest.status = 'running'
  }).catch(() => {
    // 用户取消操作
  })
}

// 初始化图表
const initCharts = () => {
  // 1. 初始化收益图表
  initEquityChart()
  
  // 2. 初始化回撤图表
  initDrawdownChart()
  
  // 3. 初始化月度收益热图
  initMonthlyReturnsChart()
  
  // 4. 初始化交易分布图
  initTradeDistributionChart()
}

// 初始化收益图表
const initEquityChart = () => {
  const equityChart = echarts.init(document.getElementById('equity-chart'))
  
  // 生成模拟数据
  const dates = []
  const equity = []
  const benchmark = []
  
  const startDate = new Date(backtest.start_date)
  const endDate = new Date(backtest.end_date)
  const days = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))
  
  let initialEquity = backtest.initial_capital
  let benchmarkValue = backtest.initial_capital
  
  for (let i = 0; i <= days; i += Math.max(1, Math.floor(days / 200))) {
    const currentDate = new Date(startDate)
    currentDate.setDate(startDate.getDate() + i)
    dates.push(currentDate.toISOString().split('T')[0])
    
    // 模拟权益曲线
    const progress = i / days
    const randomFactor = 1 + (Math.random() * 0.1 - 0.03) * Math.sin(progress * Math.PI)
    initialEquity = initialEquity * randomFactor
    equity.push(initialEquity.toFixed(2))
    
    // 模拟基准曲线
    const benchmarkFactor = 1 + (Math.random() * 0.08 - 0.04) * Math.sin(progress * Math.PI)
    benchmarkValue = benchmarkValue * benchmarkFactor
    benchmark.push(benchmarkValue.toFixed(2))
  }
  
  // 确保最后一个值等于final_capital
  equity[equity.length - 1] = backtest.final_capital
  
  equityChart.setOption({
    title: {
      text: '回测权益曲线',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(param => {
          result += `${param.seriesName}: ¥${parseFloat(param.value).toLocaleString()}<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['策略', '基准'],
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
        rotate: 45,
        formatter: function(value) {
          return value.substring(5)  // 只显示月-日
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '资金',
      axisLabel: {
        formatter: '¥{value}'
      },
      scale: true
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '策略',
        type: 'line',
        data: equity,
        smooth: true,
        symbol: 'none',
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
        name: '基准',
        type: 'line',
        data: benchmark,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          width: 2,
          color: '#909399'
        }
      }
    ]
  })
  
  // 窗口大小变化时重新调整图表
  window.addEventListener('resize', () => {
    equityChart.resize()
  })
}

// 初始化回撤图表
const initDrawdownChart = () => {
  const drawdownChart = echarts.init(document.getElementById('drawdown-chart'))
  
  // 生成模拟数据
  const dates = []
  const drawdowns = []
  
  const startDate = new Date(backtest.start_date)
  const endDate = new Date(backtest.end_date)
  const days = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))
  
  let maxDrawdown = 0
  let currentDrawdown = 0
  
  for (let i = 0; i <= days; i += Math.max(1, Math.floor(days / 200))) {
    const currentDate = new Date(startDate)
    currentDate.setDate(startDate.getDate() + i)
    dates.push(currentDate.toISOString().split('T')[0])
    
    // 模拟回撤
    const progress = i / days
    currentDrawdown = Math.min(0, currentDrawdown + (Math.random() * 2 - 1) * 0.5)
    
    // 模拟几次较大回撤
    if (progress > 0.2 && progress < 0.3 || progress > 0.6 && progress < 0.7) {
      currentDrawdown = Math.min(currentDrawdown, -Math.random() * 6)
    }
    
    // 随机恢复
    if (Math.random() > 0.8) {
      currentDrawdown = Math.min(0, currentDrawdown * 0.7)
    }
    
    maxDrawdown = Math.min(maxDrawdown, currentDrawdown)
    drawdowns.push(currentDrawdown.toFixed(2))
  }
  
  // 确保最大回撤接近backtest.max_drawdown
  const scale = backtest.max_drawdown / maxDrawdown
  drawdowns.forEach((val, idx) => {
    drawdowns[idx] = (parseFloat(val) * scale).toFixed(2)
  })
  
  drawdownChart.setOption({
    title: {
      text: '回撤分析',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c}%'
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
        rotate: 45,
        formatter: function(value) {
          return value.substring(5)  // 只显示月-日
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '回撤(%)',
      axisLabel: {
        formatter: '{value}%'
      },
      max: 0,
      min: Math.min(backtest.max_drawdown * 1.2, -10)
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '回撤',
        type: 'line',
        data: drawdowns,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          width: 2,
          color: '#F56C6C'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(245, 108, 108, 0.2)' },
              { offset: 1, color: 'rgba(245, 108, 108, 0.8)' }
            ]
          }
        },
        markLine: {
          data: [
            {
              name: '最大回撤',
              yAxis: backtest.max_drawdown,
              lineStyle: {
                color: '#F56C6C',
                type: 'dashed'
              },
              label: {
                show: true,
                formatter: '{b}: {c}%',
                position: 'middle'
              }
            }
          ]
        }
      }
    ]
  })
  
  // 窗口大小变化时重新调整图表
  window.addEventListener('resize', () => {
    drawdownChart.resize()
  })
}

// 初始化月度收益热图
const initMonthlyReturnsChart = () => {
  const monthlyChart = echarts.init(document.getElementById('monthly-returns-chart'))
  
  // 生成模拟月度收益数据
  const years = ['2022']
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  const data = []
  
  for (let year of years) {
    for (let i = 0; i < months.length; i++) {
      // 模拟月度收益，大部分为正
      const value = (Math.random() * 6 - 1).toFixed(2)
      data.push([i, years.indexOf(year), value])
    }
  }
  
  const option = {
    title: {
      text: '月度收益热图',
      left: 'center'
    },
    tooltip: {
      position: 'top',
      formatter: function (params) {
        return `${years[params.value[1]]}年${months[params.value[0]]}: ${params.value[2]}%`;
      }
    },
    grid: {
      top: '60',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: months,
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: years,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: -5,
      max: 5,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0',
      inRange: {
        color: ['#F56C6C', '#FCFCFC', '#67C23A']
      }
    },
    series: [{
      name: '月度收益',
      type: 'heatmap',
      data: data,
      label: {
        show: true,
        formatter: function(params) {
          return params.value[2] + '%'
        }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  monthlyChart.setOption(option)
  
  // 窗口大小变化时重新调整图表
  window.addEventListener('resize', () => {
    monthlyChart.resize()
  })
}

// 初始化交易分布图
const initTradeDistributionChart = () => {
  const tradeChart = echarts.init(document.getElementById('trade-distribution-chart'))
  
  // 计算不同收益区间的交易数量
  const ranges = [
    '< -5%', 
    '-5% ~ -3%', 
    '-3% ~ -1%', 
    '-1% ~ 0%', 
    '0% ~ 1%', 
    '1% ~ 3%', 
    '3% ~ 5%', 
    '> 5%'
  ]
  
  // 模拟数据
  const data = [3, 5, 8, 4, 6, 9, 7, 6]
  const colors = []
  
  for (let i = 0; i < ranges.length; i++) {
    // 为负收益区间使用红色，为正收益区间使用绿色
    if (i < 4) {
      colors.push('#F56C6C')
    } else {
      colors.push('#67C23A')
    }
  }
  
  const option = {
    title: {
      text: '交易收益分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}笔交易'
    },
    xAxis: {
      type: 'category',
      data: ranges,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '交易次数'
    },
    series: [{
      name: '交易次数',
      type: 'bar',
      data: data,
      itemStyle: {
        color: function(params) {
          return colors[params.dataIndex]
        }
      }
    }]
  }
  
  tradeChart.setOption(option)
  
  // 窗口大小变化时重新调整图表
  window.addEventListener('resize', () => {
    tradeChart.resize()
  })
}

// 组件挂载时获取数据
onMounted(() => {
  fetchBacktestDetail()
})
</script>

<template>
  <div class="backtest-detail-container">
    <el-skeleton :loading="loading" animated>
      <template #template>
        <div class="skeleton-content">
          <el-skeleton-item variant="h1" style="width: 50%" />
          <el-skeleton-item variant="text" style="margin-top: 20px; width: 80%" />
          <el-skeleton-item variant="text" style="margin-top: 10px; width: 70%" />
          <div style="margin-top: 30px; height: 300px">
            <el-skeleton-item variant="p" style="height: 100%" />
          </div>
        </div>
      </template>
      
      <template #default>
        <!-- 回测头部信息 -->
        <div class="backtest-header">
          <div class="backtest-title-area">
            <div class="flex-row align-center">
              <h1 class="backtest-title">{{ backtest.name }}</h1>
              <el-tag 
                :type="backtest.status === 'completed' ? 'success' : backtest.status === 'running' ? 'warning' : backtest.status === 'failed' ? 'danger' : 'info'"
                size="small"
                class="status-tag"
              >
                {{ 
                  backtest.status === 'completed' ? '已完成' : 
                  backtest.status === 'running' ? '运行中' : 
                  backtest.status === 'failed' ? '失败' : '已创建' 
                }}
              </el-tag>
            </div>
            <p class="backtest-description">{{ backtest.description }}</p>
            <div class="backtest-meta">
              <span class="meta-item">策略: {{ backtest.strategy_name }}</span>
              <span class="meta-item">回测区间: {{ backtest.start_date }} 至 {{ backtest.end_date }}</span>
              <span class="meta-item">初始资金: ¥{{ backtest.initial_capital.toLocaleString() }}</span>
              <span class="meta-item">创建时间: {{ backtest.created_at }}</span>
            </div>
          </div>
          
          <div class="backtest-actions">
            <el-dropdown trigger="click">
              <el-button type="primary">
                操作
                <el-icon class="el-icon--right"><el-icon-ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="rerunBacktest">重新运行</el-dropdown-item>
                  <el-dropdown-item @click="exportBacktest('csv')">导出CSV</el-dropdown-item>
                  <el-dropdown-item @click="exportBacktest('excel')">导出Excel</el-dropdown-item>
                  <el-dropdown-item divided @click="deleteBacktest" class="text-danger">删除回测</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <el-button @click="router.push('/backtest')">返回列表</el-button>
          </div>
        </div>
        
        <!-- 回测绩效 -->
        <el-card class="performance-card">
          <template #header>
            <div class="card-header">
              <span>回测绩效</span>
              <span 
                class="return-rate" 
                :class="backtest.return_rate >= 0 ? 'text-success' : 'text-danger'"
              >
                {{ backtest.return_rate >= 0 ? '+' : '' }}{{ backtest.return_rate }}%
              </span>
            </div>
          </template>
          
          <div class="performance-grid">
            <div class="performance-item">
              <div class="item-label">初始资金</div>
              <div class="item-value">
                ¥{{ backtest.initial_capital.toLocaleString() }}
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">最终资金</div>
              <div class="item-value">
                ¥{{ backtest.final_capital.toLocaleString() }}
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">年化收益率</div>
              <div 
                class="item-value" 
                :class="backtest.annual_return >= 0 ? 'text-success' : 'text-danger'"
              >
                {{ backtest.annual_return >= 0 ? '+' : '' }}{{ backtest.annual_return }}%
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">最大回撤</div>
              <div class="item-value text-danger">
                {{ backtest.max_drawdown }}%
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">夏普比率</div>
              <div class="item-value">
                {{ backtest.sharpe_ratio }}
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">波动率</div>
              <div class="item-value">
                {{ backtest.volatility }}%
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">胜率</div>
              <div class="item-value">
                {{ backtest.win_rate }}%
              </div>
            </div>
            
            <div class="performance-item">
              <div class="item-label">盈亏比</div>
              <div class="item-value">
                {{ backtest.profit_factor }}
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 图表展示 -->
        <div class="charts-section">
          <el-tabs type="border-card">
            <el-tab-pane label="权益曲线">
              <div id="equity-chart" class="chart-container"></div>
            </el-tab-pane>
            
            <el-tab-pane label="回撤分析">
              <div id="drawdown-chart" class="chart-container"></div>
            </el-tab-pane>
            
            <el-tab-pane label="月度收益">
              <div id="monthly-returns-chart" class="chart-container"></div>
            </el-tab-pane>
            
            <el-tab-pane label="交易分布">
              <div id="trade-distribution-chart" class="chart-container"></div>
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <!-- 交易记录 -->
        <el-card class="trades-card">
          <template #header>
            <div class="card-header">
              <span>交易记录 (共{{ trades.length }}笔)</span>
              <div class="card-actions">
                <el-button size="small" type="primary" @click="exportBacktest('trades-csv')">导出交易记录</el-button>
              </div>
            </div>
          </template>
          
          <el-table :data="trades" style="width: 100%" height="400" border>
            <el-table-column type="index" label="#" width="50"></el-table-column>
            <el-table-column prop="date" label="交易日期" width="120" sortable></el-table-column>
            <el-table-column prop="symbol" label="代码" width="100"></el-table-column>
            <el-table-column prop="name" label="名称" width="120"></el-table-column>
            <el-table-column prop="direction" label="方向" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.direction === 'buy' ? 'success' : 'danger'" size="small">
                  {{ scope.row.direction === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="100"></el-table-column>
            <el-table-column prop="quantity" label="数量" width="100"></el-table-column>
            <el-table-column prop="total_value" label="交易额" width="120"></el-table-column>
            <el-table-column prop="profit_loss" label="盈亏" width="100">
              <template #default="scope">
                <span 
                  :class="parseFloat(scope.row.profit_loss) >= 0 ? 'text-success' : 'text-danger'"
                >
                  {{ parseFloat(scope.row.profit_loss) >= 0 ? '+' : '' }}{{ scope.row.profit_loss }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="profit_loss_percentage" label="盈亏率" width="100">
              <template #default="scope">
                <span 
                  :class="parseFloat(scope.row.profit_loss_percentage) >= 0 ? 'text-success' : 'text-danger'"
                >
                  {{ parseFloat(scope.row.profit_loss_percentage) >= 0 ? '+' : '' }}{{ scope.row.profit_loss_percentage }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        
        <!-- 回测参数 -->
        <el-card class="params-card">
          <template #header>
            <div class="card-header">
              <span>回测参数</span>
            </div>
          </template>
          
          <el-descriptions :column="3" border>
            <el-descriptions-item 
              v-for="(value, key) in backtest.parameters" 
              :key="key" 
              :label="key"
            >
              {{ Array.isArray(value) ? value.join(', ') : value }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </template>
    </el-skeleton>
  </div>
</template>

<style scoped>
.backtest-detail-container {
  padding: 20px;
}

.skeleton-content {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
}

.backtest-header {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.backtest-title-area {
  flex: 1;
}

.flex-row {
  display: flex;
  flex-direction: row;
}

.align-center {
  align-items: center;
}

.backtest-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  margin-right: 10px;
}

.status-tag {
  margin-right: 10px;
}

.backtest-description {
  margin: 10px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.backtest-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 13px;
  color: #909399;
}

.backtest-actions {
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

.card-actions {
  display: flex;
  gap: 10px;
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

.charts-section {
  margin-bottom: 20px;
}

.chart-container {
  height: 400px;
  padding: 10px;
}

.trades-card, .params-card {
  margin-bottom: 20px;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}
</style> 