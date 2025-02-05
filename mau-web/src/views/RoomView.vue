<script setup lang="ts">
import { getRoomById, getUserById } from '@/api'
import HomeButton from '@/components/buttons/HomeButton.vue'
import RoomButtons from '@/components/room/RoomButtons.vue'
import RoomModes from '@/components/room/RoomModes.vue'
import RoomOwner from '@/components/room/RoomOwner.vue'
import RoomPlayers from '@/components/room/RoomPlayers.vue'
import RoomSettings from '@/components/room/RoomSettings.vue'
import { useUserStore } from '@/stores/user'
import type { User } from '@/types'
import { Squirrel } from 'lucide-vue-next'
import { onMounted, ref, type Ref } from 'vue'
import { useRoute } from 'vue-router'

const userState = useUserStore()
const route = useRoute()
const room = ref(getRoomById(route.params.id as string))
const owner: Ref<User | null> = ref(null)

onMounted(async () => {
  if (room.value) {
    owner.value = await getUserById(room.value.owner)
  }
})
</script>

<template>
  <div v-if="room && owner">
    <RoomOwner :room="room" :owner="owner" />
    <RoomPlayers :players="room?.players" :is-owner="userState.userId == room.owner" />

    <div class="md:flex justify-around gap-4">
      <RoomSettings v-if="userState.userId == room.owner" :room="room" />
      <RoomModes class="flex-1" />
    </div>

    <RoomButtons :room="room" />
  </div>

  <!-- На случай если не удалось загрузить комнату -->
  <div v-else>
    <section
      class="text-center flex justify-center gap-4 bg-linear-160 from-rose-400/40 rounded-xl p-2 mb-4"
    >
      <Squirrel :size="64" />
      <div>
        <h2 class="text-xl mb-2 font-bold">А где комната?</h2>
        <div class="text-stone-300">Кажется что-то пошло не так.</div>
      </div>
    </section>

    <section class="p-2 m-2 fixed bottom-0 right-0 flex gap-2">
      <HomeButton :show-name="true" />
    </section>
  </div>
</template>
