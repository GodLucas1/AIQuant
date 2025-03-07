<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSymbols, getMarketData, getDepth, getTrades } from '../api/market.js'
import { getExchanges } from '../api/market.js'

// 股票搜索
const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)

// 股票相关数据
const stockSymbol = ref('')
const stockName = ref('')
const stockPrice = ref(null)
const stockChange = ref(null)
const stockVolume = ref(null)

// 可用交易所
const exchanges = ref([])
const selectedExchange = ref('binance')

// 获取交易所列表
const loadExchanges = async () => {
  try {
    const data = await getExchanges()
    exchanges.value = data
    if (data.length > 0) {
      selectedExchange.value = data[0]
    }
  } catch (error) {
    console.error('获取交易所列表失败:', error)
    ElMessage.error('获取交易所列表失败')
  }
}

// 搜索股票
const handleSearch = async () => {
  if (!searchQuery.value) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  
  searching.value = true
  
  try {
    const data = await getSymbols({
      exchange: selectedExchange.value,
      keyword: searchQuery.value
    })
    
    searchResults.value = data.map(item => ({
      symbol: item.symbol,
      name: item.baseAsset + '/' + item.quoteAsset,
      price: item.lastPrice || '暂无',
      change: (item.priceChangePercent > 0 ? '+' : '') + item.priceChangePercent + '%',
      volume: (item.volume / 1000).toFixed(1) + '千'
    }))
    
    if (searchResults.value.length === 0) {
      ElMessage.info('未找到相关交易对')
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请重试')
  } finally {
    searching.value = false
  }
}

// 查看股票详情
const viewStockDetail = async (stock) => {
  stockSymbol.value = stock.symbol
  stockName.value = stock.name
  stockPrice.value = stock.price
  stockChange.value = stock.change
  stockVolume.value = stock.volume
  
  try {
    // 获取更详细的市场数据
    const marketData = await getMarketData({
      symbol: stock.symbol,
      exchange: selectedExchange.value,
      interval: '1d',
      limit: 1
    })
    
    // 获取深度数据
    const depthData = await getDepth({
      symbol: stock.symbol,
      exchange: selectedExchange.value,
      limit: 5
    })
    
    // 获取最近成交
    const tradesData = await getTrades({
      symbol: stock.symbol,
      exchange: selectedExchange.value,
      limit: 10
    })
    
    // 这里可以处理获取到的数据，更新图表等
    
    ElMessage.success(`已加载 ${stock.name} 的数据`)
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败，请重试')
  }
}

// 获取热门交易对
const hotStocks = ref([])
const loadHotStocks = async () => {
  try {
    const data = await getSymbols({
      exchange: selectedExchange.value,
      sort: 'volume',
      limit: 10
    })
    
    hotStocks.value = data.map(item => ({
      symbol: item.symbol,
      name: item.baseAsset + '/' + item.quoteAsset,
      price: item.lastPrice || '暂无',
      change: (item.priceChangePercent > 0 ? '+' : '') + item.priceChangePercent + '%',
      volume: (item.volume / 1000).toFixed(1) + '千'
    }))
  } catch (error) {
    console.error('获取热门交易对失败:', error)
    ElMessage.error('获取热门交易对失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadExchanges()
  loadHotStocks()
})
</script>

<template>
  <div class="market-data-container">
    <h1 class="page-title">市场数据</h1>
    
    <!-- 股票搜索 -->
    <el-card class="search-card">
      <div class="search-form">
        <el-select v-model="selectedExchange" class="exchange-select" @change="loadHotStocks">
          <el-option
            v-for="exchange in exchanges"
            :key="exchange"
            :label="exchange"
            :value="exchange"
          />
        </el-select>
        <el-input 
          v-model="searchQuery" 
          placeholder="输入交易对名称搜索，如 BTC/USDT"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><el-icon-Search /></el-icon>
          </template>
          <template #append>
            <el-button @click="handleSearch" :loading="searching">搜索</el-button>
          </template>
        </el-input>
      </div>
      
      <!-- 搜索结果 -->
      <div class="search-results" v-if="searchResults.length > 0">
        <div class="result-title">搜索结果</div>
        <el-table :data="searchResults" style="width: 100%" border>
          <el-table-column prop="symbol" label="交易对" width="120"></el-table-column>
          <el-table-column prop="name" label="名称" width="150"></el-table-column>
          <el-table-column prop="price" label="价格"></el-table-column>
          <el-table-column prop="change" label="24h涨跌幅">
            <template #default="scope">
              <span :class="scope.row.change.startsWith('+') ? 'text-success' : 'text-danger'">
                {{ scope.row.change }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量"></el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button 
                size="small"
                type="primary"
                @click="viewStockDetail(scope.row)"
              >
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
    
    <!-- 股票详情 -->
    <el-card class="stock-detail-card" v-if="stockSymbol">
      <div class="stock-detail-header">
        <div class="stock-info">
          <span class="stock-name">{{ stockName }}</span>
          <span class="stock-symbol">{{ stockSymbol }}</span>
        </div>
        <div class="stock-price-info">
          <span class="stock-price">{{ stockPrice }}</span>
          <span :class="['stock-change', stockChange?.startsWith('+') ? 'text-success' : 'text-danger']">
            {{ stockChange }}
          </span>
        </div>
      </div>
      
      <div class="stock-detail-body">
        <div class="detail-item">
          <span class="detail-label">24h成交量</span>
          <span class="detail-value">{{ stockVolume }}</span>
        </div>
      </div>
      
      <div class="stock-chart-placeholder">
        <el-tabs>
          <el-tab-pane label="K线图">
            <el-empty description="K线图加载中..."></el-empty>
          </el-tab-pane>
          <el-tab-pane label="深度图">
            <el-empty description="深度图加载中..."></el-empty>
          </el-tab-pane>
          <el-tab-pane label="成交记录">
            <el-empty description="成交记录加载中..."></el-empty>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
    
    <!-- 热门交易对 -->
    <el-card class="hot-stocks-card">
      <template #header>
        <div class="card-header">
          <span>热门交易对 ({{ selectedExchange }})</span>
          <el-button type="text" @click="loadHotStocks">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="hotStocks" style="width: 100%" v-loading="hotStocks.length === 0">
        <el-table-column prop="symbol" label="交易对" width="120"></el-table-column>
        <el-table-column prop="name" label="名称" width="150"></el-table-column>
        <el-table-column prop="price" label="价格"></el-table-column>
        <el-table-column prop="change" label="24h涨跌幅">
          <template #default="scope">
            <span :class="scope.row.change.startsWith('+') ? 'text-success' : 'text-danger'">
              {{ scope.row.change }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量"></el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="scope">
            <el-button 
              size="small"
              type="primary"
              @click="viewStockDetail(scope.row)"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.market-data-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 500;
}

.search-card,
.stock-detail-card,
.hot-stocks-card {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.exchange-select {
  width: 120px;
}

.result-title {
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: 500;
}

.stock-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stock-name {
  font-size: 20px;
  font-weight: 500;
  margin-right: 10px;
}

.stock-symbol {
  font-size: 14px;
  color: #909399;
}

.stock-price {
  font-size: 24px;
  font-weight: bold;
  margin-right: 10px;
}

.stock-change {
  font-size: 16px;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}

.stock-detail-body {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.detail-item {
  margin-right: 30px;
  margin-bottom: 10px;
}

.detail-label {
  font-size: 14px;
  color: #909399;
  margin-right: 10px;
}

.detail-value {
  font-size: 14px;
  font-weight: 500;
}

.stock-chart-placeholder {
  height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 