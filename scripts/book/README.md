# 书籍流水线（归档）

这里的脚本用于维护《C语言圣经》的 GitBook 仓库，**不是 CStudy 应用的一部分**。
它们运行时依赖本机上的其他目录，因此在仓库里保留：

| 外部路径 | 用途 |
| --- | --- |
| `D:\Markdown\C语言圣经.md` | 书稿主文件 |
| `D:\Markdown\C语言圣经-原稿备份.md` | 原稿备份，`rebuild_c_book.ps1` 的基准 |
| `D:\Code\C++code\TheGitbookLibrary\C语言圣经` | GitBook 仓库 |
| `/home/shanchuan/CStudy/run.log`（WSL） | `render_linux_terminal.py` 渲染终端截图用 |

| 文件 | 说明 |
| --- | --- |
| `rebuild_c_book.ps1` | 用 `book_fragments/*.md` 把补充章节插回书稿 |
| `sync_gitbook_book.ps1` | 把书稿同步到 GitBook 仓库 |
| `merge_gitbook_basics.ps1` | 合并 GitBook 中拆分的章节 |
| `humanize_book.ps1` | 书稿文字润色 |
| `upgrade_book_assets.ps1` | 图片资源整理 |
| `use_github_image_urls.ps1` | 图片链接改为 GitHub raw 地址 |
| `normalize_gitbook_image_names.ps1` | 统一图片文件名 |
| `render_linux_terminal.py` | 渲染 WSL 终端截图（需要 Pillow） |
| `book_fragments/` | `rebuild_c_book.ps1` 的插入片段 |

不再维护该书时，可以整体删除本目录（`git rm -r scripts/book`）。
