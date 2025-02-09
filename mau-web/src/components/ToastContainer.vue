<script setup lang="ts">
import NotifyCard from '@/components/NotifyCard.vue'
import { useNotifyStore } from '@/stores/notify'

const notifyState = useNotifyStore()
</script>

<template>
  <section class="fixed top-10 md:right-10 flex flex-col gap-2">
    <NotifyCard
      v-for="notify in notifyState.notifies"
      :key="notify.id"
      :notify="notify"
      @close="(notifyID) => notifyState.removeNotify(notifyID)"
    />
  </section>
</template>
