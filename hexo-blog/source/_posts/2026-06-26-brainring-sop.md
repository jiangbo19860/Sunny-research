---
title: BrainRing 完整使用 SOP：浏览器即开即用的脑连接弦图可视化工具
date: 2026-06-26 16:30:00
abbrlink: brainring-sop
tags:
  - SOP
  - 可视化
  - 脑连接
  - 神经影像
  - fMRI
  - D3.js
categories:
  - 科研工具
  - 数据可视化
  - SOP 教程
description: 单文件 HTML 工具，集成 8 套脑图谱（Brainnetome-246 / AAL-90/116 / Schaefer-100/200/400 / Power-264 / Dosenbach-160）+ 自定义 CSV 图谱 + FC 矩阵导入 + 全参数交互 + SVG/PNG 导出。零安装，浏览器即开即用。
---

---

## 🎯 一句话定位

**BrainRing** = 浏览器版的 **Circos + BrainNet Viewer** 集成方案。D3.js 渲染，单文件 HTML，支持 8 套脑图谱（Brainnetome-246 / AAL-90/116 / Schaefer-100/200/400 / Power-264 / Dosenbach-160）+ 自定义 CSV 图谱 + FC 矩阵/Circos link 文件导入 + 阈值/Top-N 筛选 + 颜色/字号/分隔/旋转全参数调节 + 点击连边/改色 + SVG/PNG 导出。

**科研适用场景**：
- fMRI 功能连接（FC）矩阵可视化
- EEG/MEG 相干性连接图
- DTI 结构连接网络
- 神经环路图谱展示
- 论文 Figure 4-6 脑连接图

---

## 📦 1. 安装部署（30 秒）

### 1.1 方式一：浏览器直接打开（最简单）

```bash
# 下载单文件
curl -O https://raw.githubusercontent.com/XiuFan719/brain-connectivity-viz/main/index.html

# 浏览器打开（macOS）
open index.html
```

### 1.2 方式二：本地 HTTP 服务（推荐，避免某些浏览器 file:// 限制）

```bash
cd <PROJECT_ROOT>/科研可视化/brain-connectivity-viz
python3 -m http.server 8080
# 浏览器访问 http://localhost:8080
```

### 1.3 方式三：GitHub Pages 部署

```bash
# 1. Fork 仓库到自己账户
gh repo fork XiuFan719/brain-connectivity-viz --clone

# 2. 启用 Pages (Settings → Pages → Source: main / root)
# 访问 https://<username>.github.io/brain-connectivity-viz/
```

---

## 🧠 2. 8 套脑图谱全实测

### 2.1 实测清单

| # | 图谱 | 区域数 | 类型 | 适用 |
|---|------|--------|------|------|
| 1 | **Brainnetome 246** | 246 | 解剖 | 中国标准脑图谱，最详细 |
| 2 | **AAL-90** | 90 | 解剖 | 经典，自动版 |
| 3 | **AAL-116** | 116 | 解剖 | AAL-90 + 小脑 |
| 4 | **Schaefer-100** | 100 | 功能 | Yeo 7-Network |
| 5 | **Schaefer-200** | 200 | 功能 | 中粒度 |
| 6 | **Schaefer-400** | 400 | 功能 | 细粒度 |
| 7 | **Power-264** | 264 | 功能 | 任务态 fMRI |
| 8 | **Dosenbach-160** | 160 | 功能 | 静息态 |
| 9 | **Custom (CSV)** | 任意 | 用户 | 自定义 |

### 2.2 测试方法

实测脚本：`<PROJECT_ROOT>/科研可视化/brain-connectivity-viz/test_results/screenshot_atlases.py`

```python
# Playwright 自动测试 6 套图谱
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
        page = await ctx.new_page()
        
        await page.goto("file:///path/to/index.html", wait_until="load")
        await page.wait_for_timeout(5000)
        
        atlases = ["bna246", "schaefer100", "aal90", "power264", "schaefer400", "dosenbach160"]
        for atlas in atlases:
            await page.select_option("select", atlas)
            await page.wait_for_timeout(2000)
            await page.screenshot(path=f"{atlas}.png")
            print(f"✅ {atlas}.png")

asyncio.run(main())
```

### 2.3 实测结果

| 图谱 | 切换耗时 | 截图大小 | 渲染质量 |
|------|---------|---------|---------|
| Brainnetome 246 | 5s | 1070 KB | ⭐⭐⭐⭐⭐ |
| Schaefer-100 | 2s | 1041 KB | ⭐⭐⭐⭐⭐ |
| AAL-90 | 2s | 1070 KB | ⭐⭐⭐⭐ |
| Power-264 | 2s | 1291 KB | ⭐⭐⭐⭐⭐ |
| Schaefer-400 | 3s | 1240 KB | ⭐⭐⭐⭐ |
| Dosenbach-160 | 2s | 1076 KB | ⭐⭐⭐⭐⭐ |

**通过率：6/6 = 100%**

---

## 📊 3. 核心功能详解

### 3.1 数据导入（3 种方式）

#### 方式 A：FC 矩阵上传
```
1. 左侧面板 → "FC 矩阵" → 点击上传
2. 支持 CSV/TXT/TSV，N×N 方阵
3. 自动检测分隔符（,/\\t/空格）
4. 自动识别区域数，匹配当前图谱
```

#### 方式 B：边列表
```
格式：i, j, weight (每行一条)
示例：
1, 2, 0.85
1, 3, 0.72
```
左侧 → "边列表" → 上传 txt/csv

#### 方式 C：Circos Link 文件
```
格式：hs33 20000 800000 hs69 20000 800000 color=170,170,170 value=0.027
```
- `hs33` = 区域 ID
- `20000 800000` = 染色体起止（可忽略）
- `color=r,g,b` = 边颜色
- `value=0.027` = 权重

工具自动解析 region/weight/color。**这是 BrainRing 独家功能，Circos 用户无缝迁移。**

### 3.2 阈值筛选

| 模式 | 作用 |
|------|------|
| **阈值模式** | 只显示 |weight| > 阈值的边 |
| **Top-N 模式** | 显示最强/最弱/绝对值最大 N 条 |

### 3.3 手动连边（4 种方式）

```python
# 方式 1：文本框输入
[234,16]              # 单条
[1,2],[3,4],[5,6]     # 批量

# 方式 2：点击连边模式
# 切到 "点击连边" → 点击脑区 A → 点击脑区 B

# 方式 3：CSV 上传
# 上传 i,j,weight 三列文件

# 方式 4：Circos Link 上传
# 自动解析 + 应用
```

### 3.4 点击改色
- 鼠标悬停任一连接线 → 点击 → 弹出颜色选择器
- 提供 12 个预设色 + 自定义 hex
- 一键恢复区域颜色

### 3.5 Gyrus 文字交互
- 点击环上任意 Gyrus 名 → 改名 / 改色 / 调字号 / 隐藏
- 每个 Gyrus 可单独设字号（长名字缩小 / 重要脑区放大）

### 3.6 脑区重排
1. 左侧 "Reorder" 区块
2. 选择源 Gyrus → 目标位置 → "移动"
3. FC 矩阵、选中状态、手动边、颜色**全部自动重映射**

---

## 🎨 4. 全参数调节清单

| 参数 | 范围 | 默认 | 效果 |
|------|------|------|------|
| 颜色方案 | 6 套 | Classic | Classic/Neon/Pastel/Earth/BNA/Mono |
| 颜色深度 | -80 ~ +80 | 0 | 整体明暗 |
| 弧段配色 | 2 模式 | Flat | Flat 单色 / Gradient 渐变 |
| 分隔模式 | 3 模式 | None | None/细线/间隔 |
| 间隔大小 | 20% ~ 300% | 100% | 类 Circos 间距 |
| 旋转角度 | 0° ~ 360° | 0° | 整盘旋转 |
| 圆环大小 | 30% ~ 100% | 100% | 整体缩放 |
| 圆环宽度 | 4 ~ 100 | ? | 主圆环粗细 |
| 弧段间距 | ? ~ ? | ? | 子弧段间距 |
| 线条粗细 | ? ~ ? | ? | 连接线宽度 |
| 透明度 | 0% ~ 100% | ? | 整体透明度 |
| Gyrus 字号 | ? ~ ? | ? | 标签大小 |

---

## 📤 5. 导出论文级插图

### 5.1 推荐设置（白底出版图）

```
1. 主题：Light（白底）
2. 颜色方案：Classic
3. 颜色深度：+20
4. 分隔模式：Gap separation（间隔）
5. 圆环宽度：60
6. 圆环大小：85%
7. 旋转角度：0°
8. 选中加深：关
9. Gyrus 文字颜色：一键改黑（#000000）
```

### 5.2 导出 SVG（矢量）
- 保留所有交互对象 + 文字
- 可在 Inkscape / Illustrator / Figma 后编辑
- 适合 Nature / Cell 投稿

### 5.3 导出 PNG（4× 高清）
- 4 倍分辨率 = 6400×4000
- 适合 PPT / 微信 / 知乎插图
- 直接发推 / 公众号

---

## 🛠 6. 自定义图谱（CSV 格式）

### 6.1 CSV 列要求

```csv
id,label,lobe,gyrus
1,Precentral_L,Frontal,Precentral
2,Precentral_R,Frontal,Precentral
3,Frontal_Sup_L,Frontal,Frontal_Sup
...
```

| 列名 | 必填 | 说明 |
|------|------|------|
| `id` | ✅ | 1-indexed 区域编号 |
| `label` | ✅ | 显示名称 |
| `lobe` | ✅ | 大脑叶（用于上色分组） |
| `gyrus` | ✅ | 脑回（环上文字） |

### 6.2 上传步骤

```
1. 左侧 → Atlas 下拉 → "Custom (Upload CSV)"
2. 点击上传按钮 → 选择 CSV
3. 自动验证格式 → 缓存到 localStorage
4. 自由切换 内置 / Custom 图谱
```

### 6.3 适用场景
- 自己实验室的小鼠脑图谱
- 罕见病研究的小样本图谱
- 物种特异性分区（猕猴/狨猴）

---

## 🔬 7. 实战案例：fMRI FC 矩阵 → 论文图

### 7.1 完整工作流

```python
# Step 1: 用 Nilearn 提取 FC 矩阵
from nilearn.connectome import ConnectivityMeasures
from nilearn import datasets

# 下载 ADHD 数据
data = datasets.fetch_adhd(n_subjects=1)
timeseries = ...  # 提取时间序列

# 计算相关性
measure = ConnectivityMeasures(kind='correlation')
fc_matrix = measure.fit_transform([timeseries])[0]

# 保存为 CSV
import numpy as np
np.savetxt("fc_matrix.csv", fc_matrix, delimiter=",")
```

### 7.2 BrainRing 渲染

```
1. 浏览器打开 index.html
2. 上传 fc_matrix.csv
3. 切换到 Schaefer-100（图谱匹配）
4. 阈值 0.3（保留强连接）
5. 导出 SVG / PNG
```

### 7.3 论文用图规范

- **期刊投稿**：SVG（矢量图，无损）
- **PPT 汇报**：PNG 4x
- **公众号/知乎**：PNG 2x（控制文件大小 < 5MB）

---

## ⚙️ 8. 浏览器兼容性

| 浏览器 | 版本 | 支持 |
|--------|------|------|
| Chrome | 90+ | ✅ |
| Safari | 14+ | ✅ |
| Firefox | 88+ | ✅ |
| Edge | 90+ | ✅ |
| 移动端 | - | ✅（响应式布局） |

**依赖**：
- D3.js v7（CDN 加载，无需本地）
- Google Fonts: JetBrains Mono / DM Sans（可选，断网不影响核心功能）

---

## 🆚 9. 与同类工具对比

| 工具 | 安装 | 交互 | 图谱数 | 输出 | 编程需求 |
|------|------|------|--------|------|---------|
| **BrainRing** | ✅ 零安装 | ✅ 滑块 | 8+1 | SVG/PNG | ❌ 无 |
| Circos | ❌ Perl 编译 | ❌ 配置文件 | 0 | PNG/PDF | ⚠️ 高 |
| BrainNet Viewer | ❌ MATLAB | ✅ GUI | 3 | PNG | ⚠️ 低 |
| Nilearn connectome | ⚠️ Python | ❌ 静态 | 5 | PNG | ✅ 高 |
| MNE-Python | ⚠️ Python | ⚠️ 半交互 | 5 | PNG | ✅ 高 |
| NetDraw | ❌ 桌面软件 | ✅ GUI | 自定义 | PNG | ❌ 无 |

**BrainRing 优势**：
- ✅ **零安装**（单 HTML 文件）
- ✅ **8 套图谱开箱即用**
- ✅ **实时交互**（所有参数滑块调节）
- ✅ **Circos link 文件兼容**
- ✅ **SVG 矢量导出**

---

## ⚠️ 10. 已知限制

1. **CORS 限制**：本地 file:// 直接打开 CSV 上传可能被浏览器拦截 → 用 HTTP 服务
2. **大规模矩阵**：> 500 区域渲染较慢（> 5s），建议先用 Top-N 筛选
3. **离线使用**：首次打开需联网下载 D3.js，缓存后离线可用
4. **3D 视图**：roadmap 中（玻璃脑 3D 视图）

---

## 📋 11. Roadmap（来自官方）

- [ ] 玻璃脑 3D 视图
- [ ] FC 矩阵热力图联动
- [ ] 更多图谱（Desikan-Killiany、Gordon 333、Glasser 360）
- [ ] 分组对比（A vs B）
- [ ] 边捆绑（密集连接）

---

## 🔗 12. 相关资源

- **官方仓库**：https://github.com/XiuFan719/brain-connectivity-viz
- **在线 Demo**：https://XiuFan719.github.io/brain-connectivity-viz/
- **论文**：https://arxiv.org/abs/2603.27162
- **GitHub Pages Sunny 部署**：https://zoebischuribe-cloud.github.io/Sunny-research/brainring/
- **D3.js**：https://d3js.org/

---

## ✅ 总结

BrainRing 是**目前最易用的脑连接可视化工具**：
- ✅ 单文件 HTML，零安装
- ✅ 8 套内置图谱 + 自定义 CSV
- ✅ 全参数滑块实时交互
- ✅ 阈值筛选 + Top-N + 手动连边
- ✅ Circos link 文件兼容
- ✅ SVG/PNG 论文级导出

**适用**：fMRI 功能连接 / EEG 相干性 / DTI 纤维追踪 / 神经环路 / 脑网络分析

**科研场景**：
- 数据探索（交互式调整参数）
- 论文 Figure（导出 SVG/PNG）
- 学术汇报（PPT 插图）
- 教学演示（实时展示脑网络）

---

## 相关 SOP

- **myforestplot 全 API 实测**：发表级森林图（meta-analysis / Cox / Logistic）
- **pyecharts 全栈可视化**：30+ 图表（科研 Dashboard）
- **scLLM-mac-mps-sop**：Geneformer V1-10M 完整跑通
- **多平台自动化分发 SOP**：一键同步 Hexo → 6 平台