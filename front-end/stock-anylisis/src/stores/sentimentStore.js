import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import dayjs from 'dayjs'

export const useSentimentStore = defineStore('sentiment', () => {
    // 状态
    const sentimentData = ref([])
    const loading = ref(false)
    const error = ref(null)
    const selectedCompany = ref('all')

    // 模拟情感分析数据
    const mockSentimentData = [
        {
            "company": "鴻海",
            "date": "2025年6月5日 下午2:05",
            "text": "鴻海 又 寫 最強 月 要 飛 了 分析 師 持平 看待 激勵 股價 機會 不大 奇摩 股市 鴻海 又 寫 最強 月 要 飛 了 分析 師 持平 看待 激勵 股價 機會 不大 閱讀 全文 許如 鎧 財經 特派 記者 更新 時間 年月日 下午 鴻海 今日 公布 最新 月 營收 為 億 元月 減年 增累 計前 月 營收 為 兆 元年 增雙創 同期 新高 運達 投顧 分析 師陳石輝 表示 本月 營收 算是 通關 以 持平 視之要 藉此 激勵 股價 恐怕 機會 不高 接下 來須 待 匯率 關稅 問題 有解 並待 季線 翻揚 才 有 大表現 機會",
            "time_iso": "2025-06-05T02:05",
            "impact_pct": 59.1
        },
        {
            "company": "鴻海",
            "date": "2025年6月5日 下午4:31",
            "text": "鴻海 月 營收 億元創 同期 高 第季 成長 關注 匯率 中央社 財經鴻海 月 營收 億元創 同期 高 第季 成長 關注 匯率 閱讀 全文 中央社 年月日 下午 中央社 記者 鍾 榮峰 台北 年月日 電鴻海 今天下午 公告 月 自結合 併 營收 新 台幣 億 元月 減較 年 同期 成長 創歷 年 同期 新高 主要 受惠 消費 智能 產品 拉 貨動能 強勁 預估 第季 營運顯 著季 增和年 增持續 關注 政經 局勢 及 匯率 變化",
            "time_iso": "2025-06-05T04:31",
            "impact_pct": 54.41
        },
        {
            "company": "聯發科",
            "date": "2025年6月5日 上午11:25",
            "text": "台股 聯發科 遭 剔除 跌 逾 網喊 這樣 殺 要 破底 了 吧 專家 下周 有望 回穩 奇摩 股市 台股 聯發科 遭 剔除 跌 逾 網喊 這樣 殺 要 破底 了 吧 專家 下周 有望 回穩",
            "time_iso": "2025-06-05T11:25",
            "impact_pct": 57.61
        },
        {
            "company": "聯發科",
            "date": "2025年6月4日 下午12:30",
            "text": "台北 股市 後 市 觀點 好 轉美系 外資 看 讚 雄 時 報 資 訊 台北 股市 後 市 觀點 好 轉美系 外資 看 讚 雄",
            "time_iso": "2025-06-04T12:30",
            "impact_pct": 58.82
        }
    ]

    // Getters
    const companies = computed(() => {
        const companySet = new Set(sentimentData.value.map(item => item.company))
        return ['all', ...Array.from(companySet)]
    })

    const filteredSentimentData = computed(() => {
        if (selectedCompany.value === 'all') {
            return sentimentData.value
        }
        return sentimentData.value.filter(item => item.company === selectedCompany.value)
    })

    const sentimentSummary = computed(() => {
        const data = filteredSentimentData.value
        if (data.length === 0) return null

        const avgImpact = data.reduce((sum, item) => sum + item.impact_pct, 0) / data.length
        const positive = data.filter(item => item.impact_pct > 60).length
        const neutral = data.filter(item => item.impact_pct >= 40 && item.impact_pct <= 60).length
        const negative = data.filter(item => item.impact_pct < 40).length

        return {
            total: data.length,
            avgImpact: avgImpact.toFixed(2),
            positive,
            neutral,
            negative
        }
    })

    // Actions
    const fetchSentimentData = async () => {
        loading.value = true
        error.value = null

        try {
            // 这里应该调用后端API
            // const response = await axios.get('/api/sentiment')
            // sentimentData.value = response.data

            // 现在使用模拟数据
            await new Promise(resolve => setTimeout(resolve, 500))
            sentimentData.value = mockSentimentData.sort((a, b) =>
                new Date(b.time_iso) - new Date(a.time_iso)
            )
        } catch (err) {
            error.value = '获取情感分析数据失败'
            console.error('Error fetching sentiment data:', err)
        } finally {
            loading.value = false
        }
    }

    const setSelectedCompany = (company) => {
        selectedCompany.value = company
    }

    return {
        // State
        sentimentData,
        loading,
        error,
        selectedCompany,

        // Getters
        companies,
        filteredSentimentData,
        sentimentSummary,

        // Actions
        fetchSentimentData,
        setSelectedCompany
    }
})
