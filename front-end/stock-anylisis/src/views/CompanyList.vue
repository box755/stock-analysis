<template>
  <div class="company-list">
    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <h2>股票列表</h2>
          <el-button type="primary" @click="refreshList">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="companies"
        style="width: 100%"
        :row-class-name="tableRowClassName"
        @row-click="handleCompanyClick"
      >
        <el-table-column prop="symbol" label="代碼" width="100" />
        <el-table-column prop="name" label="公司名稱" width="200" />
        <el-table-column label="現價" width="100">
          <template #default="{ row }">
            {{ formatNumber(row.price) }}
          </template>
        </el-table-column>
        <el-table-column label="漲跌" width="100">
          <template #default="{ row }">
            <span :class="{ up: row.change > 0, down: row.change < 0 }">
              {{ row.change >= 0 ? "+" : "" }}{{ formatNumber(row.change) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="漲跌幅" width="100">
          <template #default="{ row }">
            <span :class="{ up: row.change > 0, down: row.change < 0 }">
              {{ row.change >= 0 ? "+" : ""
              }}{{ formatNumber(getChangePercent(row)) }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { ElMessage } from "element-plus";
import { Refresh } from "@element-plus/icons-vue";

const router = useRouter();
const companies = ref([]);
const loading = ref(false);

// 格式化數字
const formatNumber = (num) => {
  if (typeof num !== "number") return "0.00";
  return num.toFixed(2);
};

// 計算漲跌幅
const getChangePercent = (row) => {
  if (!row.price || !row.change) return 0;
  return ((row.change / row.price) * 100).toFixed(2);
};

const tableRowClassName = ({ row }) => {
  if (row.change > 0) return "up-row";
  if (row.change < 0) return "down-row";
  return "";
};

const handleCompanyClick = (row) => {
  const encodedSymbol = encodeURIComponent(row.symbol)
  router.push({
    name: 'CompanyAnalysis',
    params: { symbol: encodedSymbol }
  })
}

const loadCompanies = async () => {
  loading.value = true;
  try {
    const response = await axios.get("http://localhost:5001/api/companies");
    if (response.data && Array.isArray(response.data)) {
      companies.value = response.data.map((company) => ({
        ...company,
        price: Number(company.price) || 0,
        change: Number(company.change) || 0,
      }));
    }
  } catch (error) {
    console.error("載入公司列表失敗:", error);
    ElMessage.error("無法載入公司列表");
  } finally {
    loading.value = false;
  }
};

const refreshList = () => {
  loadCompanies();
};

onMounted(() => {
  loadCompanies();
});
</script>

<style scoped>
.company-list {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.up {
  color: #f56c6c;
}

.down {
  color: #67c23a;
}

:deep(.up-row) {
  background-color: #fef0f0;
}

:deep(.down-row) {
  background-color: #f0f9eb;
}

:deep(.el-table tbody tr:hover) {
  cursor: pointer;
}
</style>
