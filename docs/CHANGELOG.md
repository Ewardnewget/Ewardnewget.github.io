# v2 — 2026-09-05

本轮以用户九项修订为范围，沿用已批准的页面视觉和 Hugo/HugoBlox 框架。

| 要求 | 实现位置 |
| --- | --- |
| Survey 已录用 | `data/publications.yaml`，统一论文列表 |
| 不区分一作与其他 | 移除 `lead`、`cofirst`、身份筛选和署名脚注 |
| 移除专利软著 | `records.html`、`records.yaml`、相关样式已清理 |
| 经历栏加 logo | `experience.html`、本地 `images/logos/` |
| Honors 保留但停用 | `data/settings.yaml` 的 `show_honors: false` |
| 简介合并 Research，新增招生 | 双语 `_index` 内容文件和 `recruitment.html` |
| 中英文独立、默认英文 | `languages.yaml`、`_index.zh.md`、`data/ui/`、语言链接 |
| 移除 Built with 脚标 | `layouts/home.html` 页脚 |
| 新邮箱 | `data/authors/me.yaml`，简介与招生的邮件入口 |

补充：提供可重复的离线 Go 模板渲染脚本、双语单文件预览、维护说明和本轮验证记录。
没有把本轮变化提交到 GitHub，没有修改远程 main，也没有声明真实 Hugo 或线上部署已经通过。
