<script setup lang="ts">
import { ref } from 'vue'
import { submitDeal } from '../api'
import type { DealCardData } from '../types'

const emit = defineEmits<{
  (e: 'submitted', card: DealCardData): void
}>()

const content = ref('')
const loading = ref(false)
const error = ref('')

const placeholder = `粘贴微信群消息，例如：
今晚8点，兰蔻小黑瓶精华50ml，先领200-30券，叠加跨店满300-50，到手价189元，6月20号截止`

async function handleSubmit() {
  if (!content.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    const res = await submitDeal(content.value, 'wechat_group', '微信攻略群')
    if (res.success && res.card) {
      emit('submitted', res.card)
      content.value = ''
    } else {
      error.value = res.error || '提取失败，请检查消息内容'
    }
  } catch (e: any) {
    error.value = e.message || '网络错误'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
    <h2 class="text-lg font-semibold text-gray-800 mb-4">📋 提交攻略消息</h2>
    <textarea
      v-model="content"
      :placeholder="placeholder"
      rows="4"
      class="w-full p-4 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent text-sm text-gray-700 placeholder-gray-400"
    />
    <div class="flex items-center justify-between mt-4">
      <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
      <span v-else class="text-xs text-gray-400">支持微信群、小红书等来源的优惠信息</span>
      <button
        @click="handleSubmit"
        :disabled="loading || !content.trim()"
        class="px-6 py-2.5 bg-indigo-500 text-white text-sm font-medium rounded-xl hover:bg-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
      >
        <span v-if="loading" class="inline-flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
          分析中...
        </span>
        <span v-else>提交分析</span>
      </button>
    </div>
  </div>
</template>
