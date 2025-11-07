<template>
  <div class="message-panel-header">
    <div class="message-panel-title">游戏消息</div>
    <button 
      class="clear-messages-btn" 
      @click="$emit('clear')"
    >
      清空消息
    </button>
  </div>
</template>

<script setup>
defineEmits(['clear']);
</script>

<style scoped>
.message-panel-header {
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px 10px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-panel-title {
  font-size: 16px;
  font-weight: bold;
}

.clear-messages-btn {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.3s;
}

.clear-messages-btn:hover {
  background: rgba(255,255,255,0.3);
}
</style>
