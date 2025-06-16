import { defineStore } from "pinia";
import { ref, computed } from "vue";
import dayjs from "dayjs";
import axios from "axios";

export const useSentimentStore = defineStore("sentiment", () => {
  // 状态
  const sentimentData = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const selectedCompany = ref("all");
  const currentMarket = ref("TW"); // 新增市場狀態

  // Getters
  const companies = computed(() => {
    const companySet = new Set(sentimentData.value.map((item) => item.company));
    return ["all", ...Array.from(companySet)];
  });

  const filteredSentimentData = computed(() => {
    if (selectedCompany.value === "all") {
      return sentimentData.value;
    }
    return sentimentData.value.filter(
      (item) => item.company === selectedCompany.value
    );
  });

  const sentimentSummary = computed(() => {
    const data = filteredSentimentData.value;
    if (data.length === 0) return null;

    const avgImpact =
      data.reduce((sum, item) => sum + item.impact_pct, 0) / data.length;
    const positive = data.filter((item) => item.impact_pct > 60).length;
    const neutral = data.filter(
      (item) => item.impact_pct >= 40 && item.impact_pct <= 60
    ).length;
    const negative = data.filter((item) => item.impact_pct < 40).length;

    return {
      total: data.length,
      avgImpact: avgImpact.toFixed(2),
      positive,
      neutral,
      negative,
    };
  });

  // Actions
  const fetchSentimentData = async (market = currentMarket.value) => {
    loading.value = true;
    error.value = null;
    currentMarket.value = market;

    try {
      // 從後端 API 獲取數據
      const response = await axios.get(
        `http://localhost:5001/api/sentiment-analysis/${market}`
      );

      if (response.data && Array.isArray(response.data)) {
        // 將 API 回傳的數據進行排序與處理
        sentimentData.value = response.data.sort(
          (a, b) =>
            new Date(b.time_iso || b.date) - new Date(a.time_iso || a.date)
        );
        console.log(`成功載入 ${sentimentData.value.length} 筆情緒分析數據`);
      } else {
        throw new Error("API 回傳格式錯誤");
      }
    } catch (err) {
      console.error("獲取情緒分析數據失敗:", err);
      error.value = "獲取情緒分析數據失敗";

      // 如果 API 失敗，使用備用模擬數據
      sentimentData.value = generateMockSentimentData(market);
    } finally {
      loading.value = false;
    }
  };

  // 新增更新情緒數據的方法
  const updateSentimentData = (data) => {
    // 檢查數據格式
    if (data && typeof data === "object") {
      // 如果是對象形式 {positive, neutral, negative, total}
      if ("positive" in data && "neutral" in data && "negative" in data) {
        // 直接更新摘要數據
        const summaryData = {
          positive: data.positive || 0,
          neutral: data.neutral || 0,
          negative: data.negative || 0,
          total: data.total || data.positive + data.neutral + data.negative,
        };

        // 更新計算屬性的基礎數據
        const mockNewsData = [];

        // 生成符合 positive 數量的積極新聞
        for (let i = 0; i < data.positive; i++) {
          mockNewsData.push({
            impact_pct: Math.floor(Math.random() * 20) + 70, // 70-90 之間
          });
        }

        // 生成符合 neutral 數量的中性新聞
        for (let i = 0; i < data.neutral; i++) {
          mockNewsData.push({
            impact_pct: Math.floor(Math.random() * 20) + 40, // 40-60 之間
          });
        }

        // 生成符合 negative 數量的消極新聞
        for (let i = 0; i < data.negative; i++) {
          mockNewsData.push({
            impact_pct: Math.floor(Math.random() * 40), // 0-40 之間
          });
        }

        // 更新新聞數據
        sentimentData.value = mockNewsData;
        console.log("成功更新情緒數據:", {
          summaryCount: summaryData,
          newsCount: mockNewsData.length,
        });
      } else if (Array.isArray(data)) {
        // 如果是數組，直接設置
        sentimentData.value = data;
        console.log("成功更新情緒數據數組:", data.length);
      } else {
        console.error("更新情緒數據失敗: 不支持的數據格式", data);
      }
    } else {
      console.error("更新情緒數據失敗: 無效數據", data);
    }
  };

  const setSelectedCompany = (company) => {
    selectedCompany.value = company;
  };

  // 切換市場
  const switchMarket = (market) => {
    if (market !== currentMarket.value) {
      currentMarket.value = market;
      fetchSentimentData(market);
    }
  };

  // 產生備用模擬數據的函數
  const generateMockSentimentData = (market) => {
    const companies =
      market === "TW"
        ? ["台積電", "鴻海", "聯發科", "台達電", "聯電"]
        : ["Apple", "Microsoft", "Google", "Amazon", "Meta"];

    const mockData = [];
    const now = new Date();

    // 為每家公司生成 3 筆新聞
    companies.forEach((company) => {
      for (let i = 0; i < 3; i++) {
        const date = new Date(now);
        date.setHours(date.getHours() - i * 5);

        mockData.push({
          company,
          date: dayjs(date).format("YYYY年MM月DD日 HH:mm"),
          time_iso: dayjs(date).format("YYYY-MM-DDTHH:mm"),
          text: `這是關於 ${company} 的模擬新聞 #${
            i + 1
          }。市場波動劇烈，投資人保持觀望態度。`,
          impact_pct: Math.floor(Math.random() * 40) + 30, // 30-70 之間的隨機數
        });
      }
    });

    return mockData.sort((a, b) => new Date(b.time_iso) - new Date(a.time_iso));
  };

  return {
    // State
    sentimentData,
    loading,
    error,
    selectedCompany,
    currentMarket,

    // Getters
    companies,
    filteredSentimentData,
    sentimentSummary,

    // Actions
    fetchSentimentData,
    setSelectedCompany,
    updateSentimentData,
    switchMarket,
  };
});
