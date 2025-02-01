<script setup lang="ts">
import { getTopCards, getTopGames, getTopGems, getTopWins, getUserTopIndex } from '@/api'
import HomeButton from '@/components/buttons/HomeButton.vue'
import { useSettingsStore } from '@/stores/settings'
import { useUserStore } from '@/stores/user'
import { computed } from 'vue'
import UserStatus from '../components/home/UserStatus.vue'
import Filters from '../components/leaderboard/Filters.vue'

const settingState = useSettingsStore()
const userState = useUserStore()

const records = computed(() => {
  let leaders = []
  if (settingState.topFilter == 'gems') {
    leaders = getTopGems()
  } else if (settingState.topFilter == 'games') {
    leaders = getTopGames()
  } else if (settingState.topFilter == 'wins') {
    leaders = getTopWins()
  } else if (settingState.topFilter == 'cards') {
    leaders = getTopCards()
  }

  return leaders
})

const me = userState.getMe()
const topIndex = computed(() => getUserTopIndex(me.id, settingState.topFilter))
</script>

<template>
  <section class="text-center justify-between bg-linear-170 from-amber-400/40 rounded-xl p-2 mb-4">
    <h2 class="text-xl mb-2 font-bold">Таблица лидеров</h2>
    <div class="text-stone-3003">
      Все эти игроки добились успеха упорным трудом. И вы можете быть среди них.
    </div>
  </section>

  <section class="h-[60vh] overflow-auto mb-4">
    <UserStatus
      v-for="[index, user] in records.entries()"
      :key="index"
      :user="user"
      :index="index + 1"
    />
  </section>

  <UserStatus :user="me" :index="topIndex" class="bg-linear-150 from-amber-700/40" />
  <Filters />

  <section class="p-2 m-2 fixed bottom-0 right-0 flex gap-2">
    <HomeButton />
  </section>
</template>
