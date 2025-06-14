<template>
  <div class="company-analysis">
    <!-- 頁面標題 -->
    <div class="page-header">
      <el-button @click="goBack" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <h2 v-if="companyInfo">
        {{ companyInfo.name }} ({{ companyInfo.symbol }})
      </h2>
      <el-button
        type="success"
        size="small"
        @click="generateAIAnalysis"
        :loading="generatingAnalysis"
      >
        <el-icon><ChatLineRound /></el-icon>
        更新 AI 分析
      </el-button>
    </div>

    <!-- AI 綜合分析區塊 -->
    <el-card class="ai-analysis-card" v-if="aiAnalysis">
      <div class="ai-content">
        <el-alert
          :title="getAISentiment(aiAnalysis.sentiment)"
          :type="getAISentimentType(aiAnalysis.sentiment)"
          :description="aiAnalysis.summary"
          :closable="false"
          show-icon
        />
        <div class="ai-suggestions">
          <h4>投資建議：</h4>
          <ul>
            <li
              v-for="(suggestion, index) in aiAnalysis.suggestions"
              :key="index"
            >
              {{ suggestion }}
            </li>
          </ul>
        </div>
      </div>
    </el-card>

    <!-- 主要內容區 -->
    <div class="main-content">
      <!-- K線圖區域 -->
      <div class="chart-section">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>股價走勢</h3>
              <el-select v-model="timeRange" size="small">
                <el-option label="1個月" value="1M" />
                <el-option label="3個月" value="3M" />
                <el-option label="6個月" value="6M" />
              </el-select>
            </div>
          </template>
          <div class="chart-container">
            <KLineChart :data="stockData" />
          </div>
        </el-card>
      </div>

      <!-- 新聞列表區域 -->
      <div class="news-section">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>相關新聞</h3>
              <el-button type="primary" size="small" @click="refreshNews">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div class="news-list">
            <div
              v-for="news in newsList"
              :key="news.id"
              class="news-item"
              @click="showNewsDetail(news)"
            >
              <el-card shadow="hover" class="news-card">
                <div class="news-header">
                  <span class="news-date">{{ formatDate(news.date) }}</span>
                  <el-tag
                    :type="getSentimentType(news.impact_pct)"
                    size="small"
                  >
                    情感分數: {{ news.impact_pct }}%
                  </el-tag>
                </div>
                <div class="news-preview">
                  {{ truncateText(news.text, 100) }}
                </div>
              </el-card>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 新聞詳情對話框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="formatDate(selectedNews?.date)"
      width="50%"
    >
      <div class="news-detail">
        <p class="news-content">{{ selectedNews?.text }}</p>
        <div class="news-analysis">
          <h4>
            情感分析分數：
            <el-tag :type="getSentimentType(selectedNews?.impact_pct)">
              {{ selectedNews?.impact_pct }}%
            </el-tag>
          </h4>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import KLineChart from "../components/KLineChart.vue"; // 確保路徑正確
import axios from "axios";
import { ElMessage } from "element-plus";
import { format } from "date-fns";
import { ChatLineRound } from "@element-plus/icons-vue";

const router = useRouter();

const props = defineProps({
  symbol: {
    type: String,
    required: true,
  },
});

const symbol = ref(props.symbol);

const companyInfo = ref(null);
const stockData = ref([]);
const newsList = ref([]);
const loading = ref(false);
const timeRange = ref("1M");
const dialogVisible = ref(false);
const selectedNews = ref(null);
const aiAnalysis = ref(null);
const generatingAnalysis = ref(false);

// 格式化股價資料
const formatStockData = (data) => {
  return data.map((item) => ({
    date: item.date,
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    volume: item.volume,
  }));
};

// 載入公司資訊和新聞資料
const loadData = async () => {
  loading.value = true;
  try {
    // 確保 symbol 存在
    if (!symbol.value) {
      throw new Error("未指定公司代碼");
    }

    const encodedSymbol = encodeURIComponent(symbol.value);

    // 使用 Promise.all 並加入錯誤處理
    const [stockResp, newsResp] = await Promise.all([
      axios
        .get(`http://localhost:5001/api/stocks/${encodedSymbol}`)
        .catch((error) => {
          console.error("載入股價數據失敗:", error);
          return { data: [] };
        }),
      axios
        .get(`http://localhost:5001/api/news/${encodedSymbol}`)
        .catch((error) => {
          console.error("載入新聞數據失敗:", error);
          return { data: [] };
        }),
    ]);

    // 更新數據
    if (stockResp.data) {
      stockData.value = stockResp.data;
    }

    if (newsResp.data) {
      newsList.value = newsResp.data;
      // 更新公司資訊
      companyInfo.value = {
        symbol: symbol.value,
        name: newsResp.data[0]?.company || symbol.value,
      };
    }
  } catch (error) {
    console.error("數據載入失敗:", error);
    ElMessage.error("無法載入公司資料，請稍後再試");
  } finally {
    loading.value = false;
  }
};

const showNewsDetail = (news) => {
  selectedNews.value = news;
  dialogVisible.value = true;
};

const getSentimentType = (score) => {
  if (score >= 60) return "success";
  if (score <= 40) return "danger";
  return "warning";
};

const goBack = () => router.push("/");
const refreshNews = () => loadData();

// 格式化日期
const formatDate = (date) => {
  try {
    return format(new Date(date), "yyyy/MM/dd");
  } catch {
    return date;
  }
};

// 截斷文字
const truncateText = (text, length) => {
  if (!text) return "";
  return text.length > length ? text.slice(0, length) + "..." : text;
};

// 生成 AI 分析
const generateAIAnalysis = async () => {
  generatingAnalysis.value = true;
  try {
    const response = await axios.post(
      "http://localhost:5001/api/analyze/sentiment",
      {
        company: symbol.value,
        news: newsList.value,
      }
    );

    aiAnalysis.value = response.data;
    ElMessage.success("AI 分析完成");
  } catch (error) {
    console.error("AI 分析生成失敗:", error);

    let errorMessage = "分析生成失敗";
    if (error.response) {
      // 服務器回應錯誤
      errorMessage = error.response.data?.error || errorMessage;
    } else if (error.request) {
      // 請求發送失敗
      errorMessage = "無法連接到分析服務，請確認服務是否運行";
    }

    ElMessage.error(errorMessage);
  } finally {
    generatingAnalysis.value = false;
  }
};

// 取得 AI 情感評價文字
const getAISentiment = (sentiment) => {
  const sentiments = {
    positive: "整體評價：正面 📈",
    neutral: "整體評價：中性 ➡️",
    negative: "整體評價：負面 📉",
  };
  return sentiments[sentiment] || "評價待定";
};

// 取得 AI 情感類型
const getAISentimentType = (sentiment) => {
  const types = {
    positive: "success",
    neutral: "info",
    negative: "warning",
  };
  return types[sentiment] || "info";
};

// 監聽 symbol 變化
watch(
  () => props.symbol,
  (newSymbol) => {
    if (newSymbol) {
      symbol.value = newSymbol;
      loadData();
    }
  }
);

// 初始化載入
onMounted(() => {
  if (symbol.value) {
    loadData();
  }
});
</script>

<style scoped>
.company-analysis {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.ai-analysis-card {
  margin-bottom: 20px;
  background: linear-gradient(to right, #f0f9ff, #ffffff);
}

.ai-content {
  padding: 15px;
}

.ai-suggestions {
  margin-top: 15px;
  padding: 15px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
}

.main-content {
  display: flex;
  gap: 20px;
}

.chart-section {
  flex: 0 0 60%;
}

.news-section {
  flex: 0 0 40%;
}

.chart-container {
  height: 400px;
}

.news-list {
  max-height: 600px;
  overflow-y: auto;
}

.news-title {
  cursor: pointer;
  color: #409eff;
}

.news-title:hover {
  text-decoration: underline;
}

.news-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.news-item:hover {
  transform: translateX(5px);
}

.news-card {
  border-left: 4px solid transparent;
}

.news-card:hover {
  border-left-color: #409eff;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.news-date {
  color: #909399;
  font-size: 14px;
}

.news-preview {
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.news-detail {
  padding: 20px;
}

.news-content {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 20px;
  white-space: pre-line;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-analysis-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>