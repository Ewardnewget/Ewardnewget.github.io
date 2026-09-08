# 资料来源与处理边界 · v2

## 原始资料

个人身份、头像、机构、研究方向、教育与工作经历、论文题名和作者顺序、既往参与项目、
保留但隐藏的荣誉，来自用户提供的中文简历及上一版交付源码。
资助信息同时采用用户最初消息中的三项主持项目和金额。
本轮未以外部搜索结果扩展或替换个人经历。

## 本轮明确更新

1. 用户确认 Survey 论文已录用。`On Models for Sound Dynamic Data Race Detection` 进入统一论文列表，
   `status: accepted`；不再显示在投。刊名沿用附件 `ACM Survey`，不擅自补写正式全称、年份、卷期或 DOI。
2. 按用户要求去掉作者身份分类及共同一作标记，但真实作者顺序不变，本人姓名仍加粗。
3. 专利与软件著作权的页面和对应数据移除；Honors 数据与模板保留但配置关闭。
4. 头像仍使用原图。软件所 logo 来自简历第1页内嵌图像（xref 14，透明蒙版 12）；
   北京大学校徽来自同页图像（xref 20，透明蒙版 18）。没有生成、重绘或替换机构标识。
5. 简介合并研究方向；招生信息按用户本轮提供的条件编写，中文保留每周工作4天以上、最少实习3个月及优秀者可提供软件所保研/推免名额的表述。
6. 英文和中文为独立显示文稿。中文论文页仍保留英文题名和原作者署名。
7. 新邮箱显示 `zhush_aT_ios.ac.cn`，邮件地址按 `_aT_` 还原为 `zhush@ios.ac.cn`；原 Gmail 保留。

用户本轮的录用状态覆盖旧附件的在投状态；这是用户直接提供的更新，不是外部检索验证的出版结论。

## 翻译与未知信息

英文简介、招生文案，以及项目和荣誉的英文显示名称，是基于中文资料的译文，
不表示已经核实官方英文全称。没有为在资料中缺失的项目编号、职务起止日、
论文出版年、DOI、引用次数或 h-index 填入推测值。

没有公开原简历 PDF、手机号、年龄、政治面貌。`email_display` 的混淆形式仅用于显示，
并不能防止读取 HTML 中的实际邮件地址。

## 技术依据

本轮查阅的外部资料仅用于 Hugo 多语言实现，不用于补充个人履历：

- Hugo multilingual content: https://gohugo.io/content-management/multilingual/
- Hugo language configuration: https://gohugo.io/configuration/languages/
- Hugo page translations: https://gohugo.io/methods/page/translations/

项目使用 `_index.md` 与 `_index.zh.md` 配对内容，以及 `.AllTranslations` 生成普通语言链接；
首页默认英文，中文在 `/zh/`。项目级 `layouts/home.html` 自行控制首页页脚，
未修改第三方模块源文件或原仓库授权文件。
