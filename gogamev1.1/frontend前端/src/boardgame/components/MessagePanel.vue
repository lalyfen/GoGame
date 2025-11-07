<template>
  <div class="message-panel" :class="{ hidden: !visible }">
    <MessagePanelHeader @clear="$emit('clear')" />
    
    <div class="message-list" ref="listRef">
      <MessageItem
        v-for="m in messages"
        :key="m.id"
        :text="m.text"
        :type="m.type"
        :timestamp="m.time ? m.time.getTime() : null"
      />
    </div>
  </div>
</template>

<script setup>
/**
 * 消息面板：使用细粒度组件
 */
import { ref, onUpdated } from 'vue';
import MessagePanelHeader from './message/MessagePanelHeader.vue';
import MessageItem from './message/MessageItem.vue';

defineProps({
  messages: { type: Array, required: true },
  visible: { type: Boolean, default: true }
});

defineEmits(['clear']);

const listRef = ref(null);

// 自动滚动到底部
onUpdated(() => {
  if (listRef.value) {
    listRef.value.scrollTop = listRef.value.scrollHeight;
  }
});
</script>

<style scoped>
.message-panel {
  background: white;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  z-index: 100;
  height: 100%;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.message-panel.hidden {
  display: none;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message-list::-webkit-scrollbar {
  width: 0px;
  height: 0px;
}
</style>
