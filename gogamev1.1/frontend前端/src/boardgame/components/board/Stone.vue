<template>
  <div 
    class="stone"
    :class="[colorClass, { dead: isDead, 'last-move': isLastMove }]"
  ></div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  color: {
    type: String,
    required: true, // 'black' | 'white'
    validator: (value) => ['black', 'white'].includes(value)
  },
  isDead: {
    type: Boolean,
    default: false
  },
  isLastMove: {
    type: Boolean,
    default: false
  }
});

const colorClass = computed(() => props.color);
</script>

<style scoped>
.stone {
  position: absolute;
  width: 84%;
  height: 84%;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  z-index: 2;
  transition: all 0.2s ease;
  box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.stone.black {
  background: radial-gradient(circle at 30% 30%, #555, #000);
}

.stone.white {
  background: radial-gradient(circle at 30% 30%, #fff, #e0e0e0);
  border: 1px solid #999;
}

.stone.dead {
  opacity: 0.5;
}

.stone.dead::after {
  content: '×';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 20px;
  font-weight: bold;
  color: red;
}

.stone.last-move::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 30%;
  height: 30%;
  border-radius: 50%;
  background: rgba(255, 0, 0, 0.6);
}
</style>
