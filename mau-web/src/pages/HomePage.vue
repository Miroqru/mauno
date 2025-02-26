<script setup lang="ts">
import type { GameContext } from '@/share/api/types'
import type { Ref } from 'vue'
import NewGame from '@/components/buttons/NewGame.vue'
import RandomGame from '@/components/buttons/RandomGame.vue'
import ChallengeList from '@/components/home/ChallengeList.vue'
import LeaderBoard from '@/components/home/LeaderBoard.vue'

import RoomList from '@/components/home/RoomList.vue'
import GameCard from '@/components/room/GameCard.vue'
import UserCard from '@/components/user/UserCard.vue'
import { getGame, getRatingIndex } from '@/share/api'
import { useUserStore } from '@/share/stores/user'
import { ref, watchEffect } from 'vue'
import RoomCard from '../components/room/RoomCard.vue'
import UserCardPlaceholder from '../components/user/UserCardPlaceholder.vue'

const userStore = useUserStore()
const me = userStore.getMe()
const room = userStore.fetchRoom()
const game: Ref<GameContext | null> = ref(null)
const isMobile = /android|iPad|iPhone|iPod/.test(navigator.userAgent)
const topIndex = ref(0)

watchEffect(async () => {
  if (me.value === null) {
    return
  }
  topIndex.value = await getRatingIndex(me.value.username, 'gems')
  game.value = await getGame()
})
</script>

<template>
  <UserCard v-if="me" :user="me" :top-index="topIndex" />
  <UserCardPlaceholder v-else />

  <GameCard v-if="game" :game="game" />
  <RoomCard v-else-if="room && isMobile" :room="room" />

  <div class="md:flex md:gap-2">
    <section v-if="!isMobile" class="p-2 m-2 flex flex-col gap-2">
      <NewGame :show-name="true" />
      <RandomGame :show-name="true" />
    </section>
    <LeaderBoard class="flex-1" />
  </div>

  <div class="md:flex md:justify-around md:gap-2">
    <RoomList class="flex-1" />
    <div>
      <RoomCard v-if="room && !isMobile" :room="room" />
      <ChallengeList />
    </div>
  </div>

  <section v-if="isMobile" class="p-2 m-2 fixed bottom-0 right-0 flex gap-2">
    <RandomGame />
    <NewGame />
  </section>
</template>
