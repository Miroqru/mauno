<script setup lang="ts">
import type { Room } from '@/types'
import type { Ref } from 'vue'
import { getRoomById } from '@/api'
import HomeButton from '@/components/buttons/HomeButton.vue'
import RoomButtons from '@/components/room/RoomButtons.vue'
import RoomModes from '@/components/room/RoomModes.vue'
import RoomOwner from '@/components/room/RoomOwner.vue'
import RoomPlayers from '@/components/room/RoomPlayers.vue'
import RoomSettings from '@/components/room/RoomSettings.vue'
import { useUserStore } from '@/stores/user'
import { Squirrel } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const userState = useUserStore()
const route = useRoute()
const room: Ref<Room | null> = ref(null)

onMounted(async () => {
  const res = await getRoomById(route.params.id as string)
  if (res.type === 'right') {
    room.value = res.value
  }
})
</script>

<template>
  <div v-if="room">
    <RoomOwner :room="room" />

    <div class="md:flex gap-4">
      <RoomPlayers :room="room" class="flex-1" />
      <RoomSettings
        v-if="userState.userId === room.owner.username && room.status !== 'ended'"
        :room="room"
      />
      <RoomModes :room="room" />
    </div>

    <RoomButtons v-if="room.status !== 'ended'" :room="room" />
    <section v-else class="p-2 m-2 absolute bottom-0 right-0 flex gap-2">
      <HomeButton :show-name="true" />
    </section>
  </div>

  <!-- На случай если не удалось загрузить комнату -->
  <div v-else>
    <section
      class="text-center flex justify-center gap-4 bg-linear-160 from-rose-400/40 rounded-xl p-2 mb-4"
    >
      <Squirrel :size="64" />
      <div>
        <h2 class="text-xl mb-2 font-bold">
          А где комната?
        </h2>
        <div class="text-stone-300">
          Кажется что-то пошло не так.
        </div>
      </div>
    </section>

    <section class="p-2 m-2 absolute bottom-0 right-0 flex gap-2">
      <HomeButton :show-name="true" />
    </section>
  </div>
</template>
