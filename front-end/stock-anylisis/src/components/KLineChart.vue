<template>
  <div class="k-line-chart">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend
)

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const chartRef = ref(null)
let chartInstance = null

const createChart = () => {
  if (!chartRef.value || !props.data) return

  const ctx = chartRef.value.getContext('2d')

  // 销毁现有图表
  if (chartInstance) {
    chartInstance.destroy()
  }

  const labels = props.data.map(item => item.date)
  const prices = props.data.map(item => parseFloat(item.close))
  const volumes = props.data.map(item => item.volume)

  chartInstance = new ChartJS(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: '收盘价',
          data: prices,
          borderColor: '#409eff',
          backgroundColor: 'rgba(64, 158, 255, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: '股价走势图'
        },
        legend: {
          display: true,
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: '价格 (元)'
          }
        },
        x: {
          title: {
            display: true,
            text: '日期'
          }
        }
      },
      interaction: {
        intersect: false,
        mode: 'index'
      }
    }
  })
}

watch(() => props.data, createChart, { deep: true })

onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<style scoped>
.k-line-chart {
  width: 100%;
  height: 100%;
  position: relative;
}

canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>
