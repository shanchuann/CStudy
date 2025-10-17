# Tasks: CStudy - Interactive C Programming Learning Platform

**Input**: Design documents from `/specs/001-cstudy-interactive-c/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 创建项目目录结构，包含 scripts/、Exercises/、Detection/、AIserver/、tests/，按实现计划分层（无依赖）
- [ ] T002 初始化 PowerShell/Bash 脚本项目，配置 UTF-8 编码和跨平台兼容（scripts/cstudy.ps1, scripts/cstudy.sh）
- [ ] T003 [P] 配置 GitHub Actions 跨平台 CI 测试（.github/workflows/ci.yml）

---

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T004 实现练习题自动检测与注册脚本（scripts/common/detect_exercises.ps1, scripts/common/detect_exercises.sh）
- [ ] T005 [P] 实现判题引擎基础模块（scripts/common/judge.ps1, scripts/common/judge.sh）
- [ ] T006 [P] 实现日志与错误处理基础模块（scripts/common/log.ps1, scripts/common/log.sh）
- [ ] T007 配置判题沙箱与资源限制（Detection/temp/, scripts/common/sandbox.ps1, scripts/common/sandbox.sh）
- [ ] T008 配置 exercises/ 目录下 description.md、Test.txt、metadata.json 文件格式校验脚本

---

## Phase 3: User Story 1 - 完成编程练习并获得即时反馈 (P1) 🎯 MVP

**Goal**: 学生可选择练习题，提交 C 代码，系统自动编译并判题，3 秒内反馈结果。
**Independent Test**: 创建简单练习题，用户提交代码，3 秒内显示编译与测试结果。

- [ ] T009 [P] [US1] 实现 exercises/ 目录的练习题列表与状态展示（scripts/common/list_exercises.ps1, .sh）
- [ ] T010 [US1] 实现单题编译与判题流程（scripts/common/judge.ps1, .sh）
- [ ] T011 [US1] 实现 CLI 主界面与命令（scripts/cstudy.ps1, .sh）
- [ ] T012 [US1] 实现编译/判题结果输出与错误提示（scripts/common/judge.ps1, .sh）
- [ ] T013 [US1] 实现进度统计与完成提示（scripts/common/list_exercises.ps1, .sh）

---

## Phase 4: User Story 2 - 批量验证所有练习 (P2)

**Goal**: 学生可一键批量检测所有练习，获得通过/失败/未完成统计。
**Independent Test**: 多练习题混合状态，批量检测后正确分类统计。

- [ ] T014 [P] [US2] 实现批量检测命令与流程（scripts/cstudy.ps1, .sh）
- [ ] T015 [US2] 实现批量检测结果统计与展示（scripts/common/list_exercises.ps1, .sh）
- [ ] T016 [US2] 支持超时终止与失败练习高亮（scripts/common/judge.ps1, .sh）
- [ ] T017 [US2] 支持点击/命令跳转到失败练习（scripts/cstudy.ps1, .sh）

---

## Phase 5: User Story 3 - AI 辅助编程 (P3)

**Goal**: 学生可请求 AI 分析当前代码，获得错误分析与修正建议。
**Independent Test**: 设置本地 AI，提交带典型错误的代码，30 秒内获得分析与建议。

- [ ] T018 [P] [US3] 实现 AI 辅助命令与参数收集（scripts/cstudy.ps1, .sh）
- [ ] T019 [US3] 实现与本地 ollama/AIserver 通信（AIserver/）
- [ ] T020 [US3] 实现 AI 响应解析与建议输出（scripts/common/ai_helper.ps1, .sh）
- [ ] T021 [US3] 支持自动应用 AI 建议并备份原代码（scripts/common/ai_helper.ps1, .sh）

---

## Phase 6: User Story 4 - AI 模型管理 (P4)

**Goal**: 用户可管理本地 AI 模型，支持列出、下载、切换、删除。
**Independent Test**: 执行模型管理命令，验证各操作成功并状态更新。

- [ ] T022 [P] [US4] 实现 AI 模型管理命令（scripts/cstudy.ps1, .sh）
- [ ] T023 [US4] 实现模型下载、切换、删除逻辑（AIserver/model/）
- [ ] T024 [US4] 实现依赖检测与安装引导（scripts/common/ai_helper.ps1, .sh）

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T025 [P] 完善文档与用例（specs/001-cstudy-interactive-c/quickstart.md, plan.md）
- [ ] T026 代码重构与性能优化（scripts/、common/）
- [ ] T027 [P] 增加单元/集成测试（tests/unit/, tests/integration/）
- [ ] T028 安全加固与沙箱验证（scripts/common/sandbox.ps1, .sh）
- [ ] T029 运行 quickstart.md 验证所有功能

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → Phase 3/4/5/6（用户故事可并行）→ Phase 7
- 各用户故事均可独立测试与交付，建议先完成 P1（MVP）

## Parallel Opportunities

- [P] 标记任务可并行（不同文件/无依赖）
- 用户故事可多团队成员并行开发
- 各阶段测试、文档、AI相关任务可并行

## Implementation Strategy

- 先完成 Phase 1/2 基础设施
- 以 User Story 1 为 MVP，独立测试后逐步扩展
- 后续每个用户故事均可独立增量交付
- 多人团队可按用户故事并行推进
