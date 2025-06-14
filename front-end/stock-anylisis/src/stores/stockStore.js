import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useStockStore = defineStore('stock', () => {
    // 状态
    const stocks = ref([])
    const currentStock = ref(null)
    const stockChart = ref(null)
    const predictionChart = ref(null)
    const loading = ref(false)
    const error = ref(null)

    // 模拟股票数据
    const mockStocks = [
        { symbol: '2317', name: '鴻海', price: 108.5, change: 2.5, changePercent: 2.36 },
        { symbol: '2330', name: '台積電', price: 890, change: -5, changePercent: -0.56 },
        { symbol: '2454', name: '聯發科', price: 1250, change: 15, changePercent: 1.22 },
        { symbol: '2412', name: '中華電', price: 125.5, change: 0.5, changePercent: 0.40 },
        { symbol: '2882', name: '國泰金', price: 65.8, change: -1.2, changePercent: -1.79 }
    ]

    // Getters
    const getStockBySymbol = computed(() => {
        return (symbol) => stocks.value.find(stock => stock.symbol === symbol)
    })

    // Actions
    const fetchStocks = async () => {
        loading.value = true
        error.value = null

        try {
            // 这里应该调用后端API
            // const response = await axios.get('/api/stocks')
            // stocks.value = response.data

            // 现在使用模拟数据
            await new Promise(resolve => setTimeout(resolve, 500)) // 模拟网络延迟
            stocks.value = mockStocks
        } catch (err) {
            error.value = '获取股票数据失败'
            console.error('Error fetching stocks:', err)
        } finally {
            loading.value = false
        }
    }

    const fetchStockDetail = async (symbol) => {
        loading.value = true
        error.value = null

        try {
            // 这里应该调用后端API获取详细信息
            // const response = await axios.get(`/api/stocks/${symbol}`)
            // currentStock.value = response.data

            // 模拟数据
            await new Promise(resolve => setTimeout(resolve, 500))
            const stock = mockStocks.find(s => s.symbol === symbol)
            if (stock) {
                currentStock.value = {
                    ...stock,
                    description: `${stock.name} (${stock.symbol}) 是台湾重要的上市公司`,
                    marketCap: '1.2兆',
                    pe: 15.6,
                    dividend: 5.2
                }

                // 生成模拟K线图数据
                stockChart.value = generateMockChartData()
                // 生成模拟预测图数据
                predictionChart.value = generateMockPredictionData()
            }
        } catch (err) {
            error.value = '获取股票详情失败'
            console.error('Error fetching stock detail:', err)
        } finally {
            loading.value = false
        }
    }

    // 生成模拟K线图数据
    const generateMockChartData = () => {
        const data = []
        let price = 100

        for (let i = 0; i < 30; i++) {
            const change = (Math.random() - 0.5) * 10
            price += change
            const open = price
            const close = price + (Math.random() - 0.5) * 5
            const high = Math.max(open, close) + Math.random() * 3
            const low = Math.min(open, close) - Math.random() * 3

            data.push({
                date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                open: open.toFixed(2),
                high: high.toFixed(2),
                low: low.toFixed(2),
                close: close.toFixed(2),
                volume: Math.floor(Math.random() * 1000000)
            })
        }

        return data
    }

    // 生成模拟预测数据
    const generateMockPredictionData = () => {
        const labels = []
        const actual = []
        const predicted = []

        let price = 100

        for (let i = 0; i < 20; i++) {
            labels.push(new Date(Date.now() + i * 24 * 60 * 60 * 1000).toLocaleDateString())

            if (i < 10) {
                // 历史数据
                actual.push(price)
                predicted.push(null)
            } else {
                // 预测数据
                actual.push(null)
                predicted.push(price)
            }

            price += (Math.random() - 0.5) * 5
        }

        return { labels, actual, predicted }
    }

    return {
        // State
        stocks,
        currentStock,
        stockChart,
        predictionChart,
        loading,
        error,

        // Getters
        getStockBySymbol,

        // Actions
        fetchStocks,
        fetchStockDetail
    }
})
