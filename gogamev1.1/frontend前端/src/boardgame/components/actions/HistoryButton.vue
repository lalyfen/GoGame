<template>
  <button type="button" @click="$emit('click')" title="历史棋局列表">历史棋局</button>
  
</template>

<script setup>
defineEmits(['click']);
</script>

<style scoped>
/* 保持最小样式，由父容器控制布局 */
</style>
