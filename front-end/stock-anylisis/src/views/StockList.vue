<template>
  <div class="stock-list">
    <el-card class="header-card">
      <template #header>
        <div class="card-header">
          <span>股票列表</span>
          <el-button
              type="primary"
              @click="refreshStocks"
              :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table
          :data="stocks"
          v-loading="loading"
          class="stock-table"
          @row-click="handleRowClick"
      >
        <el-table-column prop="symbol" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="price" label="当前价格" width="120">
          <template #default="scope">
            <span class="price">{{ scope.row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="change" label="涨跌" width="100">
          <template #default="scope">
            <span :class="['change', scope.row.change >= 0 ? 'positive' : 'negative']">
              {{ scope.row.change >= 0 ? '+' : '' }}{{ scope.row.change }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="changePercent" label="涨跌幅" width="120">
          <template #default="scope">
            <el-tag
                :type="scope.row.change >= 0 ? 'success' : 'danger'"
                size="small"
            >
              {{ scope.row.change >= 0 ? '+' : '' }}{{ scope.row.changePercent }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button
                type="primary"
                size="small"
                @click.stop="viewDetail(scope.row.symbol)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-alert
        v-if="error"
        :title="error"
        type="error"
        class="error-alert"
        show-icon
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStockStore } from '@/stores/stockStore'
import { storeToRefs } from 'pinia'

const router = useRouter()
const stockStore = useStockStore()
const { stocks, loading, error } = storeToRefs(stockStore)

const refreshStocks = () => {
  stockStore.fetchStocks()
}

const handleRowClick = (row) => {
  viewDetail(row.symbol)
}

const viewDetail = (symbol) => {
  router.push(`/stocks/${symbol}`)
}

onMounted(() => {
  stockStore.fetchStocks()
})
</script>

<style scoped>
.stock-list {
  max-width: 1200px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-table {
  cursor: pointer;
}

.stock-table .el-table__row:hover {
  background-color: #f5f7fa;
}

.price {
  font-weight: 600;
  font-size: 16px;
}

.change.positive {
  color: #67c23a;
  font-weight: 600;
}

.change.negative {
  color: #f56c6c;
  font-weight: 600;
}

.error-alert {
  margin-top: 20px;
}
</style>
