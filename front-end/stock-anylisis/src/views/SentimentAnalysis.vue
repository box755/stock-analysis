<template>
  <div class="sentiment-analysis">
    <el-card class="header-card">
      <template #header>
        <div class="card-header">
          <span>情感分析</span>
          <div class="header-actions">
            <el-select
                v-model="selectedCompany"
                placeholder="选择公司"
                style="margin-right: 10px; width: 150px"
                @change="handleCompanyChange"
            >
              <el-option
                  v-for="company in companies"
                  :key="company"
                  :label="company === 'all' ? '全部公司' : company"
                  :value="company"
              />
            </el-select>
            <el-button
                type="primary"
                @click="refreshData"
                :loading="loading"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 情感分析摘要 -->
      <div v-if="sentimentSummary" class="summary-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总数据量" :value="sentimentSummary.total" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="平均影响力" :value="sentimentSummary.avgImpact" suffix="%" />
          </el-col>
          <el-col :span="4">
            <el-statistic title="正面" :value="sentimentSummary.positive">
              <template #suffix>
                <el-icon style="color: #67c23a;"><CaretTop /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="4">
            <el-statistic title="中性" :value="sentimentSummary.neutral">
              <template #suffix>
                <el-icon style="color: #e6a23c;"><Minus /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="4">
            <el-statistic title="负面" :value="sentimentSummary.negative">
              <template #suffix>
                <el-icon style="color: #f56c6c;"><CaretBottom /></el-icon>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 情感数据列表 -->
    <el-card class="data-card">
      <template #header>
        <h3>情感分析数据</h3>
      </template>

      <div v-loading="loading" class="sentiment-list">
        <div
            v-for="item in filteredSentimentData"
            :key="item.time_iso"
            class="sentiment-item"
        >
          <div class="item-header">
            <div class="company-info">
              <el-tag type="primary" size="small">{{ item.company }}</el-tag>
              <span class="date">{{ formatDate(item.time_iso) }}</span>
            </div>
            <div class="impact-score">
              <span class="score-label">影响力评分：</span>
              <el-progress
                  :percentage="item.impact_pct"
                  :color="getScoreColor(item.impact_pct)"
                  :status="getScoreStatus(item.impact_pct)"
                  :stroke-width="8"
                  style="width: 200px;"
              />
              <span class="score-value">{{ item.impact_pct }}%</span>
            </div>
          </div>

          <div class="item-content">
            <p class="news-text">{{ getShortText(item.text) }}</p>
            <el-button
                type="text"
                size="small"
                @click="toggleTextExpansion(item)"
                v-if="item.text.length > 200"
            >
              {{ item.expanded ? '收起' : '展开' }}
            </el-button>
          </div>
        </div>

        <el-empty v-if="filteredSentimentData.length === 0 && !loading" description="暂无数据" />
      </div>
    </el-card>

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
import { onMounted } from 'vue'
import { useSentimentStore } from '@/stores/sentimentStore'
import { storeToRefs } from 'pinia'
import dayjs from 'dayjs'

const sentimentStore = useSentimentStore()
const {
  filteredSentimentData,
  loading,
  error,
  companies,
  selectedCompany,
  sentimentSummary
} = storeToRefs(sentimentStore)

const refreshData = () => {
  sentimentStore.fetchSentimentData()
}

const handleCompanyChange = (company) => {
  sentimentStore.setSelectedCompany(company)
}

const formatDate = (timeIso) => {
  return dayjs(timeIso).format('YYYY年MM月DD日 HH:mm')
}

const getScoreColor = (score) => {
  if (score >= 60) return '#67c23a'
  if (score >= 40) return '#e6a23c'
  return '#f56c6c'
}

const getScoreStatus = (score) => {
  if (score >= 60) return 'success'
  if (score >= 40) return 'warning'
  return 'exception'
}

const getShortText = (text) => {
  return text.length > 200 ? text.substring(0, 200) + '...' : text
}

const toggleTextExpansion = (item) => {
  item.expanded = !item.expanded
}

onMounted(() => {
  sentimentStore.fetchSentimentData()
})
</script>

<style scoped>
.sentiment-analysis {
  max-width: 1200px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.summary-section {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.data-card {
  margin-bottom: 20px;
}

.sentiment-list {
  max-height: 600px;
  overflow-y: auto;
}

.sentiment-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background: white;
  transition: box-shadow 0.3s;
}

.sentiment-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.company-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date {
  color: #909399;
  font-size: 14px;
}

.impact-score {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-label {
  font-size: 14px;
  color: #606266;
}

.score-value {
  font-weight: 600;
  color: #303133;
  min-width: 50px;
}

.item-content {
  color: #606266;
  line-height: 1.6;
}

.news-text {
  margin: 0;
  word-break: break-all;
}

.error-alert {
  margin-top: 20px;
}
</style>
