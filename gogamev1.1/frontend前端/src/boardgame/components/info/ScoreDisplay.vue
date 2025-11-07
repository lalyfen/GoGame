<template>
  <div class="score-board">
    <h3>比分</h3>
    <div class="score-item">
      <span>黑棋提子：</span>
      <span>{{ captures.black }}</span>
    </div>
    <div class="score-item">
      <span>白棋提子：</span>
      <span>{{ captures.white }}</span>
    </div>
    <div class="score-item komi-setting">
      <span>贴目：</span>
      <input
        type="number"
        class="komi-input"
        :value="komi"
        step="0.25"
        min="0"
        max="15"
        :disabled="disabled"
        @change="onKomiChange"
      />
      <span class="komi-unit">目</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  captures: {
    type: Object,
    required: true
  },
  komi: {
    type: Number,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['updateKomi']);

function onKomiChange(e) {
  const val = parseFloat(e.target.value);
  if (!isNaN(val)) {
    emit('updateKomi', val);
  }
}
</script>

<style scoped>
.score-board {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.score-board h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
}

.score-item {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  font-size: 16px;
}

.komi-setting {
  display: flex;
  align-items: center;
  gap: 5px;
}

.komi-input {
  width: 70px;
  padding: 5px 8px;
  border: 2px solid #DEB068;
  border-radius: 5px;
  font-size: 14px;
  text-align: center;
  background: white;
  transition: all 0.3s ease;
}

.komi-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
}

.komi-input:disabled {
  background: #f5f5f5;
  border-color: #ddd;
  cursor: not-allowed;
  opacity: 0.7;
}

.komi-unit {
  font-size: 14px;
  color: #666;
}
</style>
