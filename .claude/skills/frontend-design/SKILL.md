---
name: 极简白底黑字前端设计
description: Vue3 + Element Plus 极简白底黑字渡边风格企业前端设计模式。包含首页 GSAP 入场动画 + 功能端表格/分页/弹窗布局两套体系，覆盖自定义光标、Lenis 平滑滚动、Element Plus 组件定制。当你需要设计企业后台页面、登录首页、Vue3 管理面板、或提到极简/白底黑字/渡边风格时使用此技能。
---

# 极简白底黑字渡边风格前端设计

基于连锁超市管理系统前端项目提炼的设计语言和组件封装。

## 核心设计原则

- **极致黑白** — 黑色文字 (#000, #111, #333) + 白色背景 (#fff)，无彩色渐变
- **网格布局** — 横向等分网格卡片，比纵向列表更精致
- **字体系统** — `"Helvetica Neue", helvetica, "Segoe UI", system-ui, sans-serif`
- **透明控件** — 输入框、按钮均为透明底色 + 黑色细边框，hover 反色
- **大写英文标注** — 每个中文标题旁配英文副标题，全部大写
- **SVG 图标** — 用内联 SVG 不用 Icon 组件，保持一致视觉风格

## CSS 变量体系

```css
:root {
  --w-bg: #ffffff;
  --w-text: #111111;
  --w-text-gray: #999999;
  --w-border: #e0e0e0;
  --w-hover-bg: #f5f5f5;
  --w-red: #ff3b30;
  --w-green: #34c759;
}
```

所有页面使用 `var(--w-*)` 引用，保证风格统一。

## 布局模板

```vue
<template>
  <div class="xxx-page page-container">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="display-title">
          <span class="cn-title">页面名</span>
          <span class="en-title">/ English.</span>
        </h2>
        <span class="sub-text">Subtitle / 副标题</span>
      </div>
      <div class="header-right">
        <!-- 筛选/操作按钮 -->
      </div>
    </div>

    <!-- 统计数字面板（可选） -->
    <div class="stat-overview">...</div>

    <!-- 内容表格 -->
    <div class="table-container">
      <el-table :data="pagedList" stripe style="width:100%">
        ...
      </el-table>
    </div>

    <!-- 分页组件 -->
    <div style="display:flex;justify-content:center;margin-top:24px">
      <el-pagination background layout="prev, pager, next"
        :total="list.length" :page-size="20"
        @current-change="(v) => currentPage = v" />
    </div>
  </div>
</template>
```

## Element Plus 组件定制样式

### 按钮
```css
.minimal-btn {
  background: transparent;
  border: 1px solid var(--w-text);
  color: var(--w-text);
  padding: 6px 16px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}
.minimal-btn:hover { background: var(--w-text); color: var(--w-bg); }
```

### 下拉选择
```css
.minimal-select {
  appearance: none;
  background: transparent url("data:image/svg+xml,...") right 8px center/10px no-repeat;
  border: none;
  border-bottom: 1px solid var(--w-border);
  padding: 8px 24px 8px 0;
  font-size: 16px;
  font-weight: 600;
  outline: none;
}
```

### 表格
- 使用 `#000` 分割线，无背景色条（`stripe` 属性天然支持）
- ID 列固定宽度 `width="120"`，名称列 `min-width="200"`
- 金额列 `align="right"` + `font-family: monospace`
- 操作列 `fixed="right"` `align="right"`

## 页面入场动画

```css
.page-container {
  animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes fadeUp {
  0%   { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
```

**注意：App.vue 的 `<router-view>` 不要用 `<transition mode="out-in">`**，会卡住 Login→业务页的切换。

## 分页

所有列表页面统一 20 条/页，使用 Element Plus `<el-pagination>`：

```vue
<script setup>
import { ref, computed } from 'vue'

const list = ref([])
const currentPage = ref(1)
const pageSize = 20
const pagedList = computed(() =>
  list.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize)
)
</script>
```

## 标题格式

每个页面统一使用：

```html
<h2 class="display-title">
  <span class="cn-title">商品定价</span>
  <span class="en-title">/ Products.</span>
</h2>
<span class="sub-text">Management & Pricing / 管理与定价</span>
```

样式：
```css
.cn-title { font-size: 36px; letter-spacing: 2px; }
.en-title { font-size: 64px; letter-spacing: -2px; color: var(--w-text-gray); opacity: 0.3; }
.sub-text { font-size: 14px; color: var(--w-text-gray); text-transform: uppercase; letter-spacing: 2px; }
```

## 弹窗/对话框

使用 `el-dialog` + `append-to-body`，挂到 `<body>` 上避免被 Lenis 滚动容器影响：

```vue
<el-dialog v-model="visible" title="标题" width="400px"
  append-to-body top="5vh" custom-class="minimal-dialog">
  <!-- 内容 -->
</el-dialog>
```

## 自定义光标

```javascript
// App.vue onMounted
const cursor = document.querySelector('.custom-cursor')
window.addEventListener('mousemove', (e) => {
  gsap.to(cursor, { x: e.clientX, y: e.clientY, duration: 0.15, ease: 'power2.out' })
})
window.addEventListener('mouseover', (e) => {
  const target = e.target.closest('button, a, .menu-item')
  cursorState.value = target ? 'hover' : 'default'
})
```

## Lenis 平滑滚动

仅在非移动端、非登录页启用：

```javascript
const startLenis = () => {
  if (window.innerWidth <= 768) return
  if (route.path === '/' || route.path === '/register') return
  lenisInstance = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smooth: true,
  })
  const raf = (time) => { lenisInstance.raf(time); requestAnimationFrame(raf) }
  requestAnimationFrame(raf)
}
watch(() => route.path, startLenis)
```

## GSAP 动画最佳实践

- 所有 ScrollTrigger 用 `once: true`
- 退场动画控制在 0.6s 内
- 入场动画 `duration: 1.1-1.4s`, `ease: 'power4.out'`
- `onUnmounted` 中 `ScrollTrigger.getAll().forEach(st => st.kill())`

## 数据表格列设计

| 列类型 | 宽度 | 对齐 | 样式 |
|--------|------|------|------|
| ID/编号 | 120px | left | `font-family: monospace; color: #999` |
| 名称 | min-width: 200px | left | `font-weight: 500` |
| 金额/价格 | 150-220px | right | `font-family: monospace; font-size: 16px` |
| 状态标签 | 150px | center | `text-transform: uppercase; letter-spacing: 1px; font-size: 10px` |
| 操作按钮 | 160-220px | right | `fixed="right"` |

---

## 首页/登录页设计（GSAP 专场）

不同于管理页的静态布局，首页是全屏沉浸式滚动页面，包含：

### 结构层次

```
┌─────────────────────────────────┐
│  Opening Overlay (GSAP intro)    │  ← 品牌标语入场动画
├─────────────────────────────────┤
│  Hero Section                    │  ← 大标题 + 副标题 + CTA 按钮
├─────────────────────────────────┤
│  Feature Cards (3×N grid)        │  ← SVG 图标 + 标题 + 描述
├─────────────────────────────────┤
│  Tech Stack Links (横向滚动条)    │  ← hover 交互
├─────────────────────────────────┤
│  Footer                          │
└─────────────────────────────────┘
```

### 入场动画序列 (initIntro)

```javascript
const initIntro = () => {
  const tl = gsap.timeline({
    defaults: { ease: 'power4.out' },
    onComplete: () => {
      introActive.value = false
      initWaves()       // 背景波浪
      initCursor()      // 自定义光标
      initReveals()     // ScrollTrigger 揭示
      // Lenis 平滑滚动（仅桌面端）
      if (window.innerWidth > 768) {
        lenis = new Lenis({ duration: 2.0, smoothWheel: true })
        requestAnimationFrame((t) => { lenis.raf(t); raf() })
      }
    }
  })
  // 两段品牌标语依次淡入+淡出
  tl.fromTo('#slide1', { opacity:0, y:30, scale:0.97 },
            { opacity:1, y:0, scale:1, duration:1.6 })
    .to('#slide1', { opacity:0, y:-20, duration:1.0 }, '+=2.0')
    .fromTo('#slide2', { opacity:0, y:30, scale:0.97 },
            { opacity:1, y:0, scale:1, duration:1.6 }, '-=0.4')
    .to('#slide2', { opacity:0, y:-20, duration:1.0 }, '+=2.0')
    .to('#overlay', { opacity:0, duration:1.0 }, '-=0.4')
}
```

### 功能卡片

```html
<div class="feature-card" v-for="item in features" :key="item.name">
  <div class="card-icon" v-html="item.icon" />  <!-- 内联 SVG -->
  <h3>{{ item.name }}</h3>
  <p>{{ item.desc }}</p>
</div>
```

```css
.feature-card { padding: 40px; border: 1px solid var(--w-border); }
.feature-card svg { width: 32px; height: 32px; stroke: var(--w-text); }
```

### 技术链接条

```html
<div class="tech-strip">
  <a v-for="t in techList" :key="t" class="tech-link"
     @mouseenter="onTechLinkEnter" @mouseleave="onTechLinkLeave">
    {{ t }}
  </a>
</div>
```

### GSAP 退场清理

```javascript
onUnmounted(() => {
  ScrollTrigger.getAll().forEach(st => st.kill())
  if (lenis) { lenis.destroy(); lenis = null }
  cancelAnimationFrame(animFrame)
})
```

### 路由守卫（配合首页设计）

首页（`/`）和注册页（`/register`）不使用 Lenis 和自定义光标，避免与 GSAP 冲突。通过 `route.path` 判断。

---

## 技能使用指南

- **功能页面**（表格/表单/弹窗）：参考上方布局模板、分页、表格样式
- **首页/登录页**：参考 GSAP 入场动画、卡片网格、Lenis 平滑滚动
- **配色**：始终使用 CSS 变量，永远不要添加第三方颜色
- **字体**：标题英文用 `letter-spacing: -2px`（大字号衬线感），中文用 `letter-spacing: 2px`
- **不要用 `mode="out-in"` 的 `<transition>`**，会卡住路由切换
