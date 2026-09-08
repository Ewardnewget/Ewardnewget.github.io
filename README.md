# 祝世豪个人主页 · v2

基于原有 **Hugo / HugoBlox / GitHub Pages** 仓库的双语学术主页源码覆盖包。
英文是默认语言，中文单独成页。资料使用 Markdown 与 YAML 维护，不需要修改 HTML。

> 本轮交付已更新源码、离线预览和截图，**没有执行远程推送、合并或部署**。
> 离线模板与浏览器检查已完成；真实 Hugo/HugoBlox 集成构建、GitHub Actions 和线上路由仍须在发布前验证。

## 1. 这次修改

- Survey 论文 `On Models for Sound Dynamic Data Race Detection` 改为已录用，移入统一论文列表；未推断出版年份、卷期或 DOI。
- 不再区分一作、共同一作和其他论文；删除对应筛选、标记及数据字段。保留真实作者顺序与本人姓名加粗。
- 删除专利和软件著作权的页面、渲染代码与数据；Honors 数据、模板和样式保留，默认不输出。
- 经历栏增加软件所与北京大学 logo，取自提供的简历原始内嵌图片，不依赖外部图床。
- 研究方向并入简介，下方增加招生信息及邮件联系入口。
- 中英文页面、界面文案和导航分离；默认英文，不按浏览器语言自动跳转。
- 删除首页右下角 Built with Hugo / HugoBlox 字样，仅保留返回顶部入口。
- 新增并优先显示 `zhush_aT_ios.ac.cn`，实际邮件链接为 `zhush@ios.ac.cn`；原 Gmail 保留为备用邮箱。

## 2. 日常更新改哪里

| 内容 | 文件 |
| --- | --- |
| 英文简介、研究方向、英文招生文案 | `site-content/_index.md` |
| 中文简介、研究方向、中文招生文案 | `site-content/_index.zh.md` |
| 姓名、职务、机构、经历、邮箱与学术链接 | `data/authors/me.yaml` |
| 两种语言共用的论文列表 | `data/publications.yaml` |
| 主持资助与参与项目 | `data/funding.yaml` |
| Honors 是否显示 | `data/settings.yaml` |
| 保留的 Honors 内容 | `data/records.yaml` |
| 导航、按钮、筛选提示等界面文字 | `data/ui/en.yaml`、`data/ui/zh.yaml` |
| 个人照片 | `site-static/images/portrait.jpg` |
| 单位和学校 logo | `site-static/images/logos/iscas.png`、`pku.png` |
| 内容更新日期 | `data/authors/me.yaml` 的 `updated` |

共用事实只维护一次，例如论文作者顺序、资助金额、经历日期。资料中的 `*_zh` 字段用于中文显示，
无此后缀的对应字段用于英文显示。**论文题名和作者署名保留出版物原文，不把中文页的英文文献题名另行翻译。**

`public/`、`preview/` 和单文件 HTML 均是生成结果，不应作为正式更新入口。

## 3. 简介与招生信息

两个 `_index` 文件的正文就是简介，研究方向已经合并在正文中。
招生信息放在各自的 YAML front matter 中：

```yaml
recruitment: |
  招收**计算机专业实习生**，要求**基础知识扎实、动手能力强**，**每周工作4天以上**，**最少实习3个月**。

  实习期间表现优秀者可以提供**软件所保研或推免名额**。
```

修改中文时，同时检查英文版本是否需要同步。保留 `|` 和正文前的两个空格，
空行可分段，`**文字**` 可加粗。模板固定把招生信息放在简介之后，并自动使用主邮箱生成联系入口。

## 4. Honors 开关

当前文件 `data/settings.yaml`：

```yaml
show_honors: false
```

改为 `true` 后重新构建，**两种语言的 Honors 栏目和对应导航一起恢复**。
这是构建期的输出开关，不是用 CSS 隐藏：关闭时生成的 HTML 中没有 Honors 内容或失效导航。
保留的渲染模板为 `layouts/_partials/researcher/records.html`；不包含已移除的专利或软著代码。
论文条目自身的 APSEC 奖项标记不受此开关影响。

## 5. 论文维护

所有已发表或已录用论文都在 `data/publications.yaml` 的 `papers:` 下。
复制 `templates/publication.yaml.example` 中的相应示例；没有一作分类字段。
本人姓名统一使用 `Shihao Zhu`，作者列表必须按真实顺序填写。

已录用但出版年份还未确认的条目：

```yaml
- id: models-data-race
  title: On Models for Sound Dynamic Data Race Detection
  authors: [Shihao Zhu, Yan Cai, Jian Zhang]
  venue: ACM Survey
  status: accepted
  links: []
```

未知年份直接省略 `year`，不要填 `0`、`2026` 或猜测的年份。该条目与其余论文在同一个列表中，
标签显示 Accepted / 已录用；不会进入“在投”栏目。刊名暂沿用资料中的 `ACM Survey`。
确定正式出版信息后补充整数 `year` 和准确刊名，必要时将 `status` 改为 `published`。
已知年份按倒序显示，无年份的已录用条目放在列表前面。

增加真实链接时填入 `links`，例如 `label: PDF`、`url: /papers/真实文件名.pdf`；
对应公开文件放在 `site-static/papers/`。不确定的 DOI、PDF 或代码仓库不要填。
没有真实链接时只显示明确标注的 Scholar 检索入口。

筛选只保留关键词和年份；“年份未注明”对应未填 `year` 的条目。
新年份、条目数量、排序与筛选计数自动更新。

## 6. 邮箱和 logo

```yaml
email: zhush@ios.ac.cn
email_display: zhush_aT_ios.ac.cn
secondary_email: zshpeking@gmail.com
```

`email_display` 只控制显示形式；`email` 用于可点击的 `mailto:` 地址。
这种显示方式不意味着完整的反爬保护，真实地址仍在邮件链接中。

每条经历的 `logo` 指向 `site-static` 内的文件，例如 `images/logos/iscas.png`。
`object-fit: contain` 保留图形比例，不拉伸或裁切校徽。替换机构时同时更新机构名称、中文名称与图像。
原简历 PDF 不在交付源码中，也不自动成为可公开下载的简历。

## 7. 查看预览

包根目录的 **`shihao-zhu-preview.html`** 是单文件离线查看器：直接打开即可查看英文，
右上角可以切换中文，图片和样式都已内嵌。它为便于单文件查看而用 iframe 容纳两份独立文档，
**真实网站并不使用 iframe，也不把两种语言正文混在同一页面里**。

另外保留 `shihao-zhu-en.html` 和 `shihao-zhu-zh.html` 两份独立单文件页面。
把这两个文件放在同一文件夹后，其中的语言切换链接也能对应到另一份文件。
正式构建后的入口是 `/`（英文）与 `/zh/`（中文）。

可重复生成离线预览（仅需 Python、Go 和测试依赖）：

```bash
cd site
python3 -m pip install -r requirements-test.txt
python3 scripts/render_preview.py --output ../preview --standalone ..
SITE_DIR=../preview python3 -m unittest discover -s tests -v
python3 scripts/check_site.py ../preview
```

Windows PowerShell 中把环境变量一行改为：

```powershell
$env:SITE_DIR="../preview"
python -m unittest discover -s tests -v
```

离线渲染器使用本项目的同一套 Go 模板，但只提供模板所需的有限辅助函数，**不是 Hugo 替代品**，
也不能证明第三方主题模块和全部构建钩子已通过。

## 8. 应用到现有仓库

把交付包解压到仓库目录外，先保证本地仓库工作区干净。
包根目录的 `apply_to_repo.py` 默认只列出变化；`--apply` 才会创建新的本地分支并复制文件。
它不自动提交、推送、合并或部署，也不会移动 `main` 分支指针。

```bash
# 尚未克隆仓库时执行。
git clone https://github.com/Ewardnewget/Ewardnewget.github.io.git

# 在解压后的 shihao-homepage-v2 目录执行，先查看。
python3 apply_to_repo.py ../Ewardnewget.github.io

# 确认文件清单后，在 feat/homepage-v2 分支应用。
python3 apply_to_repo.py ../Ewardnewget.github.io --apply
```

脚本默认核对原始基线提交 `f5835dd533260d7311e7a189747eafde3ccfbb38`。
如果你已经把 v1 或其他修改合入了本地 `main`，脚本会停止，避免静默覆盖。
审阅本地差异后，可用 `--expected-base` 指定你已确认的完整 main 提交 SHA。
目标分支已存在时用 `--branch` 选择一个新的名称；不要强制覆盖已有分支。

## 9. 真实 Hugo 构建与发布

保持原仓库的 HugoBlox 模块版本，安装 **Hugo extended 0.161.1、Node.js 22、Go、pnpm 10.14.0**。
这些是源码当前固定/指定的版本，不代表建议升级到最新版本。
在已经应用源码的本地仓库中运行：

```bash
pnpm install --no-frozen-lockfile
hugo server --disableFastRender
```

同时检查英文首页和 `/zh/`，然后执行：

```bash
hugo --minify
python3 -m pip install -r requirements-test.txt
python3 scripts/check_site.py public
python3 -m unittest discover -s tests -v
```

确认结果后在新分支提交并推送，再创建面向 `main` 的 Pull Request。
现有 build / deploy 工作流保留，PR 验证不会替代对正式页面的人工检查。
首次发布还需确认 GitHub 仓库 Settings → Pages 的发布源为 GitHub Actions。
只有实际 Actions 成功并确认部署地址可访问，才能认定上线成功。

## 10. 检查范围与资料来源

- `docs/VERIFICATION.md`：本轮真实执行了哪些检查，哪些尚未执行。
- `docs/CONTENT_SOURCES.md`：附件资料、本轮用户更新、翻译和未补写的字段。
- `docs/CHANGELOG.md`：v2 修改清单。

日常 CI 运行 `test_content.py`、`test_site.py`，不固定论文数量或 Honors 开关值。
`audit_v2_content.py`、`check_browser.py` 与 `check_regressions.py` 是本轮交付快照检查，
后续资料自然变化时不要把其中的历史条数当成网站约束。
