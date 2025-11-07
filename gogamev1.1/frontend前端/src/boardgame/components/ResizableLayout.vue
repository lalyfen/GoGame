<template>
  <div class="resizable-layout" ref="containerRef">
    <div 
      class="resizable-left" 
      :style="{ width: leftWidth + 'px' }"
    >
      <slot name="left"></slot>
    </div>
    
    <div 
      class="resizer"
      @mousedown="startResize"
      v-if="showResizer"
    >
      <div class="resizer-line"></div>
    </div>
    
    <div 
      class="resizable-right"
      :style="{ width: rightWidth + 'px' }"
    >
      <slot name="right"></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps({
  initialLeftWidth: {
    type: Number,
    default: 800
  },
  minLeftWidth: {
    type: Number,
    default: 600
  },
  minRightWidth: {
    type: Number,
    default: 200
  },
  maxRightWidth: {
    type: Number,
    default: 500
  },
  showResizer: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['resize']);

const containerRef = ref(null);
const leftWidth = ref(props.initialLeftWidth);
const isResizing = ref(false);
let startX = 0;
let startLeftWidth = 0;
let containerWidth = 0;

const rightWidth = computed(() => {
  if (!containerRef.value) return props.minRightWidth;
  const totalWidth = containerRef.value.offsetWidth;
  const resizerWidth = props.showResizer ? 10 : 0;
  return Math.max(props.minRightWidth, totalWidth - leftWidth.value - resizerWidth);
});

function startResize(e) {
  isResizing.value = true;
  startX = e.clientX;
  startLeftWidth = leftWidth.value;
  containerWidth = containerRef.value.offsetWidth;
  
  document.body.style.cursor = 'col-resize';
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', stopResize);
  e.preventDefault();
}

function handleMouseMove(e) {
  if (!isResizing.value) return;
  
  const deltaX = e.clientX - startX;
  const resizerWidth = props.showResizer ? 10 : 0;
  let newLeftWidth = startLeftWidth + deltaX;
  
  // 计算右侧宽度
  const newRightWidth = containerWidth - newLeftWidth - resizerWidth;
  
  // 限制左侧最小宽度
  if (newLeftWidth < props.minLeftWidth) {
    newLeftWidth = props.minLeftWidth;
  }
  
  // 限制右侧最小和最大宽度
  if (newRightWidth < props.minRightWidth) {
    newLeftWidth = containerWidth - props.minRightWidth - resizerWidth;
  }
  if (newRightWidth > props.maxRightWidth) {
    newLeftWidth = containerWidth - props.maxRightWidth - resizerWidth;
  }
  
  leftWidth.value = newLeftWidth;
  
  emit('resize', {
    leftWidth: newLeftWidth,
    rightWidth: containerWidth - newLeftWidth - resizerWidth
  });
  
  e.preventDefault();
}

function stopResize() {
  if (!isResizing.value) return;
  
  isResizing.value = false;
  document.body.style.cursor = 'default';
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', stopResize);
}

onMounted(() => {
  // 初始化时调整布局
  if (containerRef.value) {
    const totalWidth = containerRef.value.offsetWidth;
    const resizerWidth = props.showResizer ? 10 : 0;
    
    // 如果初始左侧宽度太大，调整它
    if (leftWidth.value + props.minRightWidth + resizerWidth > totalWidth) {
      leftWidth.value = totalWidth - props.minRightWidth - resizerWidth;
    }
    
    emit('resize', {
      leftWidth: leftWidth.value,
      rightWidth: totalWidth - leftWidth.value - resizerWidth
    });
  }
});

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', stopResize);
});
</script>

<style scoped>
.resizable-layout {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 0;
}

.resizable-left {
  flex-shrink: 0;
  overflow: hidden; /* 不在左侧面板产生滚动，由内部面板自行处理 */
}

.resizable-right {
  flex-shrink: 0;
  overflow: auto;
}

.resizer {
  width: 10px;
  background: transparent;
  cursor: col-resize;
  position: relative;
  user-select: none;
  transition: background 0.3s;
  flex-shrink: 0;
}

.resizer:hover {
  background: rgba(102, 126, 234, 0.1);
}

.resizer:active {
  background: rgba(102, 126, 234, 0.2);
}

.resizer-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #ddd;
  transform: translateX(-50%);
  transition: background 0.3s;
}

.resizer:hover .resizer-line {
  background: #667eea;
  width: 3px;
}
</style>
