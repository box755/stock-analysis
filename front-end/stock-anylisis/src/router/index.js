import { createRouter, createWebHistory } from 'vue-router'
import StockList from '@/views/StockList.vue'
import StockDetail from '@/views/StockDetail.vue'
import SentimentAnalysis from '@/views/SentimentAnalysis.vue'

const routes = [
    {
        path: '/',
        redirect: '/stocks'
    },
    {
        path: '/stocks',
        name: 'StockList',
        component: StockList
    },
    {
        path: '/stocks/:symbol',
        name: 'StockDetail',
        component: StockDetail,
        props: true
    },
    {
        path: '/sentiment',
        name: 'SentimentAnalysis',
        component: SentimentAnalysis
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
