src/
tests/
backend/
api/
ios/ or android/
directories captured above]

# Implementation Plan: CStudy - Interactive C Programming Learning Platform

**Branch**: `001-cstudy-interactive-c` | **Date**: 2025-10-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-cstudy-interactive-c/spec.md`

**Note**: 本计划由 `/speckit.plan` 自动生成，遵循项目Constitution和功能规格说明。

## Summary

本项目采用脚本语言（PowerShell/Bash）实现，确保在 Windows、Linux、MacOS 平台均可运行。练习题采用后续动态添加方式，只要文件夹内容符合规范，脚本会自动检测并录入。核心功能包括练习管理、自动判题、AI辅助、批量验证等，所有操作均支持跨平台。

## Technical Context

**Language/Version**: PowerShell 5.1+（Windows），Bash 4.0+（Linux/macOS），所有脚本需兼容两者  
**Primary Dependencies**: gcc（C编译器，MinGW/WSL/系统自带），ollama（AI辅助，选装），标准shell工具（find、ls、cat、echo等）  
**Storage**: 文件系统（Exercises/、Detection/logs/、AIserver/model/等目录）  
**Testing**: 脚本自带单元测试（PowerShell/Bash），CI平台（GitHub Actions）自动运行跨平台测试  
**Target Platform**: Windows 10+，Linux（主流发行版），macOS 10.15+  
**Project Type**: 单体脚本项目，目录结构分明，支持后续扩展  
**Performance Goals**: 单题判题<5秒，批量判题100题<3分钟，AI响应<30秒  
**Constraints**: 需自动检测平台，所有路径/编码/换行符需兼容，判题过程需沙箱隔离，资源限制（内存/CPU/超时）  
**Scale/Scope**: 支持1000+练习题，单题10+测试用例，支持多用户本地使用

## Constitution Check

- ✅ 跨平台兼容性：所有脚本均需自动检测平台，适配命令/路径/编码
- ✅ 模块化架构：练习管理、判题引擎、AI服务、CLI界面均为独立模块
- ✅ 测试优先：所有核心功能需有单元/集成测试，CI自动验证
- ✅ 文件格式标准化：description.md、Test.txt、metadata.json等均有格式约定
- ✅ 沙箱与安全：判题过程隔离，资源限制，临时目录自动清理
- ✅ 可观测性：所有操作有结构化日志，错误信息清晰
- ✅ 渐进增强：AI辅助为可选模块，核心功能不依赖AI
- ✅ 目录结构与开发流程符合治理要求

无违宪项，所有GATE均通过。

## Project Structure

### Documentation (this feature)

```
specs/001-cstudy-interactive-c/
├── plan.md              # 实现计划
├── research.md          # 技术调研与决策
├── data-model.md        # 数据模型设计
├── quickstart.md        # 快速上手指南
├── contracts/           # API/接口约定
└── tasks.md             # 任务分解（后续生成）
```

### Source Code (repository root)

```
scripts/
├── cstudy.ps1           # Windows入口脚本
├── cstudy.sh            # Linux/macOS入口脚本
└── common/              # 共享逻辑模块（如判题、练习检测、AI接口）

Exercises/               # 练习题目录，支持动态添加
Detection/
├── logs/                # 判题日志
└── temp/                # 判题临时文件

AIserver/
├── model/               # AI模型存储
└── logs/                # AI操作日志


├── unit/                # 单元测试
├── integration/         # 集成测试
└── fixtures/            # 测试数据与示例练习
```

**Structure Decision**: 采用单体脚本项目结构，所有核心功能按模块分目录，练习题支持后续动态添加，脚本自动检测并录入。

## Complexity Tracking

无违宪项，无需复杂性说明。
# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)

## Delivery & Status

- 所有基础设施、判题、练习检测、AI辅助、模型管理、沙箱等脚本已实现
- 支持跨平台、自动化测试、AI扩展、练习动态管理
- 详见 tasks.md 与 quickstart.md
