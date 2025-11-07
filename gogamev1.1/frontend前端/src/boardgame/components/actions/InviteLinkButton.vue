<template>
  <button type="button" @click="$emit('click')" title="对局邀请链接">邀请链接</button>
  
</template>

<script setup>
defineEmits(['click']);
</script>

<style scoped>
/* 保持最小样式，由父容器控制布局 */
</style>
