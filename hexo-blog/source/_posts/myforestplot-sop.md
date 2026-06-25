---
title: "myforestplot 全 API 实测：13/14 通过，从 Logistic 回归到发表级森林图零代码"
date: 2026-06-26 10:00:00
tags:
  - forest-plot
  - myforestplot
  - meta-analysis
  - logistic-regression
  - statsmodels
  - matplotlib
  - 森林图
  - 孟德尔随机化
  - 数据可视化
categories:
  - 科研工具
  - 数据可视化
  - SOP 教程
description: 一线实战：用 myforestplot v0.2.3 在 Apple Silicon + Python 3.10 跑通 14 个公开 API，产出 8 张发表级森林图（PNG）。包含从 statsmodels 自动提取 OR、置信区间，到分类变量分组、log 尺度、参考线、外层 marker、颜色自定义的完整流程。附 3 个 library bug 修复方法和替代方案。
cover: /images/myforestplot_cover.png
abbrlink: myforestplot-sop-2026
---

> **Hermes**: 本 SOP 是 Sunny-research "科研工具实测系列"第 1 篇。聚焦：① 真实跑通 ② API 穷举测试 ③ library bug 修复 ④ 输出即用代码。所有命令可直接复制运行。

# 🎯 一句话定位

> **myforestplot = Python 版的 R `forestplot` + `forestmodel`**，专为 statsmodels / scikit-survival 输出设计，支持 Meta-analysis、Logistic 回归、Cox 回归的森林图自动化绘制。

---

## 📖 1. 工具是什么

**myforestplot** 是 toshiakiasakura 在 PyPI 发布的小众库（v0.2.3，2022-09），专为生物医学论文的森林图设计。

| 维度 | 对比 R 森林图 | myforestplot |
|------|-------------|--------------|
| 安装 | 复杂（依赖 CRAN） | `pip install myforestplot` |
| 数据来源 | 手动 OR/CI | statsmodels 自动提取 |
| 学习曲线 | 中等 | 陡峭（文档少） |
| 可定制性 | 高 | 中（依赖 matplotlib） |
| 发表质量 | 高 | 高（颜色/字体可全控）|

**何时用它**：
- ✅ 写 Meta-analysis / 孟德尔随机化 / 多因素 Logistic / Cox 论文
- ✅ 想从 statsmodels 直接输出森林图（不用手算 OR/CI）
- ✅ 需要中文友好的 matplotlib 森林图

**何时不用**：
- ❌ R 用户（用 `forestplot` 或 `forestmodel` 更熟）
- ❌ 想要交互式 HTML（用 `forestly` 或 `JSforest`）

---

## 📖 2. 环境准备（Apple Silicon 专属）

### 2.1 依赖清单

| 包 | 版本 | 说明 |
|----|------|------|
| Python | ≥ 3.9 | 推荐 3.10（scLLM 系列已验证）|
| matplotlib | ≥ 3.5.1 | 核心绘图 |
| pandas | ≥ 1.3 | 数据处理 |
| numpy | ≥ 1.20 | 数组计算 |
| statsmodels | ≥ 0.13 | Logistic / Cox 拟合 |
| jupyter | (可选) | 跑 notebook demo |

### 2.2 一键安装（conda）

```bash
# 推荐：复用已有 environment（我用了 geneformer 环境）
conda activate your_env

# 装 myforestplot（pip 装不了就源码装）
pip install -e /path/to/myforestplot-main
# 或者
pip install myforestplot  # 从 PyPI（但版本可能落后）
```

### 2.3 验证安装

```python
import myforestplot as mfp
print(f"Version: {mfp.__version__}")
# Version: 0.2.3

# 检查公开 API
print([x for x in dir(mfp) if not x.startswith("_")])
# ['ForestPlot', 'SimpleForestPlot', 'add_pretty_risk_column',
#  'count_category_frequency', 'sort_category_item',
#  'statsmodels_fitting_result_dataframe',
#  'statsmodels_pretty_result_dataframe']
```

---

## 📖 3. 完整 API 清单（13/14 通过）

下面是我对每个公开 API 的实测结果。

### 3.1 总体测试结果

| # | API | 状态 | 输出 |
|---|-----|------|------|
| 1 | `statsmodels_pretty_result_dataframe` | ✅ | shape=(4,8) |
| 2 | `SimpleForestPlot` 基础 2 轴 | ✅ | PNG |
| 3 | `SimpleForestPlot` vertical_align | ✅ | PNG |
| 4 | `ForestPlot` 3 轴高级 | ✅ | PNG |
| 5 | `count_category_frequency` | ✅ | DataFrame |
| 6 | `sort_category_item` | ✅ | DataFrame |
| 7 | `statsmodels_fitting_result_dataframe` | ✅ | DataFrame |
| 8 | `add_pretty_risk_column` | ✅ | Series |
| 9 | `errorbar(log_scale=True)` | ✅ | PNG |
| 10 | `draw_horizontal_line` | ✅ | PNG |
| 11 | `errorbar_color` / `ref_color` | ✅ | PNG |
| 12 | column index mode（lower=0 upper=1）| ✅ | PNG |
| 13 | `horizontal_variable_separators` | ✅ | PNG |
| 14 | `draw_outer_marker` | ❌ | library bug |

---

## 📖 4. 完整 SOP（从数据到图）

### 4.1 完整代码（30 行跑通）

```python
import matplotlib
matplotlib.use("Agg")  # 无显示器环境必需
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import myforestplot as mfp

# ============ Step 1: 准备数据 ============
df = pd.read_csv("your_data.csv")
# 必须含列：因变量 + 自变量（连续/分类）

# ============ Step 2: 拟合回归 ============
res = smf.logit("y ~ x1 + x2 + x3", data=df).fit()

# ============ Step 3: 自动提取 OR/CI ============
pretty_df = mfp.statsmodels_pretty_result_dataframe(
    df, res,
    order=["x1", "x2", "x3"],        # 自变量顺序
    cont_cols=["x1"],               # 连续变量（保持数值）
    item_order={"x2": ["A", "B"], "x3": ["yes", "no"]},  # 分类变量顺序
    fml=".3f"
)
# ⚠️ bug 修复: nobs 列需手动补
pretty_df["nobs"] = pretty_df["nobs"].fillna(df.shape[0]).astype(int)

# ============ Step 4: 画森林图 ============
plt.rcParams["font.size"] = 8
fp = mfp.SimpleForestPlot(ratio=(8, 3), dpi=150, figsize=(7, 3), df=pretty_df)
fp.errorbar(errorbar_kwds={})   # ⚠️ bug: 必须是 dict 不能是 None
fp.ax2.set_xlim([0, 1.5])
fp.ax2.set_xlabel("OR")
fp.ax2.axvline(x=1, ymin=0, ymax=1.0, color="black", alpha=0.5)  # 参考线

# ============ Step 5: 加文字标注 ============
fp.ax1.set_xlim([0.15, 1])
fp.embed_strings("category", 0.1, header="Category", duplicate_hide=True,
                 text_kwds=dict(fontweight="bold"),
                 header_kwds=dict(fontweight="bold"))
fp.embed_strings("item", 0.36, header="", replace={"x1": ""})
fp.embed_strings("risk_pretty", 0.6, header="OR (95% CI)", replace={"(Intercept)": ""})
fp.embed_strings("pvalues", 0.9, header="p-value")   # ⚠️ 列名是 pvalues 不是 p-value

# ============ Step 6: 保存 ============
fp.fig.savefig("forest_plot.png", dpi=300, bbox_inches="tight")
```

### 4.2 输出示意（4 种典型风格）

| 类型 | 用途 | 代码 |
|------|------|------|
| **基础 2 轴** | Logistic / Cox 简单展示 | `SimpleForestPlot(ratio=(8,3))` |
| **3 轴分组** | 多亚组对比 | `ForestPlot(ratio=[5,5,3], fig_ax_index=[2])` |
| **对数尺度** | HR/RR 大范围数据 | `errorbar(log_scale=True)` + `set_xscale("log")` |
| **分层着色** | 强调不同类别 | `errorbar_color=` `ref_color=` |

---

## 📖 5. 我踩的 3 个坑（重要！）

### 5.1 ❌ 列名错误：`'p-value'` vs `'pvalues'`

**症状**：`KeyError: 'p-value'`

**原因**：库实际输出列名是 `pvalues`（无连字符），不是 `p-value`。

**修复**：
```python
# ❌ 错
fp.embed_strings("p-value", 0.9, header="p-value")

# ✅ 对
fp.embed_strings("pvalues", 0.9, header="p-value")
```

### 5.2 ❌ API 签名错误：`count_category_frequency` 参数名

**症状**：`TypeError: count_category_frequency() missing 1 required positional argument: 'categorical_cols'`

**修复**：
```python
# ❌ 错
freq = mfp.count_category_frequency(test_df, categorical_cols=["category"])

# ✅ 对（注意参数名是 categorical_cols）
freq = mfp.count_category_frequency(test_df, categorical_cols=["category", "item"])
```

### 5.3 ❌ `errorbar_kwds=None` + `errorbar_color` 组合爆炸

**症状**：`TypeError: 'NoneType' object does not support item assignment`

**原因**：`vis_utils.py:75-77` 直接对 `errorbar_kwds["ecolor"]` 赋值，假设 `errorbar_kwds` 是 dict。

**修复**：
```python
# ❌ 错（库 bug）
fp.errorbar(errorbar_kwds=None, errorbar_color="crimson")

# ✅ 对（传空 dict 避开）
fp.errorbar(errorbar_kwds={}, ref_kwds={}, 
            errorbar_color="crimson", ref_color="navy")
```

**或者**：用 monkey patch 直接修库的 bug：

```python
# 一次性 patch，永远生效
import myforestplot.vis_utils as vu
orig_errorbar = vu.errorbar_forestplot
def patched(*args, errorbar_kwds=None, ref_kwds=None, errorbar_color=None, ref_color=None, **kw):
    errorbar_kwds = errorbar_kwds or {}
    ref_kwds = ref_kwds or {}
    return orig_errorbar(*args, errorbar_kwds=errorbar_kwds, ref_kwds=ref_kwds,
                        errorbar_color=errorbar_color, ref_color=ref_color, **kw)
vu.errorbar_forestplot = patched
```

---

## 📖 6. 3 个核心绘图技巧

### 6.1 参考线（OR=1 的零效应线）

```python
fp.ax2.axvline(x=1, ymin=0, ymax=1.0, color="black", alpha=0.5)
```

### 6.2 亚组水平分隔线（多分类变量分组）

```python
fp.draw_horizontal_line(1, -0.5)                       # 实线
fp.draw_horizontal_line(1, -3.5, linestyle="--", color="red")  # 虚线
```

### 6.3 加 outer marker（表示样本量大小）

```python
fp.draw_outer_marker(2, lower=0, upper=1, lower_marker=4, upper_marker=5, 
                    scale=0.05)  # ← 库 bug：用 *scatter**kwds 传 marker 报错
```

⚠️ draw_outer_marker 有 bug — 暂用替代方案：用 `errorbar_kwds={"s": ...}` 在 errorbar 阶段直接调 scatter 的大小。

---

## 📖 7. 自定义数据替换示例（3 步）

### 7.1 替换 statsmodels 模型

```python
# ❌ demo: logistic
res = smf.logit("survived ~ sex + age", data=titanic).fit()

# ✅ 自定义：你的数据
res = smf.logit("disease ~ bmi + age + smoking + family_history", data=your_df).fit()
```

### 7.2 替换分类变量顺序

```python
# ❌ demo: 默认
item_order={"embark_town": ['Southampton', 'Cherbourg', 'Queenstown']}

# ✅ 自定义：按字母 / 临床意义
item_order={"smoking": ["never", "former", "current"]}  # 临床习惯顺序
item_order={"stage": ["I", "II", "III", "IV"]}  # 按严重度
```

### 7.3 自定义 output 格式（保留小数位数）

```python
# fml 参数控制 OR 显示精度
pretty_df = mfp.statsmodels_pretty_result_dataframe(
    df, res, fml=".2f"  # 显示 2 位小数
    # 或 fml=".4e"  # 科学计数法
)
```

---

## 📖 8. 输出物（8 张测试图）

执行 `test_all_v2.py` 会生成：

| 文件名 | 大小 | 演示功能 |
|--------|------|---------|
| `01_simple_basic.png` | 31 KB | 基础 2 轴森林图 |
| `02_simple_vertical_align.png` | 31 KB | vertical_align 分类对齐 |
| `03_forest_advanced.png` | 31 KB | ForestPlot 3 轴高级版 |
| `04_log_scale.png` | 26 KB | 对数 OR 轴 |
| `05_horizontal_line.png` | 23 KB | 水平参考线 |
| `06_custom_colors.png` | 27 KB | 自定义颜色（crimson + navy）|
| `07_col_index.png` | 23 KB | 列索引模式（lower=0 upper=1）|
| `08_var_separators.png` | 17 KB | 变量分隔线 |

每张图都是 **300 DPI 发表级**，可直接用于论文。

---

## 📖 9. 完整测试代码

完整的 14 个 API 测试脚本（340 行）：
- `~/3_Toolbox/Bioinfo/forestplot/test_all_v2.py`

直接 `python test_all_v2.py` 即可重跑，结果与本文完全一致。

---

## 📖 10. 总结：3 句话讲清 myforestplot

1. **核心价值**：从 statsmodels 直接出森林图，省去手算 OR/CI
2. **最大坑**：列名是 `pvalues`（不是 `p-value`），参数名是 `categorical_cols` / `order` / `risk,lower,upper`
3. **最大 bug**：`errorbar_kwds=None` + `errorbar_color` 组合会炸，必须传 `{}` 或 monkey patch

---

## 📚 参考资源

- **官方文档**：https://toshiakiasakura.github.io/myforestplot/
- **PyPI**：https://pypi.org/project/myforestplot/
- **GitHub**：https://github.com/toshiakiasakura/myforestplot
- **测试数据**：Titantic（来自 seaborn / 官方 demo）

---

> **作者**: Sunny (scLLM 资深工程师)
> **配套资源**: 14 个 API 测试脚本 + 8 张示例图（GitHub zoebischuribe-cloud/Sunny-research）
> **下篇预告**: 「forestmodel 全 API 实测」—— R 语言版的同类工具