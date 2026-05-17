<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listDeals } from '../api'
import type { DealCardData } from '../types'
import DealCard from './DealCard.vue'

const props = defineProps<{ refreshKey: number }>()
const deals = ref<DealCardData[]>([])
const loading = ref(false)

async function fetchDeals() {
  loading.value = true
  try {
    const res = await listDeals()
    deals.value = res.deals
  } catch (e) {
    console.error('Failed to fetch deals:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchDeals)

defineExpose({ refresh: fetchDeals })
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-800">🔥 攻略列表</h2>
      <button
        @click="fetchDeals"
        :disabled="loading"
        class="text-sm text-indigo-500 hover:text-indigo-600 disabled:opacity-50"
      >
        {{ loading ? '刷新中...' : '刷新' }}
      </button>
    </div>

    <div v-if="loading && !deals.length" class="text-center py-12 text-gray-400">
      加载中...
    </div>

    <div v-else-if="!deals.length" class="text-center py-12 text-gray-400">
      <p class="text-4xl mb-3">📭</p>
      <p>暂无攻略，提交一条试试</p>
    </div>

    <div v-else class="grid gap-4">
      <DealCard v-for="deal in deals" :key="deal.id ?? deal.created_at" :deal="deal" />
    </div>
  </div>
</template>
