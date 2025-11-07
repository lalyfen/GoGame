<template>
  <button type="button" @click="$emit('click')" title="消息框">消息框</button>
  
</template>

<script setup>
defineEmits(['click']);
</script>

<style scoped>
/* 保持最小样式，由父容器控制布局 */
</style>
