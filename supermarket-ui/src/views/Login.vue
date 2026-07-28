<template>
  <!-- 开场序幕 -->
  <div class="intro-overlay" ref="introOverlay" v-if="introActive">
    <div class="intro-slide" ref="introSlide1">
      <p class="intro-text">顺应AI时代发展，零售行业也要进步</p>
    </div>
    <div class="intro-slide" ref="introSlide2">
      <p class="intro-text">让我为你介绍我的项目</p>
    </div>
  </div>

  <div class="landing-wrapper" ref="scrollContainer" @scroll="handleScroll">
    <div ref="customCursor" class="custom-cursor" v-show="!introActive">
      <div class="cursor-core"></div>
      <div class="cursor-ring"></div>
    </div>
    <canvas ref="particleCanvas" class="particle-canvas"></canvas>

    <header class="minimal-header" :class="{ 'scrolled': isScrolled }">
      <div class="brand-container">
        <span class="logo-text">LKQ<span class="logo-dot">.</span></span>
        <span class="sub-title">Smart Retail System</span>
      </div>
      <button class="header-login-btn" @click="showLogin = true">
        登录<span class="btn-slash"> · </span>Login
      </button>
    </header>

    <!-- ===== Hero ===== -->
    <section class="section hero-section" ref="heroSection" @mousemove="onHeroMouseMove" @mouseleave="onHeroMouseLeave">
      <div class="hero-content">
        <div class="hero-eyebrow" ref="heroEyebrow">
          <span class="eyebrow-line"></span>NEXT GEN RETAIL PLATFORM
        </div>
        <h1 class="hero-title" ref="heroTitle">
          <span class="title-line line-1">RETAIL</span>
          <span class="title-line line-2">INTELLIGENCE<span class="accent-dot">.</span></span>
        </h1>
        <p class="hero-subtitle" ref="heroSub">
          基于 Spring Cloud Alibaba 微服务架构 &times; YOLOv8 视觉大模型<br>
          打造覆盖多门店、多场景的连锁零售全栈数字化运营平台<br>
          <span class="sub-line">从 AI 收银到数据分析，从库存调拨到智能决策，一栈式解决</span>
        </p>
        <div class="hero-actions" ref="heroActions">
          <button class="hero-btn primary" @click="showLogin = true">
            <span>进入系统</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>

      <div class="scroll-hint" ref="scrollHint">
        <span class="hint-text">SCROLL</span>
        <div class="hint-line"><div class="hint-dot"></div></div>
      </div>
    </section>

    <!-- ===== AI 视觉收银 ===== -->
    <section class="section feature-section" ref="section2">
      <div class="section-bg-num">01</div>
      <div class="feature-layout">
        <div class="feature-title-col" ref="fInfo1">
          <h2 class="section-title">AI Vision<br>Checkout<span class="accent-dot">.</span></h2>
        </div>
        <div class="feature-media" ref="fMedia1">
          <div class="media-frame elevate">
            <div class="detect-visual">
              <div class="detect-scene">
                <div class="detect-grid"></div>
                <div class="detect-box d1"><span class="d-label">可乐 97%</span></div>
                <div class="detect-box d2"><span class="d-label">薯片 94%</span></div>
                <div class="detect-box d3"><span class="d-label">牛奶 99%</span></div>
                <div class="detect-box d4"><span class="d-label">面包 91%</span></div>
                <div class="detect-dot"></div>
              </div>
              <div class="detect-stats">
                <div class="d-stat"><span class="ds-val">0.03s</span><span class="ds-label">识别速度</span></div>
                <div class="d-stat"><span class="ds-val">99.7%</span><span class="ds-label">准确率</span></div>
                <div class="d-stat"><span class="ds-val">10K+</span><span class="ds-label">SKU 支持</span></div>
              </div>
            </div>
          </div>
        </div>
        <div class="feature-desc-col">
          <p class="section-desc">
            深度集成
            <span class="tech-link" data-url="https://github.com/ultralytics/ultralytics" data-desc="Ultralytics YOLOv8 — 实时目标检测">YOLOv8 目标检测</span>
            与
            <span class="tech-link" data-url="https://opencv.org/" data-desc="OpenCV — 开源计算机视觉库">OpenCV</span>
            图像处理引擎。摄像头实时捕捉商品画面，毫秒级精准识别，一键无感结算。
            内置交班盲盘对账机制，确保每笔交易与现金流水严丝合缝，彻底告别人工盘点误差。
          </p>
          <ul class="feature-list">
            <li ref="flItem1"><span class="li-dot"></span>YOLOv8 毫秒级商品检测与分类</li>
            <li ref="flItem2"><span class="li-dot"></span>无感结算 &amp; 自动计价，减少排队时间</li>
            <li ref="flItem3"><span class="li-dot"></span>收银员交接班盲盘对账，杜绝资金漏洞</li>
            <li ref="flItem4"><span class="li-dot"></span>异常交易实时预警与回溯追踪</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ===== 分布式库存 ===== -->
    <section class="section feature-section alt" ref="section3">
      <div class="section-bg-num right">02</div>
      <div class="feature-layout reverse">
        <div class="feature-title-col" ref="fInfo2">
          <h2 class="section-title">Global<br>Inventory<span class="accent-dot">.</span></h2>
        </div>
        <div class="feature-media" ref="fMedia2">
          <div class="media-frame elevate">
            <div class="network-visual">
              <svg class="network-svg" viewBox="0 0 320 240">
                <line v-for="(l, i) in networkLines" :key="'l'+i" :x1="l.x1" :y1="l.y1" :x2="l.x2" :y2="l.y2"
                  stroke="currentColor" stroke-width="0.5" opacity="0.15" :class="'net-line net-line-'+i" />
                <g v-for="(n, i) in networkNodes" :key="'n'+i" :class="'net-node net-node-'+i">
                  <circle :cx="n.x" :cy="n.y" r="3" fill="currentColor" opacity="0.4"/>
                  <circle :cx="n.x" :cy="n.y" r="16" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.08"/>
                  <text :x="n.x" :y="n.y+28" text-anchor="middle" font-size="9" fill="currentColor" opacity="0.4">{{ n.label }}</text>
                </g>
              </svg>
            </div>
          </div>
        </div>
        <div class="feature-desc-col">
          <p class="section-desc">
            基于
            <span class="tech-link" data-url="https://spring.io/projects/spring-cloud-alibaba" data-desc="Spring Cloud Alibaba — 微服务一站式解决方案">Spring Cloud Alibaba</span>
            云原生微服务架构，实现多门店物理数据隔离与业务逻辑统一。
            总部可一键下发强制补货任务，门店间支持双向借货审批流，FIFO 效期预警自动标记临期库存，让每一件商品都在最佳时间售出。
          </p>
          <ul class="feature-list">
            <li ref="flItem5"><span class="li-dot"></span>多门店独立库存数据物理隔离</li>
            <li ref="flItem6"><span class="li-dot"></span>总部强制补货下发与智能推荐</li>
            <li ref="flItem7"><span class="li-dot"></span>门店间双向借货审批流程</li>
            <li ref="flItem8"><span class="li-dot"></span>FIFO 效期预警，自动标记临期商品</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ===== 模块 + 页脚 ===== -->
    <section class="section modules-section" ref="section4">
      <div class="modules-header" ref="modHeader">
        <h2 class="section-title">Powerful<br>Modules<span class="accent-dot">.</span></h2>
        <p class="section-desc">六大核心业务模块，覆盖从收银到决策的零售全链路数字化管理，支持多角色权限分级，适配总部、门店、收银员三级组织架构</p>
      </div>

      <div class="modules-grid" ref="modGrid">
        <div class="mod-card" v-for="(m, i) in modules" :key="i" :ref="el => modRefs[i] = el">
          <div class="mod-icon-wrap"><div class="mod-icon" v-html="m.icon"></div></div>
          <h4 class="mod-name">{{ m.name }}</h4>
          <p class="mod-desc">{{ m.desc }}</p>
          <span class="mod-index">{{ String(i + 1).padStart(2, '0') }}</span>
        </div>
      </div>

      <footer class="site-footer">
        <div class="footer-inner">
          <span class="footer-brand">LKQ<span class="logo-dot">.</span></span>
          <div class="footer-meta">
            <span>Copyright &copy; 2026 LKQ. All rights reserved.</span>
            <span class="meta-divider">·</span>
            <span>Mainland China</span>
            <span class="meta-divider">·</span>
            <span>Spring Cloud · YOLOv8 · Vue 3 · ECharts</span>
          </div>
        </div>
      </footer>
    </section>

    <!-- ===== 登录 / 注册弹窗 (3D翻转) ===== -->
    <transition name="fade">
      <div v-if="showLogin" class="login-modal-overlay">
        <div class="login-modal-backdrop" @click="showLogin = false"></div>
        <div class="perspective-container">
          <div class="flipper" :class="{ 'is-flipped': isFlipped }">
            <!-- 正面：登录 -->
            <div class="side front">
              <button class="close-btn" @click="showLogin = false">✕</button>
              <div class="modal-header">
                <h2 class="modal-title">Log in.</h2>
                <p class="modal-subtitle">Welcome back to Supermarket OS</p>
              </div>
              <form class="login-form" @submit.prevent="login">
                <div class="apple-input-group" :class="{ 'has-value': username }">
                  <label class="apple-floating-label">Username / 用户名</label>
                  <input type="text" v-model="username" class="premium-input" required />
                </div>
                <div class="apple-input-group" :class="{ 'has-value': password }" style="margin-top: 24px;">
                  <label class="apple-floating-label">Password / 密码</label>
                  <input type="password" v-model="password" class="premium-input" required />
                </div>
                <button type="submit" class="submit-btn" :disabled="loading">
                  {{ loading ? 'VERIFYING...' : 'CONTINUE / 继续' }}
                </button>
                <div class="register-link">
                  <a href="#" @click.prevent="isFlipped = true">CREATE ACCOUNT / 注册账号 ↗</a>
                </div>
              </form>
            </div>
            <!-- 背面：注册 -->
            <div class="side back">
              <button class="close-btn" @click="showLogin = false">✕</button>
              <div class="modal-header" style="margin-bottom: 24px;">
                <h2 class="modal-title">Sign up.</h2>
                <p class="modal-subtitle">Create your cashier account</p>
              </div>
              <el-form class="login-form" :model="regForm" :rules="regRules" ref="regFormRef" @submit.prevent>
                <el-form-item prop="name">
                  <div class="apple-input-group" :class="{ 'has-value': regForm.name }">
                    <label class="apple-floating-label">Name / 姓名拼音 (如: lkq)</label>
                    <input type="text" v-model="regForm.name" class="premium-input" @input="generateUsername" required />
                  </div>
                </el-form-item>
                <el-form-item prop="storeId">
                  <div class="apple-input-group has-value">
                    <label class="apple-floating-label" style="top: 16px; font-size: 12px;">Store / 所在门店</label>
                    <el-select v-model="regForm.storeId" placeholder=" " @change="generateUsername" style="width: 100%;">
                      <el-option label="1号店 (总店)" value="1" />
                      <el-option label="2号店 (分店)" value="2" />
                      <el-option label="3号店 (分店)" value="3" />
                    </el-select>
                  </div>
                </el-form-item>
                <el-form-item prop="password">
                  <div class="apple-input-group" :class="{ 'has-value': regForm.password }">
                    <label class="apple-floating-label">Password / 密码</label>
                    <input type="password" v-model="regForm.password" class="premium-input" required />
                  </div>
                </el-form-item>
                <el-form-item prop="confirmPassword">
                  <div class="apple-input-group" :class="{ 'has-value': regForm.confirmPassword }">
                    <label class="apple-floating-label">Confirm / 确认密码</label>
                    <input type="password" v-model="regForm.confirmPassword" class="premium-input" required />
                  </div>
                </el-form-item>
                <div class="account-preview" v-if="regForm.username">
                  <div class="apple-alert">
                    <div class="alert-title">YOUR ACCOUNT / 您的账号: <strong>{{ regForm.username }}</strong></div>
                  </div>
                </div>
                <button type="button" class="submit-btn" :disabled="regLoading" @click="handleRegister" style="margin-top: 8px;">
                  {{ regLoading ? 'CREATING...' : 'CREATE ACCOUNT / 注册' }}
                </button>
                <div class="register-link">
                  <a href="#" @click.prevent="isFlipped = false">BACK TO LOGIN / 返回登录 ↗</a>
                </div>
              </el-form>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 回到首页按钮 -->
    <button class="back-top-btn" @click="scrollToTop" title="回到首页">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 15l-6-6-6 6"/></svg>
    </button>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from '@studio-freight/lenis'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()

const introOverlay = ref(null), introSlide1 = ref(null), introSlide2 = ref(null)
const introActive = ref(true)
const scrollContainer = ref(null)
const customCursor = ref(null), heroSection = ref(null)
const particleCanvas = ref(null)
const heroEyebrow = ref(null), heroTitle = ref(null), heroSub = ref(null), heroActions = ref(null), scrollHint = ref(null)
const section2 = ref(null), section3 = ref(null), section4 = ref(null)
const fMedia1 = ref(null), fInfo1 = ref(null), fMedia2 = ref(null), fInfo2 = ref(null)
const flItem1 = ref(null), flItem2 = ref(null), flItem3 = ref(null), flItem4 = ref(null)
const flItem5 = ref(null), flItem6 = ref(null), flItem7 = ref(null), flItem8 = ref(null)
const modHeader = ref(null), modGrid = ref(null), modRefs = ref([])

const username = ref(''), password = ref(''), loading = ref(false)
const showLogin = ref(false), isScrolled = ref(false), isFlipped = ref(false)

let scrollTriggers = [], lenis = null, ctx = null, animFrame = null
let cursorX = 0, cursorY = 0, mouseX = 0, mouseY = 0

const handleScroll = (e) => { isScrolled.value = e.target.scrollTop > 80 }

const modules = [
  { name: 'AI 视觉收银', desc: 'YOLOv8 毫秒级商品识别，一键无感结算', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><circle cx="12" cy="10" r="3"/><path d="M8 21h8"/></svg>' },
  { name: '库存管理', desc: '分布式库存 · FIFO 效期预警 · 实时盘点', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="6" width="18" height="15" rx="2"/><path d="M3 10h18"/><line x1="7" y1="3" x2="7" y2="6"/></svg>' },
  { name: '数据分析', desc: 'ECharts 可视引擎 · 多维度商业洞察', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="12" width="4" height="8" rx="1"/><rect x="10" y="8" width="4" height="12" rx="1"/><rect x="16" y="4" width="4" height="16" rx="1"/></svg>' },
  { name: '多门店调拨', desc: '总部补货下发 · 门店双向借货 · 审批流', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="6" r="3"/><circle cx="8" cy="18" r="3"/><circle cx="18" cy="12" r="3"/><line x1="10.5" y1="7.5" x2="15.5" y2="10.5"/><line x1="10.5" y1="16.5" x2="15.5" y2="13.5"/></svg>' },
]

const networkNodes = [
  { x: 160, y: 20, label: 'HQ' }, { x: 50, y: 120, label: 'Store 1' },
  { x: 160, y: 180, label: 'Store 2' }, { x: 270, y: 120, label: 'Store 3' },
]
const networkLines = [
  { x1: 160, y1: 24, x2: 54, y2: 116 }, { x1: 160, y1: 24, x2: 164, y2: 176 },
  { x1: 160, y1: 24, x2: 266, y2: 116 }, { x1: 54, y1: 124, x2: 156, y2: 176 },
  { x1: 266, y1: 124, x2: 164, y2: 176 }, { x1: 54, y1: 124, x2: 266, y2: 116 },
]

const scrollToSection = (index) => {
  const secs = [section2.value, section3.value, section4.value]
  if (secs[index]) secs[index].scrollIntoView({ behavior: 'smooth' })
}

// ================== Hero / Section 标题发光 ==================
const glowElements = () => {
  const list = []
  if (heroTitle.value) {
    heroTitle.value.querySelectorAll('.title-line').forEach(el => list.push(el))
  }
  document.querySelectorAll('.section-title').forEach(el => list.push(el))
  return list
}

const applyGlow = (mx, my) => {
  const R = 400

  glowElements().forEach(el => {
    const rect = el.getBoundingClientRect()
    const rx = mx - rect.left
    const ry = my - rect.top
    // 渐变覆盖整个文字区域：光标处亮，边缘保持可见暗色
    el.style.background = `radial-gradient(circle ${R}px at ${rx}px ${ry}px, rgba(225,240,255,0.95) 0%, rgba(200,225,245,0.8) 20%, rgba(160,200,225,0.55) 50%, rgba(140,185,210,0.4) 100%)`
    el.style.webkitBackgroundClip = 'text'
    el.style.webkitTextFillColor = 'transparent'
    el.style.backgroundClip = 'text'
    const dot = el.querySelector('.accent-dot')
    if (dot) { dot.style.background = `radial-gradient(circle ${R}px at ${rx}px ${ry}px, rgba(80,139,195,0.95) 0%, rgba(80,139,195,0.7) 30%, rgba(80,139,195,0.3) 100%)`; dot.style.webkitBackgroundClip = 'text'; dot.style.webkitTextFillColor = 'transparent'; dot.style.backgroundClip = 'text' }
  })

  // 描述文字和列表
  document.querySelectorAll('.hero-subtitle, .section-desc, .feature-list li').forEach(el => {
    const rect = el.getBoundingClientRect()
    const rx = mx - rect.left
    const ry = my - rect.top
    el.style.background = `radial-gradient(circle ${R}px at ${rx}px ${ry}px, rgba(210,230,245,0.9) 0%, rgba(180,205,225,0.65) 35%, rgba(140,185,210,0.35) 100%)`
    el.style.webkitBackgroundClip = 'text'
    el.style.webkitTextFillColor = 'transparent'
    el.style.backgroundClip = 'text'
  })
}

const resetGlow = () => {
  ;[...glowElements(), ...document.querySelectorAll('.hero-subtitle, .section-desc, .feature-list li')].forEach(el => {
    el.style.background = ''
    el.style.webkitBackgroundClip = ''
    el.style.webkitTextFillColor = ''
    el.style.backgroundClip = ''
    const dot = el.querySelector('.accent-dot')
    if (dot) { dot.style.background = ''; dot.style.webkitBackgroundClip = ''; dot.style.webkitTextFillColor = ''; dot.style.backgroundClip = '' }
  })
}

const onHeroMouseMove = (e) => { applyGlow(e.clientX, e.clientY) }
const onHeroMouseLeave = resetGlow

// ================== 技术链接 hover ==================
const onTechLinkEnter = (e) => {
  const el = e.currentTarget
  const desc = el.dataset.desc
  if (desc) {
    el.setAttribute('data-tip', desc)
    el.classList.add('expanded')
  }
}
const onTechLinkLeave = (e) => {
  e.currentTarget.classList.remove('expanded')
  e.currentTarget.removeAttribute('data-tip')
}
const onTechLinkClick = (e) => {
  const url = e.currentTarget.dataset.url
  if (url) window.open(url, '_blank')
}

const scrollToTop = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// ================== 海浪 Canvas ==================
const initWaves = () => {
  const c = particleCanvas.value; if (!c) return
  ctx = c.getContext('2d')
  let w, h
  const resize = () => { w = c.width = c.offsetWidth; h = c.height = c.offsetHeight }
  resize(); window.addEventListener('resize', resize)

  const layers = [
    { amp: 30, freq: 0.008, speed: 0.3, color: 'rgba(140,130,200,0.12)', height: 0.3, lineWidth: 1.5 },
    { amp: 20, freq: 0.012, speed: 0.5, color: 'rgba(120,105,180,0.08)', height: 0.25, lineWidth: 1 },
    { amp: 15, freq: 0.018, speed: 0.7, color: 'rgba(100,85,160,0.06)', height: 0.2, lineWidth: 0.8 },
  ]

  const animate = () => {
    ctx.clearRect(0, 0, w, h)
    const scroll = scrollContainer.value ? scrollContainer.value.scrollTop : 0

    layers.forEach(l => {
      ctx.beginPath()
      ctx.strokeStyle = l.color
      ctx.lineWidth = l.lineWidth
      const baseY = h * (1 - l.height)
      const phase = scroll * 0.001 * l.speed

      for (let x = 0; x <= w; x += 2) {
        const nx = x / w
        const y = baseY + Math.sin(x * l.freq + phase + nx * 2) * l.amp
               + Math.sin(x * l.freq * 2.5 - phase * 1.3) * l.amp * 0.4
        if (x === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }
      ctx.stroke()
    })
    animFrame = requestAnimationFrame(animate)
  }
  animate()
}

// ================== 自定义光标 (升级版) ==================
const initCursor = () => {
  if (window.innerWidth <= 768) return
  const el = customCursor.value; if (!el) return
  const ring = el.querySelector('.cursor-ring')
  let idleTimer = 0

  const onMove = (e) => { mouseX = e.clientX; mouseY = e.clientY; idleTimer = 0 }
  const onOver = (e) => {
    const t = e.target.closest('button, a, .mod-card, input, .el-select, .hero-btn')
    el.classList.toggle('hover', !!t)
  }

  const render = () => {
    const dx = mouseX - cursorX, dy = mouseY - cursorY
    const dist = Math.sqrt(dx * dx + dy * dy)

    // 移动时慢悠悠跟随，静止时缓缓靠近
    if (dist < 1.5) {
      cursorX = mouseX; cursorY = mouseY
    } else {
      cursorX += dx * 0.06
      cursorY += dy * 0.06
    }

    el.style.transform = `translate(${cursorX}px, ${cursorY}px) translate(-50%, -50%)`

    if (ring) {
      const lag = Math.min(dist, 40)
      ring.style.transform = `scale(${1 + lag * 0.008})`
      ring.style.opacity = 0.25 + Math.min(lag, 20) * 0.01
    }
    requestAnimationFrame(render)
  }

  window.addEventListener('mousemove', onMove); window.addEventListener('mouseover', onOver)
  // 全局标题发光
  window.addEventListener('mousemove', (e) => applyGlow(e.clientX, e.clientY))
  window.addEventListener('mouseleave', onHeroMouseLeave)
  cursorX = mouseX = window.innerWidth / 2; cursorY = mouseY = window.innerHeight / 2
  requestAnimationFrame(render)
}

// ================== GSAP 入场动画 ==================
const initIntro = () => {
  const tl = gsap.timeline({
    defaults: { ease: 'power4.out', force3D: true },
    onComplete: () => {
      introActive.value = false
      // 序幕结束，启动主页动画
      initWaves()
      initCursor()
      initReveals()
      if (window.innerWidth > 768 && scrollContainer.value) {
        lenis = new Lenis({
          wrapper: scrollContainer.value, content: scrollContainer.value,
          duration: 2.0, easing: t => (t === 1 ? 1 : 1 - Math.pow(1 - t, 4)),
          smoothWheel: true, smoothTouch: false, wheelMultiplier: 0.75, touchMultiplier: 2,
        })
        const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf) }
        requestAnimationFrame(raf)
      }
      // 技术链接事件绑定
      document.querySelectorAll('.tech-link').forEach(el => {
        el.addEventListener('mouseenter', onTechLinkEnter)
        el.addEventListener('mouseleave', onTechLinkLeave)
        el.addEventListener('click', onTechLinkClick)
      })
    }
  })
  tl.fromTo(introSlide1.value, { opacity: 0, y: 30, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 1.6 })
    .to(introSlide1.value, { opacity: 0, y: -20, scale: 1.02, duration: 1.0, ease: 'power3.in' }, '+=2.0')
    .fromTo(introSlide2.value, { opacity: 0, y: 30, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 1.6 }, '-=0.4')
    .to(introSlide2.value, { opacity: 0, y: -20, scale: 1.02, duration: 1.0, ease: 'power3.in' }, '+=2.0')
    .to(introOverlay.value, { opacity: 0, duration: 1.0, ease: 'power3.inOut' }, '-=0.4')
}

// ================== ScrollTrigger 揭示 ==================
const initReveals = () => {
  const sc = scrollContainer.value
  const mkST = (trigger, from, to, start = 'top 82%') => {
    const st = ScrollTrigger.create({
      trigger, start, scroller: sc, once: true,
      onEnter: () => gsap.fromTo(trigger, { opacity: 0, ...from }, { opacity: 1, ...to, duration: to.duration || 1.1, ease: 'power4.out' })
    })
    scrollTriggers.push(st)
  }

  mkST(fMedia1.value, { x: -60, scale: 0.94 }, { x: 0, scale: 1, duration: 1.4 })
  mkST(fInfo1.value, { y: 60 }, { y: 0, duration: 1.2 });
  [flItem1, flItem2, flItem3, flItem4].forEach((r, i) => {
    if (!r.value) return
    const st = ScrollTrigger.create({
      trigger: r.value, start: 'top 88%', scroller: sc, once: true,
      onEnter: () => gsap.fromTo(r.value, { x: -20, opacity: 0 }, { x: 0, opacity: 1, duration: 0.5, delay: i * 0.08, ease: 'power3.out' })
    }); scrollTriggers.push(st)
  })

  mkST(fMedia2.value, { x: 60, scale: 0.94 }, { x: 0, scale: 1, duration: 1.4 })
  mkST(fInfo2.value, { y: 60 }, { y: 0, duration: 1.2 });
  [flItem5, flItem6, flItem7, flItem8].forEach((r, i) => {
    if (!r.value) return
    const st = ScrollTrigger.create({
      trigger: r.value, start: 'top 88%', scroller: sc, once: true,
      onEnter: () => gsap.fromTo(r.value, { x: -20, opacity: 0 }, { x: 0, opacity: 1, duration: 0.5, delay: i * 0.08, ease: 'power3.out' })
    }); scrollTriggers.push(st)
  })

  mkST(modHeader.value, { y: 40 }, { y: 0 })
  if (modGrid.value && modRefs.value.length) {
    const st = ScrollTrigger.create({
      trigger: modGrid.value, start: 'top 85%', scroller: sc, once: true,
      onEnter: () => gsap.fromTo(modRefs.value, { y: 60, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.08, duration: 0.8, ease: 'power4.out' })
    }); scrollTriggers.push(st)
  }
}

// ================== 生命周期 ==================
onMounted(async () => {
  await nextTick()
  if (sessionStorage.getItem('intro-shown')) {
    introActive.value = false
    initWaves()
    initCursor()
    initReveals()
    if (window.innerWidth > 768 && scrollContainer.value) {
      lenis = new Lenis({
        wrapper: scrollContainer.value, content: scrollContainer.value,
        duration: 2.0, easing: t => (t === 1 ? 1 : 1 - Math.pow(1 - t, 4)),
        smoothWheel: true, smoothTouch: false, wheelMultiplier: 0.75, touchMultiplier: 2,
      })
      const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf) }
      requestAnimationFrame(raf)
    }
    return
  }
  sessionStorage.setItem('intro-shown', '1')
  initIntro()
})

onUnmounted(() => {
  scrollTriggers.forEach(st => st.kill()); scrollTriggers = []
  if (lenis) { lenis.destroy(); lenis = null }
  if (animFrame) cancelAnimationFrame(animFrame)
})

// ================== 登录逻辑 ==================
const login = async () => {
  if (!username.value || !password.value) { ElMessage.warning('请输入用户名和密码'); return }
  loading.value = true
  try {
    const p = new URLSearchParams(); p.append('username', username.value); p.append('password', password.value)
    const res = await request.post('/auth/login', p)
    if (res.data?.token) {
      localStorage.setItem('token', res.data.token); localStorage.setItem('role', res.data.role)
      localStorage.setItem('storeId', res.data.storeId || (username.value.includes('2') ? '2' : username.value.includes('3') ? '3' : '1'))
      localStorage.setItem('username', username.value)
      ElMessage.success('登录成功')
      const r = res.data.role
      router.push(r === 'HQ' ? '/product' : r === 'STORE' ? '/order' : r === 'CASHIER' ? '/pos' : '/product')
    } else ElMessage.error(res.data?.msg || '登录失败')
  } catch (e) { console.error(e) } finally { loading.value = false }
}

// ================== 注册逻辑 ==================
const regFormRef = ref(null); const regLoading = ref(false)
const regForm = reactive({ name: '', storeId: '', password: '', confirmPassword: '', username: '' })
const validatePass2 = (_r, v, cb) => { if (!v) cb(new Error('请再次输入密码')); else if (v !== regForm.password) cb(new Error('两次输入密码不一致!')); else cb() }
const regRules = reactive({
  name: [{ required: true, message: '请输入姓名全拼', trigger: 'blur' }, { pattern: /^[a-zA-Z]+$/, message: '只能输入英文字母', trigger: 'blur' }],
  storeId: [{ required: true, message: '请选择门店', trigger: 'change' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validatePass2, trigger: 'blur' }]
})
const generateUsername = () => {
  if (regForm.name && regForm.storeId) { const n = new Date(); regForm.username = `${regForm.name.toLowerCase()}${String(regForm.storeId).padStart(2, '0')}${n.getFullYear()}${String(n.getMonth() + 1).padStart(2, '0')}${String(n.getDate()).padStart(2, '0')}` }
  else regForm.username = ''
}
const handleRegister = async () => {
  if (!regFormRef.value) return
  await regFormRef.value.validate(async (valid) => {
    if (!valid) return
    regLoading.value = true
    try {
      const res = await request.post('/auth/register', { username: regForm.username, password: regForm.password, role: 'CASHIER', storeId: Number(regForm.storeId), realName: regForm.name })
      const d = res.data || res
      if (d.code === 0 || d.code === 200) { ElMessage.success(`注册成功！账号 ${regForm.username}`); username.value = regForm.username; password.value = regForm.password; setTimeout(() => { isFlipped.value = false }, 800) }
      else ElMessage.error(d.message || d.msg || '注册失败')
    } catch (e) { ElMessage.error(e.response?.data?.message || e.message || '注册失败') } finally { regLoading.value = false }
  })
}
</script>

<style scoped>
/* ================== 开场序幕 ================== */
.intro-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: #1E1D5D; display: flex; align-items: center; justify-content: center;
}
.intro-slide {
  position: absolute; display: flex; align-items: center; justify-content: center;
  opacity: 0; will-change: transform, opacity;
  backface-visibility: hidden;
}
.intro-text {
  font-size: clamp(20px, 3vw, 32px); font-weight: 300;
  color: rgba(150,185,215,0.5); letter-spacing: 4px; text-align: center;
  line-height: 1.6; padding: 0 24px; will-change: transform;
}

/* ================== 全局容器 ================== */
.landing-wrapper {
  height: 100vh; overflow-y: scroll; overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro SC", "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
  background: #1E1D5D; color: rgba(200,220,240,0.55); cursor: none;
}
.section {
  min-height: 100vh; width: 100%; position: relative;
  display: flex; flex-direction: column; overflow: hidden;
}

/* ================== 自定义光标 (柔和暖调) ================== */
.custom-cursor {
  position: fixed; top: 0; left: 0; z-index: 99999; pointer-events: none;
  width: 60px; height: 60px; will-change: transform;
}
.cursor-core { display: none; }
.cursor-ring {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 100%; height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(80,139,195,0.12) 0%, rgba(60,120,180,0.04) 40%, transparent 70%);
  border: 1px solid rgba(80,139,195,0.1);
  transition: border-color 0.5s ease, background 0.5s ease;
}
.custom-cursor.hover .cursor-ring {
  border-color: rgba(110,160,205,0.3);
  background: radial-gradient(circle, rgba(80,139,195,0.18) 0%, rgba(60,120,180,0.06) 40%, transparent 70%);
}

/* ================== 粒子 Canvas ================== */
.particle-canvas {
  position: fixed; top: 0; left: 0; width: 100%; height: 100vh;
  pointer-events: none; z-index: 2; opacity: 0.8;
}

/* ================== 导航栏 ================== */
.minimal-header {
  position: fixed; top: 0; left: 0; right: 0; height: 64px; z-index: 100;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 40px; transition: all 0.5s ease; background: transparent;
}
.minimal-header.scrolled {
  background: rgba(4, 11, 26, 0.9);
  backdrop-filter: saturate(180%) blur(24px);
  -webkit-backdrop-filter: saturate(180%) blur(24px);
  border-bottom: 1px solid rgba(80,139,195,0.06);
}
.brand-container { display: flex; align-items: baseline; gap: 10px; }
.logo-text { font-size: 18px; font-weight: 700; letter-spacing: -0.5px; color: rgba(180,200,225,0.8); }
.logo-dot { color: #5a9ecf; }
.sub-title { font-size: 10px; text-transform: uppercase; letter-spacing: 2.5px; color: rgba(160,190,215,0.25); font-weight: 500; }
.header-login-btn {
  display: flex; align-items: center; gap: 4px;
  background: rgba(80,139,195,0.06); color: rgba(170,195,220,0.6);
  border: 1px solid rgba(80,139,195,0.08); padding: 7px 20px; border-radius: 20px;
  font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.3s ease;
}
.header-login-btn:hover { background: rgba(80,139,195,0.12); color: rgba(190,210,235,0.9); border-color: rgba(80,139,195,0.2); }
.btn-slash { opacity: 0.25; margin: 0 2px; }

/* ================== Hero ================== */
.hero-section {
  justify-content: center; align-items: flex-start; text-align: left;
  background: #1E1D5D; padding-left: 8vw;
}
.hero-content { position: relative; z-index: 3; max-width: 1000px; padding: 0; }

.hero-eyebrow {
  display: flex; align-items: center; gap: 12px;
  font-size: 11px; font-weight: 600; letter-spacing: 3px;
  text-transform: uppercase; color: rgba(140,180,215,0.3); margin-bottom: 32px;
}
.eyebrow-line { width: 24px; height: 1px; background: rgba(140,180,215,0.15); }

.hero-title {
  margin-bottom: 36px; position: relative; z-index: 2; text-align: left;
}
.title-line {
  display: block;
  font-size: clamp(64px, 10vw, 120px);
  font-weight: 700; line-height: 0.92; letter-spacing: -5px;
  color: rgba(140,190,215,0.5);
  transition: color 0.4s ease, text-shadow 0.4s ease;
  will-change: color, text-shadow;
}
.accent-dot { color: rgba(80,139,195,0.3); transition: color 0.5s ease; }

.hero-subtitle { font-size: 18px; line-height: 1.8; color: rgba(140,185,215,0.35); margin-bottom: 52px; font-weight: 400; }
.sub-line { display: block; font-size: 15px; color: rgba(140,185,215,0.22); margin-top: 8px; }

.hero-actions { display: flex; gap: 16px; justify-content: center; }
.hero-btn {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 18px 44px; border-radius: 30px;
  font-size: 15px; font-weight: 600; cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); border: none;
}
.hero-btn.primary {
  background: rgba(80,139,195,0.08);
  color: rgba(170,200,225,0.65);
  border: 1px solid rgba(80,139,195,0.12);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
.hero-btn.primary:hover {
  background: rgba(80,139,195,0.15); color: rgba(200,220,240,0.9);
  border-color: rgba(80,139,195,0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(10,20,50,0.5);
}
.hero-btn svg { width: 18px; height: 18px; transition: transform 0.3s ease; color: rgba(150,185,215,0.4); }
.hero-btn:hover svg { transform: translateX(3px); color: rgba(180,210,235,0.8); }

.scroll-hint {
  position: absolute; bottom: 36px; z-index: 3;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.hint-text { font-size: 10px; letter-spacing: 3px; color: rgba(140,180,215,0.15); }
.hint-line {
  width: 1px; height: 48px; position: relative; overflow: hidden;
  background: rgba(80,139,195,0.06);
}
.hint-dot {
  position: absolute; top: 0; left: -1px; width: 3px; height: 3px;
  background: rgba(120,170,210,0.4); border-radius: 50%;
  animation: dotTravel 2.5s ease-in-out infinite;
}

/* 回到首页按钮 */
.back-top-btn {
  position: fixed; bottom: 32px; left: 32px; z-index: 90;
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(80,139,195,0.06);
  border: 1px solid rgba(80,139,195,0.12);
  color: rgba(150,195,225,0.4);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.35s ease;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.back-top-btn:hover {
  background: rgba(80,139,195,0.15);
  border-color: rgba(80,139,195,0.3);
  color: rgba(190,220,240,0.8);
  transform: translateY(-3px);
}
.back-top-btn svg { width: 18px; height: 18px; }

/* 调色盘 */
.color-palette {
  position: fixed; right: 28px; bottom: 28px; z-index: 200;
  display: flex; flex-direction: column; align-items: flex-end; gap: 8px;
}
.palette-toggle {
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.5); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.3s ease; backdrop-filter: blur(8px);
}
.palette-toggle:hover { background: rgba(255,255,255,0.15); color: #fff; }
.palette-toggle svg { width: 20px; height: 20px; }
.color-palette.open .palette-toggle { background: rgba(255,255,255,0.15); color: #fff; }

.palette-body {
  background: rgba(10,20,40,0.92); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px; padding: 16px 18px; display: flex; flex-direction: column; gap: 10px;
  backdrop-filter: blur(16px); min-width: 180px;
}
.palette-row {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
}
.palette-row label {
  font-size: 11px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px;
  font-weight: 600; min-width: 28px;
}
.palette-row input[type="color"] {
  width: 32px; height: 24px; border: 1px solid rgba(255,255,255,0.15);
  border-radius: 4px; background: transparent; cursor: pointer; padding: 0;
}
.palette-presets { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.palette-presets button {
  font-size: 10px; padding: 3px 10px; border-radius: 12px;
  background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.4);
  border: 1px solid rgba(255,255,255,0.08); cursor: pointer;
  transition: all 0.2s; white-space: nowrap;
}
.palette-presets button:hover { background: rgba(255,255,255,0.15); color: #fff; }
@keyframes dotTravel {
  0% { top: 0; opacity: 0; } 20% { opacity: 1; }
  80% { opacity: 1; } 100% { top: 100%; opacity: 0; }
}

/* ================== 背景编号 ================== */
.section-bg-num {
  position: absolute; top: 40px; left: 40px;
  font-size: 160px; font-weight: 800; color: rgba(80,150,200,0.02);
  letter-spacing: -8px; line-height: 1; pointer-events: none; z-index: 0;
}
.section-bg-num.right { left: auto; right: 40px; }

/* ================== 特性展示屏 — 统一暗调背景 ================== */
.feature-section {
  background: #1E1D5D; color: rgba(155,200,225,0.6); justify-content: center;
}
.feature-section.alt { background: #1E1D5D; }

.feature-layout {
  max-width: 1400px; margin: 0 auto;
  display: grid; grid-template-columns: 1fr 1fr 1fr; align-items: center;
  padding: 0 40px; gap: 40px; width: 100%; z-index: 1;
}
.feature-layout.reverse { direction: ltr; }
.feature-media { display: flex; justify-content: center; align-items: center; }
.feature-title-col { text-align: left; padding-left: 0; }
.feature-desc-col { text-align: left; padding-right: 20px; }

.media-frame {
  background: rgba(80,139,195,0.03); border: 1px solid rgba(80,139,195,0.06);
  border-radius: 20px; padding: 32px;
  transition: transform 0.4s ease, box-shadow 0.4s ease;
}
.media-frame.elevate:hover { transform: translateY(-4px); box-shadow: 0 20px 48px rgba(5,12,30,0.5); }

/* YOLO 检测可视化 */
.detect-visual { display: flex; flex-direction: column; gap: 24px; }
.detect-scene {
  position: relative; width: 100%; aspect-ratio: 4/3;
  background: rgba(10,20,40,0.4); border-radius: 12px; overflow: hidden;
}
.detect-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(80,139,195,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(80,139,195,0.03) 1px, transparent 1px);
  background-size: 20px 20px;
}
.detect-box {
  position: absolute; border: 1px solid; border-radius: 3px;
  animation: boxDrift 4s ease-in-out infinite;
}
.detect-box.d1 { top: 20%; left: 18%; width: 30%; height: 35%; border-color: rgba(0,255,100,0.5); animation-delay: 0s; }
.detect-box.d2 { top: 15%; left: 55%; width: 28%; height: 32%; border-color: rgba(255,180,0,0.5); animation-delay: -1s; }
.detect-box.d3 { top: 55%; left: 12%; width: 25%; height: 30%; border-color: rgba(0,180,255,0.5); animation-delay: -2s; }
.detect-box.d4 { top: 52%; left: 48%; width: 32%; height: 28%; border-color: rgba(255,80,120,0.5); animation-delay: -3s; }
@keyframes boxDrift { 0%, 100% { transform: translate(0,0); } 25% { transform: translate(2px,-2px); } 50% { transform: translate(-1px,1px); } 75% { transform: translate(1px,2px); } }

.d-label {
  position: absolute; top: -20px; left: -1px;
  font-size: 10px; font-weight: 600; color: inherit;
  background: inherit; -webkit-background-clip: unset;
  padding: 1px 5px; white-space: nowrap;
  letter-spacing: 0.5px;
}
.detect-dot {
  position: absolute; top: 50%; left: 50%; width: 4px; height: 4px;
  background: rgba(10,132,255,0.6); border-radius: 50%;
  box-shadow: 0 0 20px rgba(10,132,255,0.4);
  animation: dotPulse 2s ease-in-out infinite;
}
@keyframes dotPulse { 0%, 100% { transform: translate(-50%,-50%) scale(1); opacity: 0.6; } 50% { transform: translate(-50%,-50%) scale(2.5); opacity: 0.15; } }

.detect-stats { display: flex; justify-content: center; gap: 40px; }
.d-stat { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.ds-val { font-size: 26px; font-weight: 700; color: rgba(180,205,225,0.8); letter-spacing: -1px; }
.ds-label { font-size: 11px; color: rgba(140,180,215,0.2); text-transform: uppercase; letter-spacing: 1.5px; }

/* 网络视觉 */
.network-visual { display: flex; justify-content: center; }
.network-svg { width: 100%; max-width: 340px; color: rgba(255,255,255,0.7); }
.net-node { animation: nodePulse 3s ease-in-out infinite; }
.net-node-0 { animation-delay: 0s; } .net-node-1 { animation-delay: 0.6s; }
.net-node-2 { animation-delay: 1.2s; } .net-node-3 { animation-delay: 1.8s; }
@keyframes nodePulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
.net-line { animation: lineFade 2s ease-in-out infinite; }
.net-line-0 { animation-delay: 0s; } .net-line-1 { animation-delay: 0.3s; }
.net-line-2 { animation-delay: 0.6s; } .net-line-3 { animation-delay: 0.9s; }
.net-line-4 { animation-delay: 1.2s; } .net-line-5 { animation-delay: 1.5s; }
@keyframes lineFade { 0%, 100% { opacity: 0.08; } 50% { opacity: 0.3; } }

.section-title {
  font-size: clamp(52px, 8vw, 100px); font-weight: 700; line-height: 0.92;
  letter-spacing: -4px; color: rgba(255,255,255,0.08); margin: 0 0 28px;
  transition: color 0.5s ease, text-shadow 0.5s ease;
  will-change: color, text-shadow; text-align: left;
}
.section-title .accent-dot { color: rgba(10,132,255,0.1); transition: color 0.5s ease; }
.section-desc {
  font-size: 22px; line-height: 1.8; color: rgba(255,255,255,0.45); margin-bottom: 36px; max-width: 520px;
}
/* 技术链接 — hover 展开 */
.tech-link {
  color: rgba(106,175,218,0.45); cursor: pointer;
  position: relative; z-index: 1;
  transition: all 0.35s ease;
  border-bottom: 1px dashed rgba(106,175,218,0.15);
}
.tech-link:hover,
.tech-link.expanded {
  color: #6aafda; border-bottom-color: #6aafda;
  text-shadow: 0 0 12px rgba(100,170,225,0.2);
}
/* hover 时在下方显示描述气泡 */
.tech-link::after {
  content: attr(data-tip);
  position: absolute; bottom: calc(100% + 10px); left: 50%;
  transform: translateX(-50%) translateY(6px);
  background: rgba(8,20,40,0.96); color: rgba(160,200,225,0.7);
  font-size: 12px; font-weight: 400; letter-spacing: 0.5px;
  padding: 6px 14px; border-radius: 8px;
  white-space: nowrap; pointer-events: none;
  opacity: 0; transition: all 0.3s ease;
  border: 1px solid rgba(80,139,195,0.1);
}
.tech-link.expanded::after {
  opacity: 1; transform: translateX(-50%) translateY(0);
}
.feature-list { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 16px; }
.feature-list li {
  font-size: 18px; color: rgba(255,255,255,0.55); display: flex; align-items: center; gap: 14px;
}
.li-dot { width: 6px; height: 6px; background: #508BC3; border-radius: 50%; flex-shrink: 0; }

/* ================== 模块屏 ================== */
.modules-section { background: #1E1D5D; justify-content: center; align-items: center; padding: 80px 40px; }
.modules-header { text-align: center; margin-bottom: 64px; }
.modules-header .section-desc { max-width: 440px; margin: 0 auto; }

.modules-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; max-width: 1100px; width: 100%; }
.mod-card {
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
  border-radius: 18px; padding: 44px 28px 36px; position: relative;
  transition: all 0.45s cubic-bezier(0.16,1,0.3,1); cursor: pointer; overflow: hidden;
}
.mod-card::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(10,132,255,0.05), transparent 50%);
  opacity: 0; transition: opacity 0.45s ease;
}
.mod-card:hover { transform: translateY(-8px); box-shadow: 0 24px 56px rgba(0,0,0,0.4); border-color: rgba(255,255,255,0.1); }
.mod-card:hover::after { opacity: 1; }
.mod-card:hover .mod-index { color: #508BC3; }
.mod-icon-wrap { margin-bottom: 24px; }
.mod-icon { width: 40px; height: 40px; color: #508BC3; }
.mod-icon :deep(svg) { width: 100%; height: 100%; }
.mod-name { font-size: 18px; font-weight: 700; margin: 0 0 8px; color: rgba(180,205,225,0.55); }
.mod-desc { font-size: 14px; color: rgba(170,200,225,0.3); line-height: 1.5; margin: 0; }
.mod-index {
  position: absolute; top: 20px; right: 24px;
  font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.04);
  letter-spacing: 1px; transition: color 0.45s ease; font-family: "SF Mono", monospace;
}

/* ================== 页脚 ================== */
.site-footer { width: 100%; margin-top: 80px; padding-top: 28px; border-top: 1px solid rgba(255,255,255,0.05); }
.footer-inner {
  max-width: 1100px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;
  font-size: 13px; color: rgba(150,185,215,0.2);
}
.footer-brand { font-size: 15px; font-weight: 700; color: rgba(160,195,220,0.4); }
.footer-meta { display: flex; align-items: center; gap: 10px; color: rgba(150,185,215,0.2); }
.meta-divider { opacity: 0.2; }

/* ================== 弹窗 (3D翻转) ================== */
.login-modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  display: flex; align-items: center; justify-content: center;
}
.login-modal-backdrop {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.45); backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.perspective-container { perspective: 1500px; width: 100%; max-width: 420px; height: 620px; z-index: 1001; position: relative; }
.flipper { width: 100%; height: 100%; position: relative; transition: transform 0.8s cubic-bezier(0.2,0.8,0.2,1); transform-style: preserve-3d; }
.flipper.is-flipped { transform: rotateY(180deg); }
.side {
  position: absolute; inset: 0; backface-visibility: hidden;
  background: rgba(255,255,255,0.88); backdrop-filter: saturate(180%) blur(40px);
  -webkit-backdrop-filter: saturate(180%) blur(40px);
  border-radius: 24px; padding: 40px; box-shadow: 0 24px 48px rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.5); box-sizing: border-box;
  display: flex; flex-direction: column; justify-content: center;
}
.front { transform: rotateY(0deg); }
.back { transform: rotateY(180deg); }
.close-btn {
  position: absolute; top: 20px; right: 20px; background: rgba(0,0,0,0.05);
  border: none; width: 32px; height: 32px; border-radius: 50%;
  font-size: 14px; color: #86868b; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s; z-index: 20;
}
.close-btn:hover { background: rgba(0,0,0,0.1); color: #1d1d1f; }
.modal-header { text-align: center; margin-bottom: 40px; }
.modal-title { font-size: 28px; font-weight: 600; color: #1d1d1f; margin: 0 0 8px; letter-spacing: -0.5px; }
.modal-subtitle { font-size: 14px; color: #86868b; margin: 0; }

.apple-input-group {
  position: relative; width: 100%; height: 64px;
  background-color: rgba(255,255,255,0.7); backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(0,0,0,0.1);
  border-radius: 12px; transition: all 0.2s ease; box-sizing: border-box;
}
.apple-input-group:focus-within { border-color: #000; background-color: rgba(255,255,255,0.9); box-shadow: 0 0 0 4px rgba(0,0,0,0.1); }
.apple-floating-label {
  position: absolute; left: 20px; top: 50%; transform: translateY(-50%);
  color: #98989d; font-size: 16px; letter-spacing: 0.5px; pointer-events: none;
  transition: all 0.3s cubic-bezier(0.16,1,0.3,1); z-index: 10;
}
.apple-input-group:focus-within .apple-floating-label,
.apple-input-group.has-value .apple-floating-label {
  top: 20px; font-size: 11px; font-weight: 600; color: #000;
  text-transform: uppercase; letter-spacing: 1px;
}
.premium-input { width: 100%; height: 100%; background-color: transparent; border: none; padding: 24px 20px 0; font-size: 18px; font-weight: 500; color: #1d1d1f; box-sizing: border-box; outline: none; }

:deep(.el-form-item) { margin-bottom: 16px; }
:deep(.el-form-item__error) { padding-top: 4px; }
:deep(.el-select) { width: 100%; height: 100%; }
:deep(.el-select__wrapper) { background: transparent !important; box-shadow: none !important; border: none !important; padding: 18px 16px 0 !important; min-height: 100% !important; height: 100% !important; box-sizing: border-box !important; }
:deep(.el-select__placeholder), :deep(.el-select__selected-item) { font-size: 17px !important; color: #1d1d1f !important; }

.apple-alert { background: rgba(255,255,255,0.7); backdrop-filter: blur(10px); border: 1px solid rgba(0,0,0,0.1); border-radius: 12px; padding: 16px; margin-top: 16px; text-align: center; }
.alert-title { font-size: 14px; font-weight: 500; color: #1d1d1f; }

.submit-btn {
  width: 100%; height: 64px; margin-top: 32px; background: #000; color: white;
  border: none; border-radius: 12px; font-size: 14px; font-weight: 700;
  letter-spacing: 2px; text-transform: uppercase; cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
}
.submit-btn:hover:not(:disabled) { background: #333; transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
.submit-btn:disabled { background: #86868b; cursor: not-allowed; }

.register-link { text-align: center; margin-top: 24px; }
.register-link a { color: #000; text-decoration: none; font-size: 14px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; transition: opacity 0.3s; }
.register-link a:hover { opacity: 0.6; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-active .perspective-container { transition: transform 0.3s cubic-bezier(0.16,1,0.3,1); }
.fade-leave-active .perspective-container { transition: transform 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-enter-from .perspective-container { transform: translateY(20px) scale(0.95); }
.fade-leave-to .perspective-container { transform: translateY(20px) scale(0.95); }

/* ================== 移动端 ================== */
@media (max-width: 768px) {
  .minimal-header { padding: 0 20px; }
  .hero-title .title-line { font-size: 44px; letter-spacing: -1px; }
  .hero-subtitle { font-size: 15px; }
  .hero-actions { flex-direction: column; align-items: center; }
  .feature-layout { grid-template-columns: 1fr; gap: 32px; padding: 0 24px; }
  .section-title { font-size: 34px; }
  .section-desc { font-size: 15px; }
  .media-frame { padding: 24px; }
  .detect-stats { gap: 14px; }
  .ds-val { font-size: 20px; }
  .modules-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .mod-card { padding: 28px 18px; }
  .section-bg-num { font-size: 80px; top: 20px; left: 20px; }
  .section-bg-num.right { left: auto; right: 20px; }
  .footer-inner { flex-direction: column; gap: 8px; text-align: center; }
  .custom-cursor { display: none; }
  .particle-canvas { display: none; }
  .landing-wrapper { cursor: auto; }
  button, a, input, .mod-card { cursor: pointer !important; }
  .perspective-container { max-width: calc(100vw - 40px); height: 580px; }
  .side { padding: 32px 24px; }
}
</style>
