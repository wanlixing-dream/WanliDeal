<script setup lang="ts">
import { ref } from 'vue'
import SubmitForm from './components/SubmitForm.vue'
import DealList from './components/DealList.vue'
import type { DealCardData } from './types'

const refreshKey = ref(0)
const dealListRef = ref<InstanceType<typeof DealList> | null>(null)

function onSubmitted(_card: DealCardData) {
  dealListRef.value?.refresh()
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b border-gray-100 sticky top-0 z-10">
      <div class="max-w-2xl mx-auto px-4 py-4 flex items-center gap-3">
        <span class="text-2xl">💰</span>
        <div>
          <h1 class="text-lg font-bold text-gray-800">WanliDeal</h1>
          <p class="text-xs text-gray-400">618攻略验证助手</p>
        </div>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-2xl mx-auto px-4 py-6 space-y-6">
      <SubmitForm @submitted="onSubmitted" />
      <DealList ref="dealListRef" :refresh-key="refreshKey" />
    </main>
  </div>
</template>
