<script setup lang="ts">
import RoomRule from "./RoomRule.vue";
  const rules = [
    {name: "Дикие карты", status: false},
    {name: "Общий револьвер", status: true},
    {name: "На опережение", status: false},
    {name: "Вмешательство", status: false},
    {name: "Побочный выброс", status: false}
  ]
</script>

<template>
  <section class="my-4">
    <h2 class="text-xl font-bold mb-2">Игровые правила</h2>
    <RoomRule v-for="rule in rules" :key="rule.name" :name="rule.name" :status="rule.status" />
  </section>
</template>
