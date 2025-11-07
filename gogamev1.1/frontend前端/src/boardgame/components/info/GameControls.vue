<template>
  <div class="controls">
    <button
      class="btn-secondary"
      @click="$emit('pass')"
      :disabled="gameOver"
    >
      弃手 (Pass)
    </button>

    <button
      class="btn-primary"
      @click="$emit('endGame')"
      :disabled="gameOver"
    >
      结束对局
    </button>
  </div>
</template>

<script setup>
defineProps({
  gameOver: {
    type: Boolean,
    default: false
  },
  scoringPhase: {
    type: Boolean,
    default: false
  },
  markingMode: {
    type: Boolean,
    default: false
  }
});

defineEmits(['pass', 'endGame']);
</script>

<style scoped>
.controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.btn-secondary {
  background: #ff9800;
  color: white;
}

.btn-secondary:hover {
  background: #e68900;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

button:disabled:hover {
  transform: none !important;
  box-shadow: none !important;
}
</style>
