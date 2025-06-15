<template>
  <div class="stock-dashboard">
    <el-row :gutter="20" class="dashboard-header">
      <el-col :xs="24" :md="16">
        <el-card class="welcome-card" shadow="hover">
          <div class="welcome-content">
            <div class="welcome-text">
              <h1>股票数据分析平台</h1>
              <p>欢迎使用股票数据分析平台，这里提供市场趋势分析、股票实时数据和智能预测功能。</p>
              <div class="action-buttons">
                <el-button type="primary" @click="refreshDashboard" :loading="loading">
                  <el-icon><Refresh /></el-icon>
                  刷新数据
                </el-button>

                <el-radio-group v-model="selectedMarket" @change="switchMarket" size="large">
                  <el-radio-button label="TW">台灣市場</el-radio-button>
                  <el-radio-button label="US">美國市場</el-radio-button>
                </el-radio-group>
              </div>
            </div>
            <div class="welcome-image">
              <img src="@/assets/stock-analysis.svg" alt="Stock Analysis" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card class="market-summary-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>市场概览</span>
            </div>
          </template>
          <div class="market-indexes">
            <div class="index-item" :class="marketIndex.change >= 0 ? 'positive' : 'negative'">
              <div class="index-name">{{ selectedMarket === 'TW' ? '加權指數' : 'S&P 500' }}</div>
              <div class="index-price">{{ formatPrice(marketIndex.price) }}</div>
              <div class="index-change">
                {{ marketIndex.change >= 0 ? '+' : '' }}{{ formatPrice(marketIndex.change) }}
                ({{ marketIndex.change >= 0 ? '+' : '' }}{{ formatPercent(marketIndex.change) }}%)
                <el-icon v-if="marketIndex.change >= 0"><CaretTop /></el-icon>
                <el-icon v-else><CaretBottom /></el-icon>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-content">
      <!-- 热门股票列表 -->
      <el-col :xs="24" :lg="16">
        <el-card class="stock-list-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="title-section">
                <el-icon><Coin /></el-icon>
                <span>{{ selectedMarket === 'TW' ? '台灣熱門股票' : '美國熱門股票' }}</span>
              </div>
              <div class="action-section">
                <el-autocomplete
                    class="search-input"
                    v-model="searchQuery"
                    :fetch-suggestions="querySearch"
                    placeholder="搜索股票代碼或名稱"
                    @select="handleSelect"
                    :trigger-on-focus="false"
                    clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                  <template #default="{ item }">
                    <div class="search-result-item">
                      <span class="symbol">{{ item.symbol }}</span>
                      <span class="name">{{ item.name }}</span>
                      <span class="market-tag" :class="item.market === 'TW' ? 'tw-tag' : 'us-tag'">
                  {{ item.market }}
                </span>
                    </div>
                  </template>
                </el-autocomplete>
              </div>
            </div>
          </template>

          <el-table
              :data="filteredStocks"
              v-loading="loading"
              class="stock-table"
              @row-click="viewStockDetail"
              stripe
              highlight-current-row
          >
            <el-table-column prop="symbol" label="代码" width="100">
              <template #default="scope">
                <span class="symbol-text">{{ scope.row.symbol }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="name" label="名称" min-width="140">
              <template #default="scope">
                <div class="name-cell">
                  <span class="name-text">{{ scope.row.name }}</span>
                  <span v-if="scope.row.chinese_name" class="chinese-name">{{ scope.row.chinese_name }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="industry" label="行业" width="120">
              <template #default="scope">
                <el-tag size="small" effect="plain">{{ scope.row.industry }}</el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="price" label="当前价格" width="100" align="right">
              <template #default="scope">
                <span class="price">{{ formatPrice(scope.row.price) }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="change" label="涨跌" width="120" align="right">
              <template #default="scope">
                <div class="change-cell">
            <span :class="['change', scope.row.change >= 0 ? 'positive' : 'negative']">
              {{ scope.row.change >= 0 ? '+' : '' }}{{ formatPrice(scope.row.change) }}
            </span>
                  <el-icon v-if="scope.row.change > 0"><ArrowUp class="up-icon" /></el-icon>
                  <el-icon v-else-if="scope.row.change < 0"><ArrowDown class="down-icon" /></el-icon>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="changePercent" label="涨跌幅" width="120" align="right">
              <template #default="scope">
                <div class="percent-badge" :class="scope.row.change >= 0 ? 'positive-bg' : 'negative-bg'">
                  {{ scope.row.change >= 0 ? '+' : '' }}{{ formatPercent(scope.row.change) }}%
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="80" fixed="right">
              <template #default="scope">
                <el-button
                    type="primary"
                    size="small"
                    @click.stop="viewStockDetail(scope.row)"
                    class="view-button"
                >
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 新增分页组件 -->
          <div class="pagination-container">
            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="totalStocks"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                background
            />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧栏 -->
      <el-col :xs="24" :lg="8">
        <!-- 股票趋势预测卡片 -->
        <el-card class="prediction-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Histogram /></el-icon>
              <span>热门股票趋势</span>
            </div>
          </template>
          <div class="chart-container" v-if="selectedStockChart">
            <KLineChart :data="selectedStockChart" />
          </div>
          <div v-else class="empty-chart">
            <el-icon><DataLine /></el-icon>
            <p>从列表选择股票查看详细趋势</p>
          </div>
        </el-card>

        <!-- 新闻情感分析 -->
        <el-card class="sentiment-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><ChatLineRound /></el-icon>
              <span>市场情绪分析</span>
            </div>
          </template>

          <div v-if="sentimentSummary" class="sentiment-summary">
            <div class="sentiment-gauge">
              <el-progress type="dashboard" :percentage="sentimentScore" :color="sentimentColor" :stroke-width="12">
                <template #default>
                  <div class="sentiment-status">
                    <div class="status-label">{{ sentimentLabel }}</div>
                    <div class="status-score">{{ sentimentScore }}%</div>
                  </div>
                </template>
              </el-progress>
            </div>

            <el-row :gutter="10" class="sentiment-stats">
              <el-col :span="8">
                <div class="stat positive">
                  <div class="stat-value">{{ sentimentSummary.positive }}</div>
                  <div class="stat-label">
                    <el-icon><TopRight /></el-icon>
                    看涨
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat neutral">
                  <div class="stat-value">{{ sentimentSummary.neutral }}</div>
                  <div class="stat-label">
                    <el-icon><Right /></el-icon>
                    持平
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat negative">
                  <div class="stat-value">{{ sentimentSummary.negative }}</div>
                  <div class="stat-label">
                    <el-icon><BottomRight /></el-icon>
                    看跌
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
          <div v-else class="empty-sentiment">
            <el-icon><Loading /></el-icon>
            <p>分析市场情绪中...</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 股票详情弹窗 -->
    <el-dialog
        v-model="stockDetailVisible"
        title="股票详情"
        width="80%"
        destroy-on-close
        class="stock-detail-dialog"
    >
      <div v-if="currentStock" class="stock-detail-content">
        <div class="stock-header">
          <h2>{{ currentStock.name }} ({{ currentStock.symbol }})</h2>
          <div class="stock-price">
            <span class="price">{{ formatPrice(currentStock.price) }}</span>
            <span :class="['change', currentStock.change >= 0 ? 'positive' : 'negative']">
              {{ currentStock.change >= 0 ? '+' : '' }}{{ formatPrice(currentStock.change) }}
              ({{ currentStock.change >= 0 ? '+' : '' }}{{ formatPercent(currentStock.change) }}%)
            </span>
          </div>
        </div>

        <el-divider />

        <el-row :gutter="20" class="stock-detail-body">
          <el-col :xs="24" :md="12">
            <div class="chart-section">
              <h3>K线走势图</h3>
              <div class="chart-container detail-chart">
                <KLineChart v-if="currentStockChart" :data="currentStockChart" />
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :md="12">
            <div class="chart-section">
              <h3>价格预测</h3>
              <div class="chart-container detail-chart">
                <PredictionChart v-if="predictionChart" :data="predictionChart" />
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-dialog>

    <el-alert
        v-if="error"
        :title="error"
        type="error"
        class="error-alert"
        show-icon
        closable
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStockStore } from '@/stores/stockStore'
import { useSentimentStore } from '@/stores/sentimentStore'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import KLineChart from '@/components/KLineChart.vue'
import PredictionChart from '@/components/PredictionChart.vue'
import {
  Refresh, TrendCharts, Coin, Search, ArrowUp, ArrowDown,
  Histogram, DataLine, ChatLineRound, CaretTop, CaretBottom,
  TopRight, Right, BottomRight, Loading
} from '@element-plus/icons-vue'

// Router
const router = useRouter()

// Stores
const stockStore = useStockStore()
const sentimentStore = useSentimentStore()

// Store refs
const { stocks, loading, error, currentStock, stockChart, predictionChart, filteredStocks, currentMarket } = storeToRefs(stockStore)
const { sentimentSummary } = storeToRefs(sentimentStore)

// Local state
const searchQuery = ref('')
const stockDetailVisible = ref(false)
const selectedStockChart = ref(null)
const selectedMarket = ref('TW')
const currentPage = ref(1)
const pageSize = ref(10)
const totalStocks = ref(0)
const marketIndex = ref({
  name: '加權指數',
  price: 18902.35,
  change: 82.45,
  changePercent: 0.44
})

// Computed
const sentimentScore = computed(() => {
  if (!sentimentSummary.value) return 50

  const total = sentimentSummary.value.positive +
      sentimentSummary.value.neutral +
      sentimentSummary.value.negative

  if (total === 0) return 50

  return Math.round((sentimentSummary.value.positive * 100 +
      sentimentSummary.value.neutral * 50) / total)
})

const sentimentLabel = computed(() => {
  const score = sentimentScore.value
  if (score >= 70) return '强烈看涨'
  if (score >= 60) return '看涨'
  if (score >= 45) return '中性偏多'
  if (score >= 40) return '中性'
  if (score >= 30) return '中性偏空'
  if (score >= 20) return '看跌'
  return '强烈看跌'
})

const sentimentColor = computed(() => {
  const score = sentimentScore.value
  if (score >= 70) return '#67c23a'
  if (score >= 60) return '#85ce61'
  if (score >= 45) return '#a0cfff'
  if (score >= 40) return '#909399'
  if (score >= 30) return '#f89898'
  if (score >= 20) return '#f56c6c'
  return '#e24646'
})

const currentStockChart = computed(() => {
  return stockChart.value
})

// Methods
const refreshDashboard = () => {
  stockStore.fetchStocks(selectedMarket.value, currentPage.value, pageSize.value)
  sentimentStore.fetchSentimentData()

  // 更新市场指数数据
  if (selectedMarket.value === 'TW') {
    marketIndex.value = {
      name: '加權指數',
      price: 18902.35,
      change: 82.45,
      changePercent: 0.44
    }
  } else {
    marketIndex.value = {
      name: 'S&P 500',
      price: 4802.35,
      change: 12.45,
      changePercent: 0.26
    }
  }

  ElMessage({
    message: '数据已刷新',
    type: 'success'
  })
}

const formatPrice = (price) => {
  if (price === undefined || price === null) return '-'
  return Number(price).toFixed(2)
}

const formatPercent = (change) => {
  if (change === undefined || change === null) return '-'
  return Math.abs(Number(change)).toFixed(2)
}

const viewStockDetail = (row) => {
  // 通过路由导航到分析页
  const encodedSymbol = encodeURIComponent(row.symbol)
  router.push({
    name: 'CompanyAnalysis',
    params: { symbol: encodedSymbol }
  })
}

const switchMarket = (market) => {
  // 切换市场时重置页码
  currentPage.value = 1
  stockStore.switchMarket(market, pageSize.value)

  // 更新市场指数数据
  if (market === 'TW') {
    marketIndex.value = {
      name: '加權指數',
      price: 18902.35,
      change: 82.45,
      changePercent: 0.44
    }
  } else {
    marketIndex.value = {
      name: 'S&P 500',
      price: 4802.35,
      change: 12.45,
      changePercent: 0.26
    }
  }
}


// 处理页码变化
const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
  stockStore.fetchStocks(selectedMarket.value, newPage, pageSize.value)
}


// 处理每页条数变化
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  stockStore.fetchStocks(selectedMarket.value, currentPage.value, newSize)
}

// 股票搜索
const querySearch = async (queryString, cb) => {
  if (queryString.length < 1) {
    cb([])
    return
  }

  try {
    const results = await stockStore.searchStocks(queryString)
    cb(results)
  } catch (error) {
    console.error('搜索失敗:', error)
    cb([])
  }
}

const handleSelect = (item) => {
  if (item.market !== selectedMarket.value) {
    selectedMarket.value = item.market
    stockStore.switchMarket(item.market)
  }

  // 查看股票詳情
  viewStockDetail(item)

  // 清空搜索框
  searchQuery.value = ''
}

watch(() => selectedMarket.value, (newMarket) => {
  stockStore.switchMarket(newMarket)
})

onMounted(() => {
  // 初始化股票数据
  stockStore.initializeData(pageSize.value)
  sentimentStore.fetchSentimentData()

  // 监听分页数据
  watch(() => stockStore.pagination, (newPagination) => {
    if (newPagination) {
      totalStocks.value = newPagination.total
    }
  }, { deep: true })

  // 模拟数据 - 实际应用中应该从API获取
  setTimeout(() => {
    if (stocks.value.length > 0) {
      const randomIndex = Math.floor(Math.random() * Math.min(5, stocks.value.length))
      const randomStock = stocks.value[randomIndex]
      if (randomStock) {
        stockStore.fetchStockDetail(randomStock.symbol)
        selectedStockChart.value = stockStore.generateMockChartData()
      }
    }
  }, 1000)
})
</script>

<style scoped>
.stock-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 20px;
}

.welcome-card {
  height: 100%;
}

.welcome-content {
  display: flex;
  align-items: center;
  gap: 30px;
}

.welcome-text {
  flex: 1;
}

.welcome-text h1 {
  margin-top: 0;
  color: var(--el-color-primary);
  font-size: 2rem;
  margin-bottom: 16px;
}

.welcome-text p {
  color: #606266;
  margin-bottom: 24px;
  line-height: 1.6;
  font-size: 1.1rem;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.welcome-image {
  width: 180px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.welcome-image img {
  max-width: 100%;
  height: auto;
}

.market-summary-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.market-indexes {
  padding: 10px 0;
}

.index-item {
  padding: 15px;
  border-radius: 8px;
  background-color: #f8f9fa;
  transition: transform 0.3s;
}

.index-item:hover {
  transform: translateY(-2px);
}

.index-name {
  font-size: 1rem;
  color: #606266;
  margin-bottom: 8px;
}

.index-price {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.index-change {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 600;
}

.positive .index-price,
.positive .index-change {
  color: #67c23a;
}

.negative .index-price,
.negative .index-change {
  color: #f56c6c;
}


/* 在 Dashboard.vue 的 <style scoped> 部分添加 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.stock-list-card {
  height: 100%;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-section {
  display: flex;
  gap: 8px;
}

.search-input {
  width: 220px;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-result-item .symbol {
  font-weight: bold;
  color: #303133;
}

.search-result-item .name {
  color: #606266;
}

.market-tag {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  color: white;
}

.tw-tag {
  background-color: #409EFF;
}

.us-tag {
  background-color: #67C23A;
}

.stock-table {
  cursor: pointer;
}

.symbol-text {
  font-family: 'Roboto Mono', monospace;
  font-weight: 600;
}

.name-cell {
  display: flex;
  flex-direction: column;
}

.name-text {
  font-weight: 500;
}

.chinese-name {
  font-size: 12px;
  color: #909399;
}

.price {
  font-weight: 600;
  font-family: 'Roboto Mono', monospace;
}

.change-cell {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}

.change {
  font-weight: 600;
  font-family: 'Roboto Mono', monospace;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}

.up-icon {
  color: #67c23a;
}

.down-icon {
  color: #f56c6c;
}

.percent-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.8rem;
  color: white;
}

.positive-bg {
  background-color: #67c23a;
}

.negative-bg {
  background-color: #f56c6c;
}

.view-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.prediction-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 280px;
  position: relative;
}

.empty-chart {
  height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.empty-chart .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.sentiment-card {
  margin-bottom: 20px;
}

.sentiment-summary {
  padding: 10px 0;
}

.sentiment-gauge {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.sentiment-status {
  text-align: center;
}

.status-label {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 5px;
}

.status-score {
  font-size: 24px;
  font-weight: bold;
}

.sentiment-stats {
  margin-top: 20px;
  text-align: center;
}

.stat {
  padding: 10px;
  border-radius: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 14px;
}

.stat.positive {
  color: #67c23a;
}

.stat.neutral {
  color: #909399;
}

.stat.negative {
  color: #f56c6c;
}

.empty-sentiment {
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
}

.empty-sentiment .el-icon {
  font-size: 40px;
  margin-bottom: 16px;
}

/* Stock detail dialog */
.stock-detail-dialog :deep(.el-dialog__header) {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

.stock-detail-content {
  padding: 0 20px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-header h2 {
  margin: 0;
  color: #303133;
}

.stock-price {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stock-price .price {
  font-size: 24px;
}

.detail-chart {
  height: 350px;
}

.chart-section h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #303133;
}

.error-alert {
  margin-top: 20px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    text-align: center;
  }

  .welcome-image {
    width: 140px;
    margin: 0 auto;
  }

  .stock-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .stock-price {
    align-self: flex-start;
  }

  .action-buttons {
    justify-content: center;
  }
}
</style>
