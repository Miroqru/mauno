<script setup lang="ts">
const props = defineProps<{
  name: string
  image: string
  active?: boolean
}>()

let imgSrc = ''
if (props.active) {
  imgSrc = `/progressive/${props.image}.png`
} else {
  imgSrc = `/progressive_lowsat/${props.image}.png`
}
</script>

<template>
  <img :src="imgSrc" :alt="props.name" :draggable="props.active" class="h-[128px]" />
</template>
