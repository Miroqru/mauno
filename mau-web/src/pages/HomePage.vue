<script setup lang="ts">
import NewGame from '@/components/buttons/NewGame.vue'
import RandomGame from '@/components/buttons/RandomGame.vue'
import ChallengeList from '@/components/home/ChallengeList.vue'
import LeaderBoard from '@/components/home/LeaderBoard.vue'
import RoomList from '@/components/home/RoomList.vue'
import UserCard from '@/components/user/UserCard.vue'
import { fetchLeaderboardIndex } from '@/share/api/api'

import { useNotifyStore } from '@/share/stores/notify'
import { useUserStore } from '@/share/stores/user'
import { onMounted, ref } from 'vue'
import RoomCard from '../components/room/RoomCard.vue'
import UserCardPlaceholder from '../components/user/UserCardPlaceholder.vue'

const userStore = useUserStore()
const me = userStore.getMe()
const room = userStore.fetchRoom()
const isMobile = /android|iPad|iPhone|iPod/.test(navigator.userAgent)
const topIndex = ref(0)
const notifyState = useNotifyStore()

onMounted(async () => {
  if (me.value == null) {
    notifyState.addNotify('Оффлайн', 'Mau сервер не отвечает', 'error')
    return
  }

  const res = await fetchLeaderboardIndex(me.value.username, 'gems')
  if (res.type === 'right') {
    topIndex.value = res.value
  } else {
    notifyState.addNotify('Таблица лидеров', 'Mau сервер не отвечает', 'error')
  }
})
</script>

<template>
  <UserCard v-if="me" :user="me" :top-index="topIndex" />
  <UserCardPlaceholder v-else />

  <RoomCard v-if="room && isMobile" :room="room" />

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
