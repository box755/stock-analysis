<template>
  <el-card class="news-list">
    <template #header>
      <div class="card-header">
        <h3>相關新聞</h3>
      </div>
    </template>

    <el-timeline>
      <el-timeline-item
        v-for="news in newsList"
        :key="news.id"
        :timestamp="news.date"
        :type="getSentimentType(news.sentiment_score)"
      >
        <el-card class="news-card" @click="showNewsDetail(news)">
          <div class="news-header">
            <h4>{{ news.title }}</h4>
            <el-tag :type="getSentimentType(news.sentiment_score)">
              情感分數: {{ news.sentiment_score }}
            </el-tag>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>

    <!-- 新聞詳情對話框 -->
    <el-dialog
      v-model="showDetail"
      :title="selectedNews?.title"
      width="60%"
    >
      <div class="news-content">
        <p>{{ selectedNews?.content }}</p>
        <div class="sentiment-analysis" v-if="selectedNews?.analysis">
          <h4>AI 分析</h4>
          <p>{{ selectedNews.analysis }}</p>
        </div>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  newsList: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['analyze'])

const showDetail = ref(false)
const selectedNews = ref(null)

const getSentimentType = (score) => {
  if (score >= 0.6) return 'success'
  if (score <= 0.4) return 'danger'
  return 'warning'
}

const showNewsDetail = (news) => {
  selectedNews.value = news
  showDetail.value = true
  if (!news.analysis) {
    emit('analyze', news)
  }
}
</script>