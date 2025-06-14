<template>
  <div id="app">
    <el-container class="layout-container">
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="app-title">
            <el-icon><TrendCharts /></el-icon>
            股票分析系統
          </h1>
          <el-menu
            :default-active="activeIndex"
            class="header-menu"
            mode="horizontal"
            router
          >
            <el-menu-item index="/">公司列表</el-menu-item>
          </el-menu>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeIndex = computed(() => route.path)
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-menu {
  background: transparent;
  border: none;
}

.header-menu .el-menu-item {
  color: white;
  border-bottom: 2px solid transparent;
}

.header-menu .el-menu-item:hover,
.header-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.1);
  border-bottom-color: white;
  color: white;
}

.app-main {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>
