<script setup lang="ts">
import type { User } from '@/share/api/types'
import type { Ref } from 'vue'
import HomeButton from '@/components/buttons/HomeButton.vue'
import ErrorLoadingCard from '@/components/ErrorLoadingCard.vue'
import UserStatus from '@/components/home/UserStatus.vue'
import LeaderboardFilters from '@/components/leaderboard/LeaderboardFilters.vue'
import { getRating, getRatingIndex } from '@/share/api'
import { useSettingsStore } from '@/share/stores/settings'
import { useUserStore } from '@/share/stores/user'
import { ref, watchEffect } from 'vue'

const settingState = useSettingsStore()
const userState = useUserStore()

const me = userState.getMe()
const records: Ref<User[]> = ref([])
const topIndex = ref(0)

watchEffect(async () => {
  // FIXME: Почему не обновляемся в карточке пользователя
  records.value = await getRating(settingState.topFilter)
  topIndex.value = await getRatingIndex(userState.userId as string, settingState.topFilter)
})
</script>

<template>
  <section class="text-center justify-between bg-linear-170 from-amber-400/40 rounded-xl p-2 mb-4">
    <h2 class="text-xl mb-2 font-bold">
      Таблица лидеров
    </h2>
    <div class="text-stone-3003">
      Все эти игроки добились успеха упорным трудом. И вы можете быть среди них.
    </div>
  </section>

  <section v-if="records.length" class="h-[60vh] overflow-auto mb-4">
    <UserStatus
      v-for="[index, user] in records.entries()"
      :key="index"
      :user="user"
      :index="index + 1"
      :display-param="settingState.topFilter"
    />
  </section>
  <ErrorLoadingCard
    v-else
    details="Не удалось получить таблицу лидеров"
    :block="true"
    class="my-4"
  />

  <UserStatus
    v-if="me"
    :user="me"
    :index="topIndex"
    class="bg-linear-150 from-amber-700/40"
    :display-param="settingState.topFilter"
  />
  <LeaderboardFilters />

  <section class="p-2 m-2 absolute bottom-0 right-0 flex gap-2">
    <HomeButton :show-name="true" />
  </section>
</template>
