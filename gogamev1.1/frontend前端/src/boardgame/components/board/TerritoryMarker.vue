<template>
  <div 
    class="territory-marker"
    :class="color"
  ></div>
</template>

<script setup>
const props = defineProps({
  color: {
    type: String,
    required: true, // 'black' | 'white'
    validator: (value) => ['black', 'white'].includes(value)
  }
});
</script>

<style scoped>
.territory-marker {
  position: absolute;
  width: 10px;
  height: 10px;
  top: 10px;
  left: 10px;
  z-index: 3;
  pointer-events: none;
}

.territory-marker.black {
  background: rgba(0, 0, 0, 0.6);
}

.territory-marker.white {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #999;
}
</style>
