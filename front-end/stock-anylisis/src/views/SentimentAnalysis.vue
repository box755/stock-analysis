<template>
  <div class="sentiment-analysis">
    <el-card class="news-list-card">
      <template #header>
        <div class="card-header">
          <h2>新聞情感分析</h2>
          <el-button type="primary" @click="refreshNews" :loading="loading">
            刷新數據
          </el-button>
        </div>
      </template>

      <!-- 新聞列表 -->
      <el-table
        v-loading="loading"
        :data="newsList"
        style="width: 100%"
      >
        <el-table-column
          prop="date"
          label="日期"
          width="120"
          sortable
        />
        <el-table-column
          prop="company"
          label="公司"
          width="120"
        />
        <el-table-column
          prop="text"
          label="新聞內容"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <div class="news-content">
              {{ row.text }}
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="impact_pct"
          label="影響程度"
          width="120"
          sortable
        >
          <template #default="{ row }">
            <el-tag :type="getImpactLevel(row.impact_pct)">
              {{ row.impact_pct }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="120"
          fixed="right"
        >
          <template #default="{ $index }">
            <el-button
              size="small"
              type="primary"
              @click="analyzeNews($index)"
              :loading="analyzing === $index"
            >
              分析
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分析結果對話框 -->
      <el-dialog
        v-model="showAnalysis"
        title="AI 分析結果"
        width="50%"
      >
        <div v-if="currentAnalysis" class="analysis-content">
          {{ currentAnalysis }}
        </div>
      </el-dialog>
    </el-card>

    <pre>{{ newsList }}</pre> <!-- 測試用：顯示原始數據 -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const newsList = ref([])
const loading = ref(false)
const analyzing = ref(null)
const showAnalysis = ref(false)
const currentAnalysis = ref('')

// 載入新聞數據
const fetchNews = async () => {
  loading.value = true
  try {
    console.log('開始獲取新聞數據...')
    const response = await axios.get('http://localhost:5001/api/news')
    console.log('獲取數據成功:', response.data)
    newsList.value = response.data
  } catch (error) {
    console.error('獲取新聞數據失敗:', error)
    ElMessage.error(`獲取新聞數據失敗: ${error.response?.data?.error || error.message}`)
  } finally {
    loading.value = false
  }
}

// 分析新聞
const analyzeNews = async (index) => {
  analyzing.value = index
  try {
    const response = await axios.get(`http://localhost:5001/api/analyze/${index}`)
    currentAnalysis.value = response.data.analysis
    showAnalysis.value = true
  } catch (error) {
    ElMessage.error('分析新聞失敗')
    console.error(error)
  } finally {
    analyzing.value = null
  }
}

// 根據影響程度返回標籤類型
const getImpactLevel = (impact) => {
  if (impact >= 70) return 'danger'
  if (impact >= 50) return 'warning'
  return 'info'
}

// 刷新數據
const refreshNews = () => {
  fetchNews()
}

onMounted(() => {
  fetchNews()
})
</script>

<style scoped>
.sentiment-analysis {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-content {
  max-height: 3em;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.analysis-content {
  white-space: pre-line;
  line-height: 1.6;
}
</style>
