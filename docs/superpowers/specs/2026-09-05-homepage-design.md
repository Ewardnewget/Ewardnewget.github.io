> 历史记录：以下为 v1 设计/计划，不代表当前显示内容。当前 v2 以用户本轮九项修改、README.md 和 docs/CHANGELOG.md 为准。

# Researcher homepage — approved design

Build an English-first academic homepage for Shihao Zhu / 祝世豪 on the existing
Ewardnewget/Ewardnewget.github.io HugoBlox repository. Preserve its pinned HugoBlox
modules and GitHub Pages build/deploy model; do not modify the remote main branch.
Use a project-local Hugo homepage layout, not a fork of the theme. Content lives in
Markdown and YAML, separate from CSS, templates and progressive-enhancement JS.

The page contains profile, research, conference publications (reverse chronological),
a separate under-review manuscript, PI funding, selected participating projects,
experience/education, selected honors and collapsible IP records. A real portrait
is extracted unchanged from the user-provided CV. No original CV is published.
No age, mobile number, political affiliation, invented grant dates, IDs, publication
metrics, acceptance upgrades, DOI links or inferred degrees are published.

Desktop: compact academic side navigation, white background, navy links, serif
headings, text-first publication list. Mobile: natural single column. Core content,
links and disclosures work without JavaScript. JS only enhances navigation/filtering.
Use local system fonts and assets; no analytics, cookies or third-party runtime fetches.

Single-source profile: data/authors/me.yaml. Biography: site-content/_index.md.
Papers: data/publications.yaml. Funding: data/funding.yaml. Honors/IP: data/records.yaml.
Use separate site-content and site-static roots to keep the existing starter examples
out of the generated site without deleting them from repository history.

Verification: source validation, real template rendering, asset/anchor checks,
mobile and desktop browser inspection, no-JS rendering. Full Hugo/module builds and
GitHub deployment must not be reported as tested unless actually executed.

Delivery constraint discovered: create_branch returned HTTP 403 Resource not
accessible by integration. Deliver an overlay package and guarded local application
script; no remote branch, PR or deployment can currently be claimed.
