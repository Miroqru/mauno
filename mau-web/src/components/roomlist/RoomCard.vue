<script setup lang="ts">
import type { Room } from '@/types'
import dayjs from 'dayjs'
import { Gem, Lock, User2 } from 'lucide-vue-next'
import UserAvatar from '../user/UserAvatar.vue'
import RoomStatus from './RoomStatus.vue'

const { room } = defineProps<{ room: Room }>()

const date = dayjs(room.create_time)
</script>

<template>
  <RouterLink
    :to="`/room/${room.id}`"
    class="inline-flex flex-col 2 m-2 bg-stone-800 p-1 rounded-md transition hover:bg-stone-700"
  >
    <div class="flex gap-2">
      <RoomStatus :status="room.status" />
      <div class="flex gap-1">
        <div class="text-lg text-middle m-auto font-bold">
          {{ room.name }}
        </div>
        <Lock :size="14" class="text-stone-300" />
      </div>
    </div>
    <div class="flex gap-2 justify-between">
      <div class="flex gap-2">
        <UserAvatar :user="room.owner" />
        <div class="text-middle m-auto flex-1 font-bold">
          {{ room.owner.name }}
        </div>
        <div class="text-stone-300 text-sm text-middle my-auto">
          {{ date.format('DD.M mm:HH') }}
        </div>
      </div>
      <div class="flex gap-2">
        <div class="flex gap-1 mr-4 h-[24px] m-auto text-stone-300">
          {{ room.players.length }}/{{ room.max_players }} <User2 />
        </div>
        <div class="inline-flex gap-1 mr-2 text-middle m-auto text-teal-200">
          {{ room.gems }} <Gem :size="24" />
        </div>
      </div>
    </div>
  </RouterLink>
</template>
