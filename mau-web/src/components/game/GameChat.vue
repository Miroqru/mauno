<script setup lang="ts">
import ChatMessage from '@/components/game/ChatMessage.vue'
import { getGame } from '@/share/api'
import type { GameContext } from '@/share/api/types'
import { ref, type Ref } from 'vue'

const { context } = defineProps<{ context: GameContext }>()

interface Message {
  name: string
  data: string
}

const messages: Ref<Message[]> = ref([])

const ws = new WebSocket(`ws://localhost:8000/game/${context.game?.room_id}`)

ws.onerror = (event) => {
  console.error('connect to', event)
}

ws.onmessage = async (event) => {
  const data = JSON.parse(event.data)
  messages.value.push({ name: data.from_player, data: `${data.event_type}: ${data.data}` })
  await getGame()
}
</script>

<template>
  <section class="bg-stone-950 p-2 m-4 rounded-xl h-[20vh] md:h-[30vh] overflow-y-auto">
    <ChatMessage
      v-for="[index, message] in messages.entries()"
      :key="index"
      :name="message.name"
      :message="message.data"
    />
  </section>
</template>
