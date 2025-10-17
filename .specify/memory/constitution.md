# CStudy Project Constitution

## Core Principles

### I. Cross-Platform Compatibility (NON-NEGOTIABLE)
**All components must run on Windows, Linux, and macOS without modification**
- Platform detection must be automatic; no manual configuration required
- Path handling must use platform-agnostic methods (normalize separators, handle drive letters)
- Shell scripts must have cross-platform equivalents or runtime detection
- File encoding must be UTF-8 across all platforms to ensure Chinese character support
- Line endings must be handled consistently (normalize to LF internally, respect platform conventions on output)

### II. Modular Architecture
**System must be composed of independently testable, loosely coupled modules**
- **Exercise Management**: Standalone module for loading, organizing, and tracking exercises
- **Grading Engine**: Independent validation module that accepts code and test specs, returns results
- **AI Service**: Optional module with clear interface contracts, can be disabled without breaking core functionality
- **CLI Interface**: Thin orchestration layer that coordinates modules
- Each module must expose a well-defined contract (inputs, outputs, error codes)
- Modules must not share state except through explicit interfaces

### III. Test-First Development (NON-NEGOTIABLE)
**TDD mandatory for all grading logic and core functionality**
- Tests written FIRST → User/stakeholder approval → Tests fail (Red) → Implement (Green) → Refactor
- Grading engine must have test coverage for: compilation success/failure, test case parsing, output comparison, timeout handling, resource limits
- Exercise management must have tests for: directory traversal, metadata parsing, progress tracking
- AI service integration must have mocked tests to avoid external dependencies in CI/CD
- Red-Green-Refactor cycle strictly enforced

### IV. Standardized File Formats
**All data exchange uses documented, version-controlled formats**
- **Exercise Description**: Markdown format with standardized sections (Title, Description, Input, Output, Examples)
- **Test Cases**: Structured text format with INPUT/OUTPUT blocks separated by `---` delimiters
- **Grading Results**: JSON format with defined schema (compilation status, test results, timing, errors)
- **Metadata**: JSON format for exercise properties (name, difficulty, tags, order)
- **Configuration**: JSON or YAML for system settings (timeouts, paths, AI model config)
- Format changes require version bumps and backward compatibility plan

### V. Fail-Safe and Sandboxing
**User code must never compromise system stability or security**
- All compilation and execution occurs in isolated temporary directories
- Process timeouts enforced: 5 seconds per test case, 20 seconds per exercise total
- Resource limits applied: memory caps, no network access during grading
- Source files remain read-only during grading operations
- Temporary artifacts cleaned up after each grading session
- Graceful degradation: one failed exercise does not halt batch processing
- All errors logged with context for debugging

### VI. Observability and Debugging
**All operations must be traceable and debuggable**
- Structured logging required: timestamps, operation type, inputs, outputs, exit codes
- Log files organized by date and module: `Detection/logs/YYYYMMDD_HHMMSS_{module}_{exercise}.log`
- Grading results include detailed failure information: expected vs actual output, compiler errors with line numbers
- AI interactions logged: prompts sent, responses received, timing information
- Console output must be clear and actionable: tell users what failed and how to fix it
- UTF-8 encoding enforced in all log files and console output

## Cross-Platform Requirements

### Platform Detection and Adaptation
- Automatically detect OS at runtime (Windows, Linux, macOS)
- Use platform-appropriate commands:
  - **Compiler**: gcc (Linux/macOS/MinGW), cl (MSVC as fallback)
  - **Shell**: PowerShell (Windows), bash/sh (Linux/macOS)
  - **Editor**: Environment variable `EDITOR`, fallback to `notepad` (Windows), `nano` (Linux), `open -e` (macOS)
  - **Path separator**: Use language path libraries that handle platform differences automatically

### File System Conventions
- Support both forward slashes and backslashes in paths; normalize internally to platform standard
- Handle Windows drive letters (C:\, D:\) and Unix-style root (/)
- Temporary directories: Use OS temp location (`%TEMP%` on Windows, `/tmp` on Unix-like)
- Respect platform newline conventions: CRLF (Windows), LF (Unix-like); normalize to LF for processing

### Character Encoding
- **All files**: UTF-8 without BOM (Byte Order Mark)
- Console input/output: UTF-8 encoding explicitly set
- File reads/writes: UTF-8 encoding specified
- Error messages: Support Chinese and English; no garbled characters

### Dependency Management
- **Required**: C compiler (gcc or compatible), accessible via PATH
- **Optional**: ollama (for AI features), with installation detection and guidance
- **Runtime**: Shell interpreter (PowerShell 5.1+ on Windows, bash 4.0+ on Unix)
- Document minimum versions for all dependencies
- Provide installation scripts or guidance for each platform

## Development Workflow

### Directory Structure Standards
```
CStudy/
├─ Exercises/           # Exercise content (cross-platform)
├─ Detection/           # Grading engine and utilities
│  ├─ logs/            # Grading operation logs
│  └─ temp/            # Temporary compilation artifacts (auto-cleaned)
├─ AIserver/           # AI service module (optional)
│  └─ logs/            # AI operation logs
├─ scripts/            # Platform-specific entry points
│  ├─ cstudy.ps1      # Windows PowerShell entry
│  ├─ cstudy.sh       # Linux/macOS bash entry
│  └─ common/          # Shared logic modules
└─ tests/              # Test suites
   ├─ unit/           # Module unit tests
   ├─ integration/    # Cross-module integration tests
   └─ fixtures/       # Test data and sample exercises
```

### Testing Requirements
- **Unit Tests**: Test individual functions/modules in isolation
- **Integration Tests**: Test module interactions (exercise loading → grading → result display)
- **Platform Tests**: CI/CD must run tests on Windows, Linux, and macOS
- **Test Data**: Include sample exercises with known correct/incorrect solutions
- **Mocking**: AI service must be mockable for testing without external dependencies

### Code Review Gates
- All PRs must pass cross-platform CI checks (Windows, Linux, macOS runners)
- Minimum 80% test coverage maintained for core modules
- No hardcoded platform-specific paths or commands
- All new features must include tests before merge
- Documentation updated for user-facing changes

## Error Handling Standards

### Exit Codes (Consistent Across Platforms)
- `0`: Success (all operations completed successfully)
- `1`: General error (unspecified)
- `2`: Compilation error
- `3`: Test case failure
- `4`: Runtime error or timeout
- `5`: AI service error
- `100+`: Internal system errors (logged with full context)

### Error Message Requirements
- Clear, actionable messages telling users what went wrong and how to fix it
- Include context: file path, line number (for compiler errors), expected vs actual (for test failures)
- Avoid technical jargon in user-facing errors
- Log detailed technical information separately for debugging
- Support bilingual messages (Chinese/English) where appropriate

## Performance Standards

### Response Time Requirements
- Exercise listing: < 3 second for up to 100 exercises
- Single exercise grading: < 5 seconds total (including compilation and all test cases)
- UI refresh: Instantaneous (< 100ms) for screen redraws

### Resource Limits
- Compilation memory limit: 256MB per process
- Execution memory limit: 128MB per test case
- Temporary storage: Auto-cleanup ensures < 100MB accumulation
- Log retention: 30-day automatic rotation (configurable)

## Governance

### Constitution Authority
- This constitution supersedes all other coding practices and guidelines
- Violations must be justified in writing and approved by project maintainers
- All pull requests must verify compliance with these principles

### Amendment Process
1. Proposed changes documented in issue with rationale
2. Stakeholder review period (minimum 7 days)
3. Approval required from project maintainers
4. Migration plan required for breaking changes

### Quality Assurance
- Cross-platform CI/CD pipeline required (GitHub Actions or equivalent)
- User acceptance testing for major feature changes
- Performance benchmarks tracked across versions

### Documentation Requirements
- README must include installation instructions for Windows, Linux, macOS
- API documentation for all module interfaces
- Example exercises with solutions for testing
- Troubleshooting guide for common cross-platform issues

**Version**: 1.0.0 | **Ratified**: 2025-10-15 | **Last Amended**: 2025-10-15