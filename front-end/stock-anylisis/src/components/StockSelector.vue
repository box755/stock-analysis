<template>
  <div class="stock-selector">
    <el-select
      v-model="selectedValue"
      filterable
      placeholder="選擇股票"
      @change="handleChange"
    >
      <el-option
        v-for="stock in stocks"
        :key="stock.symbol"
        :label="`${stock.name} (${stock.symbol})`"
        :value="stock.symbol"
      />
    </el-select>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: String
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedValue = ref(props.modelValue)
const stocks = ref([
  { symbol: '2330', name: '台積電' },
  { symbol: '2317', name: '鴻海' },
  // ... 其他股票
])

watch(() => props.modelValue, (newVal) => {
  selectedValue.value = newVal
})

const handleChange = (value) => {
  emit('update:modelValue', value)
  const selectedStock = stocks.value.find(s => s.symbol === value)
  emit('change', selectedStock)
}
</script>

<style scoped>
.stock-selector {
  margin-bottom: 20px;
}
</style>