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
    const symbolToNameMap = ref({}) // 股票代码到名称的映射
    const currentMarket = ref('TW') // 固定為台灣市場
    const pagination = ref(null) // 分页信息

    // Computed
    const filteredStocks = computed(() => {
        return stocks.value
    })

    // 获取股票代码到名称的映射
    const fetchSymbolToNameMap = async () => {
        try {
            const response = await axios.get('http://localhost:5001/api/company-mappings')
            symbolToNameMap.value = response.data
            console.log('已载入股票代码映射', Object.keys(symbolToNameMap.value).length)
        } catch (err) {
            console.error('获取股票代码映射失败:', err)
        }
    }

    // Getters
    const getStockBySymbol = computed(() => {
        return (symbol) => stocks.value.find(stock => stock.symbol === symbol)
    })

    // Actions
    const fetchStocks = async (page = 1, pageSize = 10) => {
        loading.value = true
        error.value = null

        try {
            const response = await axios.get(
                `http://localhost:5001/api/companies?market=TW&page=${page}&page_size=${pageSize}`
            )

            if (response.data && response.data.data) {
                // 更新股票列表
                stocks.value = response.data.data.map((stock) => ({
                    ...stock,
                    market: 'TW',
                    price: Number(stock.price) || 0,
                    change: Number(stock.change) || 0,
                    changePercent: stock.changePercent !== undefined ?
                        Number(stock.changePercent) :
                        (stock.price ? (stock.change / stock.price * 100) : 0)
                }))

                // 更新分页信息
                pagination.value = response.data.pagination
            }
        } catch (err) {
            console.error('获取股票数据失败:', err)
            error.value = '获取股票数据失败'
        } finally {
            loading.value = false
        }
    }

    // 搜索股票
    const searchStocks = async (query) => {
        if (!query) return []

        try {
            const response = await axios.get(`http://localhost:5001/api/search-stocks?q=${encodeURIComponent(query)}`)
            return response.data
        } catch (err) {
            console.error('搜索股票失败:', err)
            return []
        }
    }

    const fetchStockDetail = async (symbol) => {
        loading.value = true
        error.value = null

        try {
            // 尝试从API获取股票详情
            const response = await axios.get(`http://localhost:5001/api/stocks/${encodeURIComponent(symbol)}`)

            // 找到基本信息
            const stock = stocks.value.find(s => s.symbol === symbol) ||
                { symbol, name: symbolToNameMap.value[symbol] || symbol, price: 0, change: 0, changePercent: 0, market: 'TW' }

            if (response.data) {
                // 使用API的数据生成K线图数据
                stockChart.value = response.data

                // 更新当前股票详情
                currentStock.value = {
                    ...stock,
                    description: `${stock.name} (${stock.symbol}) 是一家重要的上市公司`,
                    marketCap: '1.2兆',
                    pe: 15.6,
                    dividend: 5.2
                }

                // 生成预测数据
                predictionChart.value = generateMockPredictionData()
            } else {
                throw new Error('返回数据格式不正确')
            }
        } catch (err) {
            console.error('获取股票详情失败:', err)
            error.value = '获取股票详情失败'

            // 使用模拟数据
            const stock = stocks.value.find(s => s.symbol === symbol) ||
                { symbol, name: symbolToNameMap.value[symbol] || symbol, price: 0, change: 0, market: 'TW' }

            currentStock.value = {
                ...stock,
                description: `${stock.name} (${stock.symbol}) 是一家重要的上市公司`,
                marketCap: '1.2兆',
                pe: 15.6,
                dividend: 5.2
            }

            // 生成模拟K线图数据
            stockChart.value = generateMockChartData()
            // 生成模拟预测图数据
            predictionChart.value = generateMockPredictionData()
        } finally {
            loading.value = false
        }
    }

    // 生成模拟K线图数据 - 提供给外部使用
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
                open: parseFloat(open.toFixed(2)),
                high: parseFloat(high.toFixed(2)),
                low: parseFloat(low.toFixed(2)),
                close: parseFloat(close.toFixed(2)),
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

    // 初始化数据
    const initializeData = async (pageSize = 10) => {
        await fetchSymbolToNameMap()
        await fetchStocks(1, pageSize)
    }

    const fetchStockPrediction = async (symbol) => {
        loading.value = true
        error.value = null

        try {
            const response = await axios.get(`/api/stocks/${symbol}/predict?days=7&use_ml=true`)
            const predictionData = response.data
            
            // 將後端數據轉換為圖表所需格式
            const labels = predictionData.predictions.map(p => p.date)
            const actual = Array(labels.length).fill(null)
            const predicted = predictionData.predictions.map(p => p.price)
            
            // 第一個點是當前價格，設為歷史數據的最後一點
            actual[0] = predictionData.current_price
            
            predictionChart.value = { labels, actual, predicted }
        } catch (err) {
            error.value = '獲取預測數據失敗'
            console.error('Error fetching stock prediction:', err)
        } finally {
            loading.value = false
        }
    }

    return {
        // State
        stocks,
        currentStock,
        stockChart,
        predictionChart,
        loading,
        error,
        symbolToNameMap,
        currentMarket,
        filteredStocks,
        pagination, // 导出分页信息

        // Getters
        getStockBySymbol,

        // Actions
        fetchStocks,
        fetchStockDetail,
        searchStocks,
        generateMockChartData,
        generateMockPredictionData,
        initializeData,
        fetchStockPrediction
    }
})
