<script setup lang="ts">
import type { Room, RoomRuleData } from '@/share/api/types'
import type { Ref } from 'vue'
import { fetchRoomRules, updateRoomRules } from '@/share/api/api'
import { useUserStore } from '@/share/stores/user'
import { Sparkle } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import RoomRule from './RoomRule.vue'

const { room } = defineProps<{ room: Room }>()
const rules: Ref<RoomRuleData[]> = ref([])

const userState = useUserStore()

onMounted(async () => {
  const res = await fetchRoomRules(room.id)
  if (res.type === 'right') {
    rules.value = res.value
  }
})

async function updateRoomSubmit() {
  const active_rules = rules.value.filter(rule => rule.status).map(rule => rule.key)

  const res = await updateRoomRules(room.id, userState.userToken as string, active_rules)
  if (res.type === 'right') {
    rules.value = res.value
  }
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
      @click="updateRoomSubmit"
    >
      <Sparkle /> Применить
    </button>
  </section>
</template>
