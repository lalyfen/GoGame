<template>
  <div 
    class="intersection"
    :class="[hoverClass, edgeClasses]"
    @click="onClick"
    @mouseenter="onHover"
  >
    <slot></slot><!-- 用于插入星点 -->
    <Stone 
      v-if="stone" 
      :color="stone"
      :is-dead="isDead"
      :is-last-move="isLastMove"
    />
    <TerritoryMarker v-if="territory" :color="territory" />
    <PositionIndicator v-if="showIndicator" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import Stone from './Stone.vue';
import TerritoryMarker from './TerritoryMarker.vue';
import PositionIndicator from './PositionIndicator.vue';

const props = defineProps({
  row: {
    type: Number,
    required: true
  },
  col: {
    type: Number,
    required: true
  },
  isTopEdge: {
    type: Boolean,
    default: false
  },
  isBottomEdge: {
    type: Boolean,
    default: false
  },
  isLeftEdge: {
    type: Boolean,
    default: false
  },
  isRightEdge: {
    type: Boolean,
    default: false
  },
  stone: {
    type: String,
    default: null // 'black' | 'white' | null
  },
  isDead: {
    type: Boolean,
    default: false
  },
  isLastMove: {
    type: Boolean,
    default: false
  },
  territory: {
    type: String,
    default: null // 'black' | 'white' | null
  },
  showIndicator: {
    type: Boolean,
    default: false
  },
  currentPlayer: {
    type: String,
    default: 'black'
  },
  gameOver: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['click', 'hover']);

const hoverClass = computed(() => {
  if (props.gameOver || props.stone) return '';
  return props.currentPlayer === 'black' ? 'black-hover' : 'white-hover';
});

const edgeClasses = computed(() => ({
  'edge-top': props.isTopEdge,
  'edge-bottom': props.isBottomEdge,
  'edge-left': props.isLeftEdge,
  'edge-right': props.isRightEdge,
}));

function onClick() {
  emit('click', props.row, props.col);
}

function onHover() {
  emit('hover', props.row, props.col);
}
</script>

<style scoped>
.intersection {
  width: 100%;
  height: 100%;
  position: relative;
  cursor: pointer;
}

.intersection::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0; /* 默认横线贯穿整格 */
  height: 1px;
  background: #333;
}

.intersection::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0; /* 默认竖线贯穿整格 */
  width: 1px;
  background: #333;
}

/* 边界裁剪：让边界处只画向棋盘内部的半段 */
.intersection.edge-left::before {
  left: 50%;
  right: 0; /* 仅从中心到右侧 */
}

.intersection.edge-right::before {
  left: 0;
  right: 50%; /* 仅从左侧到中心 */
}

.intersection.edge-top::after {
  top: 50%;
  bottom: 0; /* 仅从中心到下方 */
}

.intersection.edge-bottom::after {
  top: 0;
  bottom: 50%; /* 仅从上方到中心 */
}

.intersection:hover::before {
  content: '';
  position: absolute;
  width: 80%;
  height: 80%;
  border-radius: 50%;
  top: 3px;
  left: 3px;
  opacity: 0.3;
  z-index: 1;
}

.intersection.black-hover:hover::before {
  background: black;
}

.intersection.white-hover:hover::before {
  background: white;
  border: 1px solid #999;
}
</style>
