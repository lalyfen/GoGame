<template>
  <div class="board-labels">
    <!-- 顶部列标签：直接放入与棋盘同尺寸的网格中，精确对齐每一列中心 -->
    <template v-for="i in size" :key="`col-${i}`">
      <div
        class="label-col-element"
        :style="{ gridColumn: i, gridRow: 1 }"
      >
        <span class="col-text" :data-len="colLabels[i - 1].length">{{ colLabels[i - 1] }}</span>
      </div>
    </template>

    <!-- 左侧行标签：同样使用网格行定位，保证与横线对齐 -->
    <template v-for="i in size" :key="`row-${i}`">
      <div
        class="label-row-element"
        :style="{ gridColumn: 1, gridRow: i }"
      >
        <span class="row-text" :data-len="rowLabels[i - 1].length">{{ rowLabels[i - 1] }}</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  size: {
    type: Number,
    required: true
  }
});

// 为了更精准的对齐，改用 CSS Grid 来对齐标签与棋盘网格，无需再计算百分比定位

// 行标签（竖向 - 大写汉字）
const rowLabels = computed(() => {
  const labels = ['壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '拾', 
                  '拾壹', '拾贰', '拾叁', '拾肆', '拾伍', '拾陆', '拾柒', '拾捌', '拾玖'];
  return labels.slice(0, props.size);
});

// 列标签（横向 - 小写数字）
const colLabels = computed(() => {
  const labels = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', 
                  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九'];
  return labels.slice(0, props.size);
});
</script>

<style scoped>
.board-labels {
  position: absolute;
  inset: var(--board-pad, 5%);
  pointer-events: none;
  z-index: 1;
  /* 微调变量：用于修正不同字体在竖排下的视觉居中偏差 */
  --col-offset-x: 0em; /* 默认不再横向偏移，确保与竖线中心一致 */
  /* 统一控制字号，显著缩小 */
  --label-col-size: clamp(6px, 0.6vw, 10px);
  --label-row-size: clamp(6px, 0.6vw, 10px);
  --label-col-offset-y: -10%; /* 恢复：默认稍微上移，远离棋盘内部 */
  --label-row-indent-x: -20%; /* 左侧行标签的横向缩进（负值更靠左，正值更靠右） */
  display: grid;
  grid-template-columns: repeat(v-bind(size), 1fr);
  grid-template-rows: repeat(v-bind(size), 1fr);
}

.label-row-element {
  justify-self: start;
  align-self: center;
  transform: translateX(var(--label-row-indent-x)); /* 可调缩进，避免压住边界 */
  font-size: var(--label-row-size);
  color: #333;
  font-weight: bold;
  white-space: nowrap;
  line-height: 1;
}

.label-row-element .row-text {
  display: inline-block;
  line-height: 1;
}

/* 两字的行标签（如“拾壹”）可单独微调与边界距离 */
.label-row-element .row-text[data-len="2"] {
  margin-inline-start: -1em;
}

.label-col-element {
  justify-self: center;
  align-self: start; /* 靠近单元格顶部 */
  transform: translateY(var(--label-col-offset-y)); /* 默认较小上移，远离上边界可调 */
  font-size: var(--label-col-size);
  color: #333;
  font-weight: bold;
}

.label-col-element .col-text {
  display: inline-block;
  writing-mode: vertical-rl;
  text-orientation: upright;
  line-height: 1;
  /* 两字及以上标签在竖排下适度下移，避免过贴边界 */
  margin-top: 0; /* 物理属性兜底 */
  margin-block-start: 0; /* 逻辑属性兜底 */
}


.label-col-element .col-text[data-len="2"] {
  margin-top: -1em;
}

.label-col-element .col-text[data-len="3"] {
  margin-top: -0.2em;
  margin-block-start: 0.2em;
}

@supports not (writing-mode: vertical-rl) {
  .label-col-element .col-text {
    transform: rotate(90deg);
    transform-origin: center;
    display: inline-block;
  }
}
</style>
