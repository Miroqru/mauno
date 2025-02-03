<script setup lang="ts">
import HomeButton from '@/components/buttons/HomeButton.vue'
import RoomCard from '@/components/room/RoomCard.vue'
import GameRooms from '@/components/roomlist/GameRooms.vue'
import RoomButtons from '@/components/roomlist/RoomButtons.vue'
import { useUserStore } from '@/stores/user'
import { computed, ref } from 'vue'

const userState = useUserStore()
const room = ref(userState.getRoom())
const owner = computed(async () => {
  if (!room.value) {
    return null
  }

  return await etUserById(room.value.owner)
})
const isMobile = /android|iPad|iPhone|iPod/.test(navigator.userAgent)
</script>

<template>
  <section
    class="text-center justify-between bg-linear-160 from-emerald-300/40 rounded-xl p-2 mb-4"
  >
    <h2 class="text-xl mb-2 font-bold">Игровые комнаты</h2>
    <div class="text-stone-3003">Место, где игроки собираются вместе.</div>
  </section>

  <div class="md:flex md:gap-2">
    <div>
      <RoomButtons :mobile="isMobile" />
      <RoomCard v-if="room && owner" :room="room" :owner="owner" />
    </div>
    <GameRooms class="flex-1" />
  </div>

  <section v-if="isMobile" class="p-2 m-2 fixed bottom-0 right-0 flex gap-2">
    <HomeButton :show-name="true" />
  </section>
</template>
