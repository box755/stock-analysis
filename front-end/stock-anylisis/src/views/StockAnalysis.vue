<template>
  <div class="stock-analysis">
    <el-button @click="goBack" class="back-button">
      <el-icon><ArrowLeft /></el-icon>
      返回公司列表
    </el-button>

    <div class="analysis-container" v-if="companyInfo">
      <!-- 左側 60% -->
      <div class="charts-section">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <h3>{{ companyInfo.name }} ({{ companyInfo.symbol }})</h3>
            </div>
          </template>
          <!-- K線圖 -->
          <StockCharts
            :stock-data="stockData"
            :prediction-data="predictionData"
          />
        </el-card>

        <!-- AI 分析結果 -->
        <AIAnalysis
          v-if="stockAnalysis"
          :stock-analysis="stockAnalysis"
          :news-analysis="newsAnalysis"
          :combined-suggestion="combinedSuggestion"
        />
      </div>

      <!-- 右側 40% -->
      <div class="news-section">
        <NewsList
          :news-list="newsList"
          @analyze="analyzeNews"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import StockCharts from '../components/StockCharts.vue'
import NewsList from '../components/NewsList.vue'
import AIAnalysis from '../components/AIAnalysis.vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const symbol = ref(route.params.symbol)

// 初始化所需的響應式數據
const companyInfo = ref(null)
const stockData = ref(null)
const predictionData = ref(null)
const newsList = ref([])
const stockAnalysis = ref(null)
const newsAnalysis = ref(null)
const combinedSuggestion = ref(null)

// 載入公司資訊
const loadCompanyInfo = async () => {
  try {
    const response = await axios.get(`http://localhost:5001/api/companies/${symbol.value}`)
    companyInfo.value = response.data
  } catch (error) {
    ElMessage.error('無法載入公司資訊')
    console.error(error)
  }
}

// 載入股票數據
const loadStockData = async () => {
  try {
    const response = await axios.get(`http://localhost:5001/api/stocks/${symbol.value}`)
    stockData.value = response.data
  } catch (error) {
    ElMessage.error('無法載入股票數據')
    console.error(error)
  }
}

// 載入新聞列表
const loadNews = async () => {
  try {
    const response = await axios.get(`http://localhost:5001/api/news/${symbol.value}`)
    newsList.value = response.data
  } catch (error) {
    ElMessage.error('無法載入新聞數據')
    console.error(error)
  }
}

// 返回列表頁面
const goBack = () => {
  router.push('/')
}

// 當組件掛載時載入數據
onMounted(async () => {
  if (symbol.value) {
    await Promise.all([
      loadCompanyInfo(),
      loadStockData(),
      loadNews()
    ])
  }
})
</script>

<style scoped>
.stock-analysis {
  padding: 20px;
}

.back-button {
  margin-bottom: 20px;
}

.analysis-container {
  display: flex;
  gap: 20px;
}

.charts-section {
  flex: 0 0 60%;
}

.news-section {
  flex: 0 0 40%;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>