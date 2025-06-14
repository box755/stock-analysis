<template>
  <div class="stock-detail" v-loading="loading">
    <el-button
        @click="goBack"
        class="back-button"
        type="primary"
        plain
    >
      <el-icon><ArrowLeft /></el-icon>
      返回股票列表
    </el-button>

    <div v-if="currentStock" class="stock-content">
      <!-- 股票基本信息 -->
      <el-card class="stock-info-card">
        <template #header>
          <div class="stock-header">
            <h2>{{ currentStock.name }} ({{ currentStock.symbol }})</h2>
            <div class="stock-price">
              <span class="price">{{ currentStock.price }}</span>
              <span :class="['change', currentStock.change >= 0 ? 'positive' : 'negative']">
                {{ currentStock.change >= 0 ? '+' : '' }}{{ currentStock.change }}
                ({{ currentStock.change >= 0 ? '+' : '' }}{{ currentStock.changePercent }}%)
              </span>
            </div>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="8">
            <div class="info-item">
              <span class="label">市值：</span>
              <span class="value">{{ currentStock.marketCap }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <span class="label">市盈率：</span>
              <span class="value">{{ currentStock.pe }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <span class="label">股息率：</span>
              <span class="value">{{ currentStock.dividend }}%</span>
            </div>
          </el-col>
        </el-row>

        <p class="description">{{ currentStock.description }}</p>
      </el-card>

      <!-- 图表区域 -->
      <el-row :gutter="20" class="charts-row">
        <!-- K线图 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <h3>K线图</h3>
            </template>
            <div class="chart-container">
              <KLineChart v-if="stockChart" :data="stockChart" />
              <div v-else class="chart-placeholder">
                <el-icon><Loading /></el-icon>
                <p>加载中...</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 预测图 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <h3>价格预测</h3>
            </template>
            <div class="chart-container">
              <PredictionChart v-if="predictionChart" :data="predictionChart" />
              <div v-else class="chart-placeholder">
                <el-icon><Loading /></el-icon>
                <p>加载中...</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-alert
        v-if="error"
        :title="error"
        type="error"
        class="error-alert"
        show-icon
    />
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStockStore } from '@/stores/stockStore'
import { storeToRefs } from 'pinia'
import KLineChart from '@/components/KLineChart.vue'
import PredictionChart from '@/components/PredictionChart.vue'

const props = defineProps({
  symbol: {
    type: String,
    required: true
  }
})

const router = useRouter()
const stockStore = useStockStore()
const { currentStock, stockChart, predictionChart, loading, error } = storeToRefs(stockStore)

const goBack = () => {
  router.push('/stocks')
}

const loadStockDetail = () => {
  stockStore.fetchStockDetail(props.symbol)
}

watch(() => props.symbol, loadStockDetail, { immediate: true })

onMounted(() => {
  loadStockDetail()
})
</script>

<style scoped>
.stock-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.back-button {
  margin-bottom: 20px;
}

.stock-info-card {
  margin-bottom: 20px;
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

.price {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.change.positive {
  color: #67c23a;
  font-weight: 600;
}

.change.negative {
  color: #f56c6c;
  font-weight: 600;
}

.info-item {
  margin-bottom: 10px;
}

.info-item .label {
  color: #909399;
  margin-right: 5px;
}

.info-item .value {
  color: #303133;
  font-weight: 600;
}

.description {
  margin-top: 20px;
  color: #606266;
  line-height: 1.6;
}

.charts-row {
  margin-top: 20px;
}

.chart-container {
  height: 400px;
  position: relative;
}

.chart-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
}

.chart-placeholder .el-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.error-alert {
  margin-top: 20px;
}
</style>
