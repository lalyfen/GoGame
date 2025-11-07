<template>
  <Teleport to="body">
    <div class="modal-overlay" @click="closeOnBackdrop && $emit('close')" v-show="visible">
      <div class="modal-container" @click.stop :class="{ 'modal-entering': entering, 'modal-leaving': leaving }">
        <div class="modal-header">
          <div class="modal-icon">⚠️</div>
          <h2>确认登出</h2>
          <button class="modal-close" @click="$emit('close')" aria-label="关闭">
            <span>✕</span>
          </button>
        </div>

        <div class="modal-content">
          <p>您确定要登出当前账户吗？</p>
          <div class="modal-warning">
            <span class="warning-icon">⚠️</span>
            <span>登出后需要重新登录才能访问受保护的内容</span>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-cancel" @click="$emit('close')" :disabled="loading">
            取消
          </button>
          <button class="btn btn-logout" @click="handleLogout" :disabled="loading">
            <div class="btn-content">
              <span v-if="!loading">确认登出</span>
              <span v-else class="loading-spinner">
                <span class="spinner"></span>
                登出中...
              </span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
/**
 * 登出确认对话框组件
 * 提供炫酷的登出确认界面
 */
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close', 'confirm'])

const loading = ref(false)
const entering = ref(false)
const leaving = ref(false)

const handleLogout = async () => {
  loading.value = true
  try {
    await emit('confirm')
    // 等待确认函数完成后再关闭
    await nextTick()
    emit('close')
  } finally {
    loading.value = false
  }
}

// 动画处理
watch(() => props.visible, (newVal) => {
  if (newVal) {
    entering.value = true
    leaving.value = false
    setTimeout(() => {
      entering.value = false
    }, 300)
  } else {
    leaving.value = true
    entering.value = false
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.modal-container {
  background: linear-gradient(180deg, var(--card), #081020);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 0;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05);
  max-width: 480px;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
  transform: scale(0.9) translateY(20px);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-container.modal-entering {
  transform: scale(1) translateY(0);
}

.modal-container.modal-leaving {
  transform: scale(0.9) translateY(20px);
  opacity: 0;
}

.modal-header {
  display: flex;
  align-items: center;
  padding: 32px 32px 24px 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-icon {
  font-size: 32px;
  margin-right: 16px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #e6eef8;
  flex: 1;
}

.modal-close {
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 18px;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  transform: scale(1.05);
}

.modal-content {
  padding: 24px 32px;
}

.modal-content p {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: var(--muted);
  line-height: 1.5;
}

.modal-warning {
  display: flex;
  align-items: center;
  background: rgba(255, 80, 80, 0.1);
  border: 1px solid rgba(255, 80, 80, 0.2);
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
}

.warning-icon {
  font-size: 18px;
  margin-right: 12px;
  color: #ff8080;
}

.modal-warning span:last-child {
  font-size: 14px;
  color: #ffb4b4;
}

.modal-footer {
  display: flex;
  gap: 16px;
  padding: 24px 32px 32px 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn {
  padding: 14px 24px;
  border-radius: 12px;
  border: none;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
  position: relative;
  overflow: hidden;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-cancel:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  transform: translateY(-2px);
}

.btn-logout {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
  box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
}

.btn-logout:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(255, 107, 107, 0.4);
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-spinner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 浅色主题适配 */
.app.light .modal-container {
  background: linear-gradient(180deg, #ffffff, #f6f9ff);
  border: 1px solid rgba(12, 20, 30, 0.1);
  box-shadow: 0 20px 60px rgba(12, 30, 60, 0.15), 0 0 0 1px rgba(12, 20, 30, 0.05);
}

.app.light .modal-header h2 {
  color: #0b1320;
}

.app.light .modal-content p {
  color: #3f5160;
}

.app.light .modal-close {
  background: rgba(12, 20, 30, 0.05);
  color: #3f5160;
}

.app.light .modal-close:hover {
  background: rgba(12, 20, 30, 0.1);
  color: #0b1320;
}

.app.light .modal-warning {
  background: rgba(255, 80, 80, 0.05);
  border: 1px solid rgba(255, 80, 80, 0.1);
}

.app.light .btn-cancel {
  background: rgba(12, 20, 30, 0.05);
  color: #3f5160;
  border: 1px solid rgba(12, 20, 30, 0.1);
}

.app.light .btn-cancel:hover:not(:disabled) {
  background: rgba(12, 20, 30, 0.1);
  color: #0b1320;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .modal-container {
    width: 95%;
    margin: 20px;
  }

  .modal-header {
    padding: 24px 24px 20px 24px;
  }

  .modal-content {
    padding: 20px 24px;
  }

  .modal-footer {
    padding: 20px 24px 24px 24px;
    flex-direction: column;
  }

  .modal-header h2 {
    font-size: 20px;
  }

  .modal-icon {
    font-size: 28px;
  }
}
</style>