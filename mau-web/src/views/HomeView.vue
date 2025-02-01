<script setup lang="ts">
import NewGame from '@/components/buttons/NewGame.vue'
import RandomGame from '@/components/buttons/RandomGame.vue'
import ChallengeList from '@/components/home/ChallengeList.vue'
import LeaderBoard from '@/components/home/LeaderBoard.vue'
import RoomList from '@/components/home/RoomList.vue'
import UserCard from '@/components/user/UserCard.vue'
import { useUserStore } from '@/stores/user'

import { ref } from 'vue'

const userStore = useUserStore()
const me = ref(userStore.getMe())

const isMobile = /android|iPad|iPhone|iPod/.test(navigator.userAgent)
</script>

<template>
  <UserCard :user="me" />

  <div class="flex gap-2">
    <section v-if="!isMobile" class="p-2 m-2">
      <NewGame :show-name="true" />
      <RandomGame :show-name="true" />
    </section>
    <LeaderBoard class="flex-1" />
  </div>

  <div class="md:flex md:justify-around md:gap-2">
    <RoomList class="flex-1" />
    <ChallengeList />
  </div>

  <section v-if="isMobile" class="p-2 m-2 fixed bottom-0 right-0 flex gap-2">
    <RandomGame />
    <NewGame />
  </section>
</template>
