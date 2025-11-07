<template>
  <div class="position-control">
    <h4>位置控制</h4>
    <div class="position-input-group">
      <input
        type="text"
        class="position-input"
        :value="positionText"
        placeholder="x1-x19,y1-y19"
        maxlength="10"
        @keydown="$emit('positionKeydown', $event)"
        @input="$emit('positionInput', $event.target.value)"
      />
      <button 
        class="btn-primary btn-small" 
        @click="$emit('confirmPosition')"
      >
        落子
      </button>
    </div>
    <div class="position-hint">
      使用方向键移动，Enter键确认
      <br>
      或输入坐标 (x1~x19, y1~y19)
      <br>
      例如: x3,y5 表示第3列第5行
    </div>
  </div>
</template>

<script setup>
defineProps({
  positionText: {
    type: String,
    required: true
  }
});

defineEmits(['positionKeydown', 'positionInput', 'confirmPosition']);
</script>

<style scoped>
.position-control {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 2px solid #DEB068;
  box-sizing: border-box;
  width: 100%;
  overflow: visible; /* 允许按钮悬浮态完整显示 */
}

.position-control h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
}

.position-input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: stretch;
  width: 100%;
  flex-wrap: wrap; /* 窄宽时换行，避免内容被裁剪 */
}

.position-input {
  flex: 1;
  min-width: 0;
  padding: 8px 12px;
  border: 2px solid #DEB068;
  border-radius: 5px;
  font-size: 14px;
  text-align: center;
  background: white;
  transition: all 0.3s ease;
  font-family: 'Courier New', monospace;
  box-sizing: border-box;
}

.position-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
}

.position-hint {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

.btn-primary {
  background: #4CAF50;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.btn-small {
  padding: 8px 16px;
  font-size: 14px;
  flex: 0 0 auto;
  white-space: nowrap;
}
</style>
