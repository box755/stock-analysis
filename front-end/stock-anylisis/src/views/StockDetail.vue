<template>
  <div class="stock-detail">
    <div class="back-link">
      <el-button @click="goBack" size="small">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
    </div>

    <h2 class="stock-title">{{ currentStock?.name || "" }} ({{ symbol }})</h2>

    <!-- 原有的股價走勢圖區塊 -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><TrendCharts /></el-icon>
          <span>股價走勢</span>
          <div class="time-filter">
            <el-radio-group v-model="timeRange" size="small">
              <el-radio-button value="1w">1週</el-radio-button>
              <el-radio-button value="1m">1月</el-radio-button>
              <el-radio-button value="3m">3月</el-radio-button>
              <el-radio-button value="6m">6月</el-radio-button>
              <el-radio-button value="1y">1年</el-radio-button>
              <el-radio-button value="all">全部</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      <div class="chart-container" v-if="stockChart && stockChart.length > 0">
        <KLineChart :data="filteredStockChart" />
      </div>
      <div class="empty-chart" v-else>
        <el-empty description="暫無股價數據" />
      </div>
    </el-card>

    <!-- 新增的股價預測區塊 -->
    <el-card class="prediction-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>股價預測分析</span>
          <div class="prediction-actions">
            <el-select
              v-model="predictionDays"
              size="small"
              placeholder="預測天數"
            >
              <el-option label="5 天" :value="5" />
              <el-option label="10 天" :value="10" />
              <el-option label="15 天" :value="15" />
            </el-select>
            <el-button
              size="small"
              type="primary"
              @click="loadPrediction"
              :loading="loadingPrediction"
            >
              <el-icon><RefreshRight /></el-icon>
              更新預測
            </el-button>
          </div>
        </div>
      </template>

      <!-- 預測內容 -->
      <div v-if="loadingPrediction" class="loading-container">
        <el-skeleton animated :rows="3" />
      </div>

      <div
        v-else-if="predictionData && predictionData.length > 0"
        class="prediction-content"
      >
        <div class="prediction-summary">
          <div class="summary-item">
            <span class="label">預測趨勢:</span>
            <span :class="['value', trendClass]">
              {{ trendText }}
              <el-icon v-if="overallTrend > 0"><CaretTop /></el-icon>
              <el-icon v-else-if="overallTrend < 0"><CaretBottom /></el-icon>
            </span>
          </div>
          <div class="summary-item">
            <span class="label">預期收益:</span>
            <span :class="['value', expectedReturnClass]">
              {{ expectedReturn >= 0 ? "+" : "" }}{{ expectedReturn }}%
            </span>
          </div>
        </div>

        <div class="prediction-chart-container">
          <!-- 使用 PredictionChart 組件 -->
          <PredictionChart
            :historicalData="filteredStockChart"
            :predictions="predictionData"
          />
        </div>

        <div class="prediction-disclaimer">
          <p>
            *
            此預測基於深度學習模型和統計分析，綜合評估歷史數據趨勢，僅供參考。投資有風險，決策需謹慎。
          </p>
        </div>
      </div>

      <div v-else class="empty-prediction">
        <el-empty description="暫無預測數據">
          <template #extra>
            <el-button type="primary" @click="loadPrediction"
              >生成預測</el-button
            >
          </template>
        </el-empty>
      </div>
    </el-card>

    <!-- 相關新聞區塊 -->
    <el-card class="news-card">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>相關新聞</span>
          <el-button size="small" @click="refreshNews">刷新</el-button>
        </div>
      </template>
      <!-- 新聞列表... -->
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useStockStore } from "@/stores/stockStore";
import { storeToRefs } from "pinia";
import KLineChart from "@/components/KLineChart.vue";
import PredictionChart from "@/components/PredictionChart.vue";
import { ElMessage } from "element-plus";
import axios from "axios";
import {
  ArrowLeft,
  TrendCharts,
  RefreshRight,
  CaretTop,
  CaretBottom,
  DataAnalysis,
} from "@element-plus/icons-vue";

export default {
  components: {
    KLineChart,
    PredictionChart,
  },
  props: {
    symbol: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const router = useRouter();
    const stockStore = useStockStore();
    const { currentStock, stockChart } = storeToRefs(stockStore);

    // 股價走勢時間範圍
    const timeRange = ref("3m");

    // 預測相關數據
    const predictionDays = ref(5);
    const predictionData = ref([]);
    const loadingPrediction = ref(false);

    // 計算篩選後的股價數據
    const filteredStockChart = computed(() => {
      if (!stockChart.value || stockChart.value.length === 0) return [];

      const now = new Date();
      let filterDate = new Date();

      switch (timeRange.value) {
        case "1w":
          filterDate.setDate(now.getDate() - 7);
          break;
        case "1m":
          filterDate.setMonth(now.getMonth() - 1);
          break;
        case "3m":
          filterDate.setMonth(now.getMonth() - 3);
          break;
        case "6m":
          filterDate.setMonth(now.getMonth() - 6);
          break;
        case "1y":
          filterDate.setFullYear(now.getFullYear() - 1);
          break;
        default:
          return stockChart.value;
      }

      return stockChart.value.filter((item) => {
        const itemDate = new Date(item.date);
        return itemDate >= filterDate;
      });
    });

    // 計算預測趨勢
    const overallTrend = computed(() => {
      if (!predictionData.value || predictionData.value.length < 2) return 0;

      const firstPrice = predictionData.value[0].price;
      const lastPrice =
        predictionData.value[predictionData.value.length - 1].price;

      if (lastPrice > firstPrice) return 1;
      if (lastPrice < firstPrice) return -1;
      return 0;
    });

    const trendText = computed(() => {
      if (overallTrend.value > 0) return "看漲";
      if (overallTrend.value < 0) return "看跌";
      return "持平";
    });

    const trendClass = computed(() => {
      if (overallTrend.value > 0) return "positive";
      if (overallTrend.value < 0) return "negative";
      return "neutral";
    });

    // 計算預期收益率
    const expectedReturn = computed(() => {
      if (!predictionData.value || predictionData.value.length === 0) return 0;

      const lastDay = predictionData.value[predictionData.value.length - 1];
      const firstDay = predictionData.value[0];

      const returnPercent = (lastDay.price / firstDay.price - 1) * 100;
      return returnPercent.toFixed(2);
    });

    const expectedReturnClass = computed(() => {
      if (parseFloat(expectedReturn.value) > 0) return "positive";
      if (parseFloat(expectedReturn.value) < 0) return "negative";
      return "neutral";
    });

    // 載入預測數據
    const loadPrediction = async () => {
      loadingPrediction.value = true;
      try {
        console.log('開始請求預測數據...');
        
        // 使用改進後的 API，包含歷史天數和預測天數參數
        const response = await axios.get(
          `http://localhost:5001/api/stocks/${props.symbol}/predict`,
          { 
            params: { 
              days: predictionDays.value,
              history_days: 90,  // 可以根據需要調整歷史數據天數
              use_ml: true
            },
            timeout: 15000  // 增加超時時間，因為模型預測可能需要更多時間
          }
        );
        
        console.log('預測 API 響應:', response.data);
        
        // 檢查預測數據有效性
        if (response.data && response.data.data && response.data.data.length > 0) {
          // 分離歷史數據和預測數據
          const historicalData = response.data.data.filter(item => !item.is_prediction);
          const predictedData = response.data.data.filter(item => item.is_prediction);
          
          // 設置預測數據
          predictionData.value = predictedData;
          
          // 也可以更新歷史數據 (如果需要)
          stockChart.value = historicalData;
          
          console.log('已設置預測數據:', predictionData.value.length);
          console.log('第一個預測數據:', predictionData.value[0]);
          
          ElMessage.success('預測數據已更新');
        } else {
          console.warn('預測 API 返回的數據格式不正確');
          ElMessage.warning('獲取預測數據失敗，使用模擬數據');
          useMockPredictionData(); // 使用模擬數據
        }
      } catch (error) {
        console.error('預測請求失敗:', error);
        ElMessage.error('無法獲取預測數據，使用模擬數據');
        useMockPredictionData(); // 使用模擬數據
      } finally {
        loadingPrediction.value = false;
      }
    };

    // 使用模擬數據的函數
    const useMockPredictionData = () => {
      const mockPredictions = [];
      const currentPrice = currentStock.value?.price || 500;
      let price = currentPrice;

      for (let i = 0; i < predictionDays.value; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i + 1);

        const changePercent = Math.random() * 4 - 2; // -2% 到 2% 的隨機變化
        price = price * (1 + changePercent / 100);

        mockPredictions.push({
          date: date.toISOString().split("T")[0],
          price: Math.round(price * 100) / 100,
          change: Math.round(changePercent * 100) / 100,
        });
      }

      predictionData.value = mockPredictions;
    };

    // 格式化日期
    const formatDate = (dateStr) => {
      const date = new Date(dateStr);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    };

    // 返回上一頁
    const goBack = () => {
      router.push("/dashboard");
    };

    onMounted(async () => {
      console.log("StockDetail 組件已掛載，股票代碼:", props.symbol);
      try {
        // 獲取股票詳情
        await stockStore.fetchStockDetail(props.symbol);
        console.log("股票詳情已獲取:", currentStock.value?.name);
        console.log("歷史數據長度:", stockChart.value?.length);

        // 故意延遲一下，確保股票數據已經加載完成
        await new Promise((resolve) => setTimeout(resolve, 300));

        // 加載預測數據
        console.log("開始獲取預測數據");
        await loadPrediction();
        console.log("預測數據已獲取:", predictionData.value?.length);
      } catch (err) {
        console.error("初始化資料出錯:", err);
      }
    });

    return {
      timeRange,
      currentStock,
      filteredStockChart,
      predictionDays,
      predictionData,
      loadingPrediction,
      overallTrend,
      trendText,
      trendClass,
      expectedReturn,
      expectedReturnClass,
      goBack,
      loadPrediction,
      formatDate,
    };
  },
};
</script>

<style scoped>
.stock-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.back-link {
  margin-bottom: 15px;
}

.stock-title {
  font-size: 24px;
  margin-bottom: 20px;
}

.chart-card,
.prediction-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-header .el-icon {
  margin-right: 8px;
}

.time-filter,
.prediction-actions {
  margin-left: auto;
}

.chart-container {
  height: 400px;
}

.prediction-card {
  margin-bottom: 20px;
}

.prediction-content {
  padding: 15px 0;
}

.prediction-summary {
  display: flex;
  gap: 30px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 15px;
}

.summary-item .label {
  font-weight: bold;
  margin-right: 10px;
}

.positive {
  color: #67c23a;
  font-weight: bold;
}

.negative {
  color: #f56c6c;
  font-weight: bold;
}

.neutral {
  color: #909399;
  font-weight: bold;
}

.prediction-chart-container {
  height: 400px; /* 增加高度 */
  min-height: 400px;
  width: 100%;
  border: 1px solid #ebeef5; /* 添加邊框便於查看 */
  margin: 20px 0;
}

.prediction-disclaimer {
  font-size: 12px;
  color: #909399;
  text-align: center;
  margin-top: 15px;
}

.loading-container,
.empty-prediction {
  padding: 30px 20px;
  text-align: center;
}
</style>
