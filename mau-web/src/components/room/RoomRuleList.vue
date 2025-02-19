<script setup lang="ts">
import type { Room, RoomRuleData } from '@/share/api/types'
import type { Ref } from 'vue'
import { getRoomRules, setRoomRules } from '@/share/api'
import { Sparkle } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import RoomRule from './RoomRule.vue'

const { room } = defineProps<{ room: Room }>()
const rules: Ref<RoomRuleData[]> = ref([])

onMounted(async () => {
  // TODO: Глобальный контекст комнаты
  rules.value = await getRoomRules(room.id)
})

async function setModes() {
  const active_rules = rules.value.filter(rule => rule.status).map(rule => rule.key)

  await setRoomRules(room.id, active_rules)
}
</script>

<template>
  <section class="my-4 md:p-2 md:border-2 md:border-stone-700 rounded-md">
    <h2 class="text-xl font-bold mb-2">
      Игровые правила
    </h2>
    <RoomRule
      v-for="[index, rule] in rules.entries()"
      :key="rule.name"
      :rule="rule"
      @update="rules[index].status = !rules[index].status"
    />
    <button
      class="p-1 bg-stone-700 rounded-lg transition hover:bg-teal-600 flex gao-4"
      @click="setModes"
    >
      <Sparkle /> Применить
    </button>
  </section>
</template>
