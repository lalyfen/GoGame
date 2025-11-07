<template>
  <MessagePanel :messages="messages" :visible="true" @clear="onClear" />
</template>

<script setup>
import { inject } from 'vue';
import MessagePanel from '../components/MessagePanel.vue';

const messages = inject('messages');
const clearMessages = inject('clearMessages');

function onClear() {
  if (typeof clearMessages === 'function') {
    clearMessages();
  } else if (clearMessages && typeof clearMessages.value === 'function') {
    clearMessages.value();
  }
}
</script>

<style scoped>
/* 空样式 */
</style>
