<script setup lang="ts">
import type { DealCardData } from '../types'

defineProps<{ deal: DealCardData }>()

function formatTime(iso: string | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  expiring_soon: 'bg-amber-100 text-amber-700',
  expired: 'bg-red-100 text-red-600',
  unverified: 'bg-gray-100 text-gray-600',
}
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
    <!-- Header -->
    <div class="flex items-start justify-between mb-3">
      <h3 class="text-base font-semibold text-gray-800 leading-snug flex-1 mr-3">
        {{ deal.product_name }}
      </h3>
      <span :class="[statusColors[deal.status] || statusColors.unverified, 'text-xs font-medium px-2.5 py-1 rounded-full whitespace-nowrap']">
        {{ deal.status_icon }} {{ deal.status_label }}
      </span>
    </div>

    <!-- Price -->
    <div class="flex items-baseline gap-3 mb-4">
      <span v-if="deal.claimed_price" class="text-2xl font-bold text-indigo-600">
        ¥{{ deal.claimed_price }}
      </span>
      <span v-if="deal.original_price" class="text-sm text-gray-400 line-through">
        ¥{{ deal.original_price }}
      </span>
      <span v-if="deal.original_price && deal.claimed_price" class="text-xs bg-red-50 text-red-500 px-2 py-0.5 rounded-full font-medium">
        省{{ Math.round((1 - deal.claimed_price / deal.original_price) * 100) }}%
      </span>
    </div>

    <!-- Claims -->
    <div v-if="deal.claims.length" class="flex flex-wrap gap-2 mb-4">
      <span
        v-for="(claim, i) in deal.claims"
        :key="i"
        class="text-xs bg-indigo-50 text-indigo-600 px-2.5 py-1 rounded-lg"
      >
        {{ claim.type_label }}：{{ claim.description }}
      </span>
    </div>

    <!-- Steps -->
    <div v-if="deal.steps.length" class="mb-4">
      <p class="text-xs text-gray-500 mb-2 font-medium">操作步骤</p>
      <ol class="text-sm text-gray-600 space-y-1">
        <li v-for="(step, i) in deal.steps" :key="i" class="flex items-start gap-2">
          <span class="text-xs bg-gray-100 text-gray-500 w-5 h-5 flex items-center justify-center rounded-full shrink-0 mt-0.5">{{ i + 1 }}</span>
          <span>{{ step }}</span>
        </li>
      </ol>
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between text-xs text-gray-400 pt-3 border-t border-gray-50">
      <span>{{ deal.source_name || deal.source }}</span>
      <span v-if="deal.valid_until">截止 {{ formatTime(deal.valid_until) }}</span>
    </div>
  </div>
</template>
