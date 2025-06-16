<template>
  <div class="simple-prediction-chart" ref="chartContainer"></div>
</template>

<script>
import { ref, onMounted, watch, onUnmounted } from 'vue';

export default {
  props: {
    predictions: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const chartContainer = ref(null);
    let chart = null;

    const createChart = () => {
      if (!chartContainer.value || !props.predictions || props.predictions.length === 0) {
        console.log('無法創建圖表 - 沒有容器或數據');
        return;
      }

      if (!window.echarts) {
        console.log('ECharts 未載入');
        return;
      }

      if (chart) {
        chart.dispose();
      }

      try {
        chart = window.echarts.init(chartContainer.value);
        
        const dates = props.predictions.map(item => item.date);
        const prices = props.predictions.map(item => item.price);
        
        const option = {
          title: { text: '股價預測' },
          xAxis: { type: 'category', data: dates },
          yAxis: { type: 'value' },
          series: [{
            data: prices,
            type: 'line',
            smooth: true
          }]
        };
        
        chart.setOption(option);
        console.log('簡化預測圖表已創建');
      } catch (e) {
        console.error('創建簡化預測圖表出錯:', e);
      }
    };
    
    watch(() => props.predictions, () => {
      console.log('預測數據變化，重繪圖表');
      createChart();
    }, { deep: true });
    
    onMounted(() => {
      console.log('SimplePredictionChart 已掛載');
      setTimeout(createChart, 100); // 延遲創建確保容器已經準備好
    });
    
    onUnmounted(() => {
      if (chart) {
        chart.dispose();
      }
    });
    
    return { chartContainer };
  }
};
</script>

<style scoped>
.simple-prediction-chart {
  width: 100%;
  height: 300px;
}
</style>

<!-- 在 StockDetail.vue 中將 PredictionChart 替換為 SimplePredictionChart 測試 -->
<SimplePredictionChart
  :predictions="predictionData"
/>

<script>
import SimplePredictionChart from '@/components/SimplePredictionChart.vue';

// 在 components 中添加
components: {
  KLineChart,
  PredictionChart,
  SimplePredictionChart // 添加簡化圖表
},
</script>