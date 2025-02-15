<script setup lang="ts">
import type { Notify } from '@/share/stores/notify'
import { CheckCircle, CircleAlert, CircleX, Info, XIcon } from 'lucide-vue-next'

const { notify } = defineProps<{ notify: Notify }>()
const emit = defineEmits<{
  close: [string]
}>()
</script>

<template>
  <div
    class="bg-stone-800 transition inline-flex gap-2 rounded-xl border-2 p-2"
    :class="{
      'border-teal-300': notify.type === 'success',
      'border-pink-300': notify.type === 'error',
      'border-sky-300': notify.type === 'info',
      'border-amber-300': notify.type === 'warning',
    }"
  >
    <div class="flex">
      <Info v-if="notify.type === 'info'" class="align-middle my-auto text-sky-200" />
      <CheckCircle v-if="notify.type === 'success'" class="align-middle my-auto text-teal-200" />
      <CircleAlert v-if="notify.type === 'warning'" class="align-middle my-auto text-amber-200" />
      <CircleX v-if="notify.type === 'error'" class="align-middle my-auto text-pink-200" />

      <!-- {{ notify.type }} -->
    </div>
    <div class="flex-1">
      <div class="text-lg font-bold">
        {{ notify.name }}
      </div>
      <div>{{ notify.body }}</div>
    </div>
    <button class="text-stone-400 hover:text-pink-500 transition" @click="emit('close', notify.id)">
      <XIcon />
    </button>
  </div>
</template>
