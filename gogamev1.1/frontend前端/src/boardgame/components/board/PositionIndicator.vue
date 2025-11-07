<template>
  <div class="position-indicator"></div>
</template>

<script setup>
// 位置指示器 - 纯展示组件，显示当前选中的位置
</script>

<style scoped>
.position-indicator {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
  animation: pulse 1.5s infinite;
}

.position-indicator::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 80%;
  height: 80%;
  border: 2px solid #ff6b35;
  border-radius: 50%;
  box-sizing: border-box;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
