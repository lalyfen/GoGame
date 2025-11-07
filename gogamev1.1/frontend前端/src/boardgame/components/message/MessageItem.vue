<template>
  <div 
    class="message-item"
    :class="type"
  >
    <div class="message-content" v-html="text"></div>
    <div v-if="timestamp" class="message-time">
      {{ formatTime(timestamp) }}
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  text: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['info', 'warning', 'error', 'success', 'game-over'].includes(value)
  },
  timestamp: {
    type: Number,
    default: null
  }
});

function formatTime(ts) {
  if (!ts) return '';
  const date = new Date(ts);
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
</script>

<style scoped>
.message-item {
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  animation: slideInRight 0.3s ease;
  position: relative;
  padding-left: 40px;
}

.message-content :where(p, ul, ol, li, strong, em, br) {
  all: revert;
}

.message-item::before {
  content: '';
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.message-item.info {
  background: #E3F2FD;
  color: #1976D2;
  border-left: 3px solid #2196F3;
}

.message-item.info::before {
  content: 'ℹ';
  background: #2196F3;
  color: white;
}

.message-item.warning {
  background: #FFF3E0;
  color: #F57C00;
  border-left: 3px solid #FF9800;
}

.message-item.warning::before {
  content: '⚠';
  background: #FF9800;
  color: white;
}

.message-item.error {
  background: #FFEBEE;
  color: #C62828;
  border-left: 3px solid #F44336;
}

.message-item.error::before {
  content: '✕';
  background: #F44336;
  color: white;
}

.message-item.success {
  background: #E8F5E9;
  color: #2E7D32;
  border-left: 3px solid #4CAF50;
}

.message-item.success::before {
  content: '✓';
  background: #4CAF50;
  color: white;
}

/* 终局结果消息样式 */
.message-item.game-over {
  background: #E3F2FD;
  color: #1976D2;
  border-left: 3px solid #2196F3;
}

.message-item.game-over::before {
  content: '🏆';
  background: #2196F3;
  color: white;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 5px;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 内嵌 game-result 结构的默认样式（来自逻辑层的 HTML） */
.message-content .game-result {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
}

.message-content .game-result .result-title {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.message-content .game-result .winner-info {
  font-weight: 600;
  margin-bottom: 10px;
}

.message-content .game-result .score-section {
  margin-top: 8px;
}

.message-content .game-result .score-table {
  width: 100%;
  border-collapse: collapse;
}

.message-content .game-result .score-table td {
  padding: 4px 6px;
  border-bottom: 1px dashed #ddd;
}

.message-content .game-result .score-table .total-row td {
  font-weight: 700;
  border-top: 1px solid #ccc;
  border-bottom: none;
}
</style>
