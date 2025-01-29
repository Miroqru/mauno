<script setup lang="ts">
  import UserCard from '@/components/user/UserCard.vue'
import NewGame from '../components/buttons/NewGame.vue'
import ContentCard from '../components/ContentCard.vue'
import RandomGame from '../components/buttons/RandomGame.vue'
import LobbyList from '../components/home/LobbyList.vue'
import ChallengeList from '../components/home/ChallengeList.vue'
import LeaderBoard from '../components/home/LeaderBoard.vue'
</script>

<template>
  <UserCard />

  <LobbyList />
  <ChallengeList />
  <LeaderBoard />

  <NewGame />
  <RandomGame />
</template>
