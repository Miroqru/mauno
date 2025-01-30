<script setup lang="ts">
import HomeButton from '@/components/buttons/HomeButton.vue'
import Filters from '../components/leaderboard/Filters.vue'
import TopRecord from '../components/leaderboard/TopRecord.vue'

const records: object[] = []

for (let index = 0; index < 100; index++) {
  records.push({ index: index, name: `user #${1000 - index}`, value: 1000 - 7 * index })
}
</script>

<template>
  <section class="text-center justify-between bg-linear-160 from-amber-300/40 rounded-xl p-2 mb-4">
    <h2 class="text-xl mb-2 font-bold">Таблица лидеров</h2>
    <div class="text-stone-3003">
      Все эти игроки добились успеха упорным трудом. И вы можете быть среди них.
    </div>
  </section>

  <section class="h-[60vh] overflow-auto mb-4">
    <TopRecord
      v-for="record in records"
      :key="record.index"
      :index="record.index"
      :name="record.name"
      :value="record.value"
    />
  </section>

  <RouterLink to="/me">
    <TopRecord
      :index="172"
      name="Milinuri"
      :value="100"
      class="border-2 border-stone-700 bg-linear-160 from-amber-300/30"
    />
  </RouterLink>
  <Filters />

  <HomeButton />
</template>
