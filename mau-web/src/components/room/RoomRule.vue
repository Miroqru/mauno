<script setup lang="ts">
import { CheckCircle, Circle } from 'lucide-vue-next';

  const props = defineProps<{
    name: string
    status: boolean
  }>()

</script>

<template>
  <div class="flex gap-2 mb-2">
    <button>
        <CheckCircle v-if="props.status" class="text-teal-200" />
        <Circle v-else />
    </button>
    <div>{{ props.name }}</div>
  </div>
</template>
