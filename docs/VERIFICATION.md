# v2 验证记录

日期：2026-09-05。对象：本交付包源码、使用同一套 Go 模板产生的离线 HTML、内嵌资源预览。

## 已执行并通过

| 检查 | 结果 |
| --- | --- |
| 维护用单元/HTML 检查 | 22 项：10 项内容检查，12 项双语 HTML 检查 |
| 本轮九项修订快照 | 11 项检查，涵盖录用状态、统一论文、logo、招生、语言、邮箱与移除/隐藏栏目 |
| 浏览器检查 | 56 项；报告位于包内 `screenshots/browser-checks.json` |
| 视口 | 英文与中文分别检查 320、360、390、540、768、850、1024、1440 像素宽，无页面横向溢出 |
| 双语预览 | 默认英文；单文件预览中可以切到中文并切回英文 |
| 筛选 | 关键词与年份、无年份已录用论文、大小写不敏感多词检索、无结果提示和清空；两种语言分别通过 |
| 资源 | 原始头像、软件所与北京大学 logo 在浏览器中加载；数据驱动的每条经历均有 logo |
| 无 JavaScript | 中英文文稿均可读，全部论文在 HTML 中，筛选控件不显示，参与项目的原生 details 可展开 |
| Honors | 默认完全不输出；临时启用后双语栏目和导航都正常，随后默认交付数据保持 false |
| 后续更新回归 | 6 个场景：Honors 启用、新增论文、录用论文补齐年份、子路径部署数据测试、缺失图片拒绝、重复 ID 拒绝 |
| 子路径检查 | 在临时副本上以 `/research/` 为 base URL 输出两种语言，并再次通过 22 项维护测试 |
| 作者顺序 | 生成文本逐条与同一 YAML 中的作者列表比对；不因删除身份分类而重新排列作者 |
| 隐私与删除 | 未打包原始简历 PDF；运行数据无手机号、年龄、政治面貌、专利和软著数据；输出无 Honors 或 Built with 脚标 |

第一次 v2 接收测试对旧版本运行时失败，随后完成对应修改并通过。
Honors 和后续出版年份等回归场景在临时源码副本中运行，没有将测试示例写入正式交付资料。

## 浏览器检查的具体方式

当前环境的 Chromium 策略禁止 HTTP/file URL 导航，连本地测试服务器也不能通过浏览器访问。
本轮未修改或绕过浏览器策略。通过 Playwright `set_content` 将本项目的自包含 HTML
载入内存检查样式、交互和响应式排版，图片/CSS/JS 均来自已生成的本地资产。
截图为上述浏览器实际渲染，不是设计图。

单文件预览查看器中的语言切换经过真实点击验证。
独立网页的语言链接、hreflang、canonical、两页路径和站内锚点完成静态检查；
**没有把这些检查声称为真实服务器上的完整导航验证。**

## 离线模板检查不等于 Hugo 集成构建

`render_preview.py` 解析项目 YAML/Markdown，调用 Go 标准库 `html/template` 执行项目中
未经另行改写的 `layouts/home.html`、`404.html` 和 partials。
辅助程序只实现本页面使用的函数与页面数据，不运行 HugoBlox 模块或 Hugo 的构建生命周期。

当前环境没有 Hugo 可执行程序；尝试访问固定版本的 GitHub 下载地址时 DNS 解析失败。
因此本轮**没有运行完整 Hugo/HugoBlox 构建，没有运行 GitHub Actions，没有部署 GitHub Pages**。
也没有逐项验证外部论文链接或以外部检索更新个人资料。

## 重复运行

在 `site/` 中：

```bash
python3 -m pip install -r requirements-test.txt
python3 scripts/render_preview.py --output ../preview --standalone ..
SITE_DIR=../preview python3 -m unittest discover -s tests -v
SITE_DIR=../preview python3 -m unittest discover -s tests -p audit_v2_content.py -v
python3 scripts/check_site.py ../preview
node --check site-static/js/researcher.js
python3 scripts/check_regressions.py
```

浏览器快照检查另外需要 Playwright 和 Chromium：

```bash
python3 scripts/check_browser.py --standalone .. --artifacts ../screenshots --viewer ../shihao-zhu-preview.html --browser /usr/bin/chromium
```

以上浏览器和 v2 审计脚本针对本轮资料快照。日常 CI 的维护测试不固定为 9 篇论文或 Honors 必须关闭。
发布前仍须在能够安装原主题依赖的环境中运行：

```bash
hugo --minify
python3 scripts/check_site.py public
python3 -m unittest discover -s tests -v
```

然后检查 PR 的真实 CI、Pages 部署工作流以及英文首页与 `/zh/` 的线上访问。
