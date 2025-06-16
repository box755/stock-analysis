<template>
  <div class="prediction-chart-container" ref="chartContainer">
    <div v-if="!chartInitialized" class="chart-loading">
      <p>圖表載入中...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, onUnmounted, nextTick } from "vue";

export default {
  props: {
    historicalData: {
      type: Array,
      default: () => [],
    },
    predictions: {
      type: Array,
      default: () => [],
    },
  },
  setup(props) {
    const chartContainer = ref(null);
    const chartInitialized = ref(false);
    let chart = null;

    // 準備圖表數據
    const prepareChartData = () => {
      console.log("準備圖表數據 - 歷史數據長度:", props.historicalData.length);
      console.log("準備圖表數據 - 預測數據長度:", props.predictions.length);

      // 如果沒有歷史數據或預測數據，直接返回空數據
      if (!props.historicalData || props.historicalData.length === 0 || 
          !props.predictions || props.predictions.length === 0) {
        return {
          dates: [],
          prices: [],
          predictionDates: [],
          predictionPrices: [],
        };
      }

      // 取最近 30 天的歷史數據
      const historyLimit = Math.min(30, props.historicalData.length);
      const recentHistory = props.historicalData.slice(-historyLimit);

      // 處理歷史數據 - 使用 close 欄位作為價格
      const dates = recentHistory.map((item) => item.date || "");
      const prices = recentHistory.map((item) => {
        // 首先檢查 close 欄位，然後檢查 Close 欄位（大寫）
        return item.close || item.Close || 0;
      });

      // 處理預測數據 - 使用 close 或 price 欄位
      const predictionDates = props.predictions.map((item) => item.date || "");
      const predictionPrices = props.predictions.map((item) => {
        return item.close || item.price || 0;
      });

      return {
        dates,
        prices, 
        predictionDates,
        predictionPrices
      };
    };

    // 更新圖表
    const updateChart = () => {
      console.log("執行 updateChart");

      if (!chart || !window.echarts) {
        console.warn("圖表或 echarts 尚未初始化");
        return;
      }

      const { dates, prices, predictionDates, predictionPrices } =
        prepareChartData();

      // 如果沒有數據，則不更新圖表
      if (dates.length === 0 && predictionDates.length === 0) {
        console.warn("沒有足夠的數據更新圖表");
        return;
      }

      console.log(`更新圖表: ${dates.length} 條歷史數據, ${predictionDates.length} 條預測數據`);

      const option = {
        title: {
          text: "股價預測分析",
          left: "center",
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross",
          },
        },
        legend: {
          data: ["歷史價格", "預測價格"],
          bottom: 10,
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "15%",
          top: "15%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: [...dates, ...predictionDates],
          axisLabel: {
            formatter: (value) => {
              if (!value) return "";
              // 如果是完整的日期格式 (YYYY-MM-DD)，只顯示月/日
              if (value.length >= 10) {
                return value.substring(5).replace("-", "/");
              }
              return value;
            },
            rotate: 30,
          },
        },
        yAxis: {
          type: "value",
          scale: true,
          name: "價格",
          axisLabel: {
            formatter: "{value} 元",
          },
        },
        series: [
          {
            name: "歷史價格",
            type: "line",
            data: [...prices, ...Array(predictionDates.length).fill(null)],
            smooth: true,
            symbol: "circle",
            symbolSize: 5,
            // 避免預測區域顯示歷史數據的連線
            connectNulls: false,
          },
          {
            name: "預測價格",
            type: "line",
            data: [...Array(dates.length).fill(null), ...predictionPrices],
            smooth: true,
            symbol: "circle",
            symbolSize: 5,
            lineStyle: {
              type: "dashed",
            },
            itemStyle: {
              color: "#ff9f7f",
            },
            // 避免歷史區域顯示預測數據的連線
            connectNulls: false,
          },
        ],
      };

      chart.setOption(option);
      console.log("圖表已更新");
    };

    // 初始化圖表
    const initChart = async () => {
      if (!chartContainer.value) {
        console.error("圖表容器元素未找到");
        return;
      }
      
      try {
        console.log('容器尺寸:', chartContainer.value.offsetWidth, chartContainer.value.offsetHeight);
        
        // 確保容器有大小
        if (chartContainer.value.offsetHeight < 50) {
          console.warn('容器高度不足，強制設置為 300px');
          chartContainer.value.style.height = '300px';
        }
        
        // 確保 echarts 已載入
        if (!window.echarts) {
          console.error("echarts 未載入，嘗試載入 echarts...");
          await loadECharts();
        }
        
        if (!window.echarts) {
          console.error("無法載入 echarts");
          return;
        }
        
        console.log("初始化圖表...");
        chart = window.echarts.init(chartContainer.value);
        chartInitialized.value = true;
        console.log("圖表已初始化");
        
        // 明確強制更新圖表
        await nextTick();
        updateChart();
        
        // 為了確保渲染，再次更新一次
        setTimeout(() => {
          if (chart) {
            chart.resize();
            updateChart();
          }
        }, 100);
      } catch (err) {
        console.error("初始化圖表失敗:", err);
      }
    };

    // 加載 ECharts 庫
    const loadECharts = () => {
      return new Promise((resolve) => {
        if (window.echarts) {
          console.log("echarts 已存在");
          resolve(true);
          return;
        }

        console.log("加載 echarts...");
        const script = document.createElement("script");
        script.src =
          "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js";
        script.async = true;

        script.onload = () => {
          console.log("echarts 加載成功");
          resolve(true);
        };

        script.onerror = () => {
          console.error("echarts 加載失敗");
          resolve(false);
        };

        document.head.appendChild(script);
      });
    };

    // 監聽數據變化
    watch(
      () => props.historicalData,
      () => {
        console.log("歷史數據變化，更新圖表");
        if (chartInitialized.value) {
          updateChart();
        }
      },
      { deep: true }
    );

    watch(
      () => props.predictions,
      (newData) => {
        console.log("預測數據變化，新數據長度:", newData?.length);
        console.log("圖表是否已初始化:", chartInitialized.value);
        if (chartInitialized.value) {
          updateChart();
        } else {
          console.warn("圖表尚未初始化，無法更新");
          // 嘗試重新初始化
          initChart();
        }
      },
      { deep: true }
    );

    // 處理視窗大小變化
    const handleResize = () => {
      if (chart) {
        chart.resize();
      }
    };

    onMounted(async () => {
      console.log("PredictionChart 組件已掛載");
      await initChart();
      window.addEventListener("resize", handleResize);
    });

    onUnmounted(() => {
      if (chart) {
        chart.dispose();
      }
      window.removeEventListener("resize", handleResize);
      console.log("PredictionChart 組件已卸載");
    });

    return {
      chartContainer,
      chartInitialized,
    };
  },
};
</script>

<style scoped>
.prediction-chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.chart-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 300px;
  color: #909399;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
