<script setup lang="ts">
import type { RoomRuleData } from '@/share/api/types'
import { CheckCircle, Circle } from 'lucide-vue-next'

const { rule } = defineProps<{ rule: RoomRuleData }>()
const emit = defineEmits<{ update: [string] }>()
</script>

<template>
  <div class="flex gap-2 mb-2">
    <button @click="emit('update', rule.key)">
      <CheckCircle v-if="rule.status" class="text-teal-200" />
      <Circle v-else />
    </button>
    <div>{{ rule.name }}</div>
  </div>
</template>
