<template>
  <div class="chart-container">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { Chart } from 'chart.js/auto'
import 'chartjs-adapter-date-fns'

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  }
})

const chartRef = ref(null)
let chart = null

const createChart = () => {
  if (!chartRef.value || !props.data.length) return

  const ctx = chartRef.value.getContext('2d')

  // 銷毀現有圖表
  if (chart) {
    chart.destroy()
  }

  // 模擬 K 線圖數據
  const mockData = props.data.map((item, index) => ({
    x: new Date(new Date().setDate(new Date().getDate() - (props.data.length - index))),
    y: item.close || item.price || 0
  }))

  chart = new Chart(ctx, {
    type: 'line', // 使用基本線圖
    data: {
      datasets: [{
        label: '股價',
        data: mockData,
        borderColor: '#409EFF',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index'
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'day'
          }
        },
        y: {
          beginAtZero: false
        }
      }
    }
  })
}

watch(() => props.data, () => {
  createChart()
}, { deep: true })

onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chart) {
    chart.destroy()
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
}
</style>
