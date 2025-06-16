import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import axios from 'axios'
import zhTw from 'element-plus/dist/locale/zh-tw.mjs'

// 設定 axios 預設值
axios.defaults.baseURL = 'http://localhost:5001'

// 加載 echarts
const loadEcharts = () => {
  return new Promise((resolve) => {
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js'
    script.async = true
    script.onload = () => {
      console.log('echarts 已全局加載')
      resolve(true)
    }
    script.onerror = () => {
      console.error('無法加載 echarts')
      resolve(false)
    }
    document.head.appendChild(script)
  })
}

// 啟動應用前加載 echarts
loadEcharts().then(() => {
  // 創建 Vue 應用
  const app = createApp(App)

  // 註冊 Element Plus 圖標
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.use(router)
  app.use(ElementPlus, { locale: zhTw })
  app.use(createPinia())

  app.mount('#app')
})
