<script setup lang="ts">
import UserCard from '@/components/user/UserCard.vue'
import NewGame from '../components/buttons/NewGame.vue'
import RandomGame from '../components/buttons/RandomGame.vue'
import LobbyList from '../components/home/LobbyList.vue'
import ChallengeList from '../components/home/ChallengeList.vue'
import LeaderBoard from '../components/home/LeaderBoard.vue'
import { ref } from 'vue'
import { getMe } from '@/api'

const me = ref(getMe())
</script>

<template>
  <UserCard :user="me" />

  <LobbyList />
  <div class="md:flex md:justify-around md:gap-2">
    <LeaderBoard class="flex-1"/>
    <ChallengeList />
  </div>

  <NewGame />
  <RandomGame />
</template>
