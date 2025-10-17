# Feature Specification: CStudy - Interactive C Programming Learning Platform

**Feature Branch**: `001-cstudy-interactive-c`  
**Created**: 2025年10月15日  
**Status**: Draft  
**Input**: User description: "CStudy - Interactive C Programming Learning Platform with Automated Grading and AI Assistance"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete Programming Exercise with Immediate Feedback (Priority: P1)

A student opens CStudy, views available C programming exercises organized by chapter, selects an exercise to work on, writes their solution in a C file, saves the file, and immediately receives automated feedback showing whether their code compiles and passes all test cases.

**Why this priority**: This is the core learning loop that delivers immediate value. Students can practice coding and receive instant validation without waiting for instructor review.

**Independent Test**: Can be fully tested by creating a simple exercise with test cases, having a user write a solution, saving the file, and verifying that compilation and test results appear within 3 seconds. Delivers immediate learning value even as a standalone feature.

**Acceptance Scenarios**:

1. **Given** a student has launched CStudy, **When** they view the main interface, **Then** they see a welcome message, progress indicator showing completed vs total exercises, and a list of available commands
2. **Given** a student executes the list command, **When** the system displays exercises, **Then** each exercise shows its name, completion status, and file path
3. **Given** a student selects an exercise, **When** the system opens the exercise file, **Then** the file contains the problem description as comments, a designated user editing area, and example test cases
4. **Given** a student has written code and saved the file, **When** the file save is detected, **Then** the system automatically compiles the code within 1 seconds
5. **Given** the code compiles successfully, **When** the system runs test cases, **Then** each test case executes with a maximum timeout of 5 seconds per case
6. **Given** all test cases pass, **When** results are displayed, **Then** the student sees success confirmation and is prompted whether to proceed to the next exercise
7. **Given** compilation fails or tests fail, **When** results are displayed, **Then** the student sees clear error messages showing expected vs actual output, with line numbers for compiler errors

---

### User Story 2 - Batch Verify All Exercises (Priority: P2)

A student wants to check their progress across all exercises without manually opening each one. They execute a check command that runs automated grading on all exercises and displays a summary showing which exercises pass, which fail, and which have not been attempted.

**Why this priority**: Allows students to assess overall progress and identify areas needing attention. Useful for review sessions or before seeking help from instructors.

**Independent Test**: Can be tested by preparing multiple exercises (some complete, some incomplete, some with errors), running the batch check command, and verifying the summary correctly categorizes each exercise. Delivers value for progress tracking independently of other features.

**Acceptance Scenarios**:

1. **Given** a student executes the check command, **When** the system processes exercises, **Then** it traverses all exercise directories organized by chapter in sequential order
2. **Given** the system is checking exercises, **When** processing each exercise, **Then** it compiles the code, runs all test cases, and records results without modifying source files
3. **Given** the check completes, **When** displaying results, **Then** the summary shows total exercises, number passed, number failed, number not attempted, and lists failed exercises with clickable file paths
4. **Given** a batch check is running, **When** an exercise takes longer than 10 seconds total, **Then** the system terminates that exercise with a timeout error and continues to the next exercise
5. **Given** the check summary is displayed, **When** a student clicks on a failed exercise path, **Then** the system opens that exercise file in the configured editor

---

### User Story 3 - Get AI-Powered Coding Assistance (Priority: P3)

A student is stuck on an exercise and requests AI help. The system collects the exercise description, the student's current code, and test cases, sends this context to a local AI model, and displays analysis of potential issues, suggested fixes, and explanations to help the student understand and correct their mistakes.

**Why this priority**: Provides personalized learning support when students are stuck, reducing frustration and enabling self-directed learning. Lower priority because basic learning can occur without AI (students can debug manually or seek human help).

**Independent Test**: Can be tested by setting up a local AI model, creating an exercise with a common error (e.g., off-by-one error), requesting help, and verifying that the AI response includes error analysis and suggested corrections within 30 seconds. Delivers learning support value independently.

**Acceptance Scenarios**:

1. **Given** a student is working on an exercise, **When** they execute the help command, **Then** the system checks if AI service is enabled
2. **Given** AI service is not enabled, **When** help is requested, **Then** the system prompts whether to enable AI and guides through model selection and download
3. **Given** AI service is enabled, **When** help is requested, **Then** the system collects the exercise description, current code, and test cases into a structured prompt
4. **Given** the AI prompt is prepared, **When** sent to the local model, **Then** the system receives a response within 30 seconds containing error analysis, suggested code, and explanation
5. **Given** AI response is received, **When** displayed to the student, **Then** analysis appears first, followed by suggested code in a copyable format, with an option to automatically apply the fix
6. **Given** the student chooses to apply AI suggestion, **When** confirmed, **Then** the system backs up the current file and writes the suggested code to the exercise file

---

### User Story 4 - Manage AI Models (Priority: P4)

A student or instructor wants to manage which AI model is used for coding assistance. They can view available models, download new models, switch between models, and remove unused models to free up disk space.

**Why this priority**: Enables customization of AI assistance based on hardware capabilities and preferences. Lower priority because a default model can serve most users initially.

**Independent Test**: Can be tested by executing AI management commands to list, download, switch, and remove models, verifying each operation completes successfully and updates system state appropriately.

**Acceptance Scenarios**:

1. **Given** a user executes the AI management command, **When** viewing options, **Then** they see commands to list, enable, disable, switch, and remove models
2. **Given** AI is being enabled for the first time, **When** the system checks dependencies, **Then** it verifies ollama is installed and provides installation instructions if missing
3. **Given** selecting a model, **When** multiple models are recommended, **Then** the system displays model names with size requirements and descriptions
4. **Given** downloading a model, **When** the download starts, **Then** progress is displayed and the model is stored in the designated directory
5. **Given** switching models, **When** a new model is selected, **Then** the system prompts whether to remove the old model and updates configuration to use the new model
6. **Given** listing models, **When** the command executes, **Then** all downloaded models are displayed with their status (active/inactive) and storage size

---

### Edge Cases

- What happens when a student's code contains an infinite loop? System must detect timeout (2 seconds per test case), terminate the process, and report timeout error
- What happens when compilation produces Chinese error messages that might display incorrectly? System must enforce UTF-8 encoding for all console and file operations
- What happens when a student saves an empty file or a file with only comments? System should compile and report compilation or test failures appropriately without crashing
- What happens when exercise directory structure is malformed (missing description.md or Test.txt)? System should detect missing required files and display clear error indicating which files are missing
- What happens when multiple students use the same exercise directory simultaneously? System uses temporary directories for compilation/execution to avoid conflicts; source files remain read-only during grading
- What happens when the local AI model is not responding? System should timeout after 30 seconds and inform the user that AI service is unavailable
- What happens when disk space is insufficient for model downloads? System should detect disk space before downloading and warn the user if space is insufficient
- What happens when a student tries to access exercises that don't exist? System should display a helpful message indicating no exercises were found and suggest checking the Exercises directory
- What happens when file system permissions prevent reading exercise files or writing temporary files? System should catch permission errors and display a message indicating the specific file or directory that cannot be accessed

## Requirements *(mandatory)*

### Functional Requirements

#### Exercise Management

- **FR-001**: System MUST organize exercises in a hierarchical directory structure with chapters containing multiple exercises
- **FR-002**: System MUST provide a list command that displays all available exercises with their names, status (completed/incomplete), and file paths
- **FR-003**: System MUST support exercise metadata including name, difficulty level, tags, and ordering within chapters
- **FR-004**: System MUST load exercise descriptions from standardized markdown files containing problem statements, input/output specifications, and examples
- **FR-005**: System MUST provide clickable file paths in terminal output for supported terminals (Windows Terminal, VS Code Terminal)

#### Automated Grading

- **FR-006**: System MUST automatically detect when an exercise file is saved and trigger grading within 3 seconds
- **FR-007**: System MUST compile C code using standard compilation flags (C11 standard with optimization and warnings enabled)
- **FR-008**: System MUST execute compiled programs with test input and capture standard output, standard error, and exit codes
- **FR-009**: System MUST compare program output against expected output using exact byte-for-byte matching (after normalizing line endings)
- **FR-010**: System MUST enforce a timeout limit of 2 seconds per test case and 10 seconds per exercise total
- **FR-011**: System MUST terminate processes that exceed timeout limits and report timeout errors
- **FR-012**: System MUST parse test cases from standardized test files with INPUT and OUTPUT sections separated by delimiters
- **FR-013**: System MUST support multiple test cases per exercise with detailed pass/fail reporting for each case
- **FR-014**: System MUST isolate grading operations in temporary directories to prevent modification of source files
- **FR-015**: System MUST clean up temporary compilation artifacts after grading completes
- **FR-016**: System MUST log all grading operations including timestamps, commands executed, output captured, and exit codes

#### Batch Verification

- **FR-017**: System MUST provide a check command that grades all exercises in the repository
- **FR-018**: System MUST traverse exercise directories in a predictable order (by chapter, then by metadata ordering)
- **FR-019**: System MUST display a summary after batch checking showing total exercises, passed count, failed count, and not-attempted count
- **FR-020**: System MUST list all failed exercises with clickable paths to allow quick navigation
- **FR-021**: System MUST continue processing remaining exercises even if one exercise fails or times out

#### User Interface

- **FR-022**: System MUST display a welcome banner when launched showing the application name and visual branding
- **FR-023**: System MUST display a progress indicator showing completed exercises versus total exercises
- **FR-024**: System MUST refresh the console display when switching between interface modes (clear and redraw)
- **FR-025**: System MUST support commands: check (batch verify), list (show exercises), AI (manage AI service), help me (get AI assistance), quit (exit)
- **FR-026**: System MUST open exercise files in an external editor (using environment variable EDITOR or default editor)
- **FR-027**: System MUST prompt users for confirmation before advancing to the next exercise after completing one
- **FR-028**: System MUST display compilation errors with source line numbers and error descriptions
- **FR-029**: System MUST display test case failures showing input provided, expected output, and actual output
- **FR-030**: System MUST encode all console output and file operations using UTF-8 to support Chinese characters

#### AI Assistance

- **FR-031**: System MUST provide a help command that requests AI-powered coding assistance for the current exercise
- **FR-032**: System MUST detect whether AI service is enabled before processing help requests
- **FR-033**: System MUST prompt users to enable AI service if not already enabled, guiding through model selection and download
- **FR-034**: System MUST collect exercise context (description, current code, test cases) into a structured prompt for AI
- **FR-035**: System MUST send AI prompts to a local AI model (using ollama for model management)
- **FR-036**: System MUST support multiple AI models including default and alternative options for different hardware capabilities
- **FR-037**: System MUST receive AI responses within 30 seconds or report timeout
- **FR-038**: System MUST parse AI responses to extract error analysis, suggested code fixes, and explanations
- **FR-039**: System MUST display AI analysis before showing suggested code
- **FR-040**: System MUST provide an option for users to automatically apply AI-suggested code changes
- **FR-041**: System MUST back up the current exercise file before applying AI suggestions
- **FR-042**: System MUST provide AI management commands to list available models, download models, switch active model, and remove models
- **FR-043**: System MUST verify that ollama is installed before attempting to use AI features
- **FR-044**: System MUST store AI configuration and active model information in a persistent state file
- **FR-045**: System MUST log all AI operations including prompts sent, responses received, and errors encountered

#### System Requirements

- **FR-046**: System MUST verify that required dependencies (C compiler) are available before executing grading operations
- **FR-047**: System MUST store logs in organized directories with timestamps in filenames for traceability
- **FR-048**: System MUST support Windows operating system as the primary platform
- **FR-049**: System MUST handle file paths correctly across different path separators and drive letters
- **FR-050**: System MUST implement resource limits for compilation and execution processes to prevent system overload

### Key Entities

- **Exercise**: Represents a single programming problem with description, starter code template, test cases, metadata (name, difficulty, tags, order), and completion status
- **Test Case**: Represents input data and expected output for validating an exercise solution, with execution time and pass/fail status
- **Grading Result**: Represents the outcome of automated grading including compilation status, test case results, overall pass/fail, error messages, and execution logs
- **AI Model**: Represents a local language model configuration including model name, storage location, size, status (active/inactive), and capabilities
- **User Session**: Represents an active CStudy session including current exercise being worked on, progress state, AI service status, and configuration preferences

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students can discover and begin working on an exercise within 30 seconds of launching the application
- **SC-002**: Students receive compilation and test results within 3 seconds of saving their code file
- **SC-003**: Students can complete batch verification of all exercises (assuming 20 exercises averaging 0.5 seconds each) within 15 seconds
- **SC-004**: 90% of students successfully complete their first exercise without external help beyond the automated feedback
- **SC-005**: Students receive AI-powered assistance with error analysis and suggested fixes within 30 seconds of requesting help
- **SC-006**: The system handles exercises with up to 10 test cases per exercise without performance degradation
- **SC-007**: Compilation errors display with sufficient detail that students can locate and fix syntax errors within 2 minutes on average
- **SC-008**: Test case failures show clear differences between expected and actual output enabling students to identify logic errors within 5 minutes on average
- **SC-009**: Students can switch between exercises, check progress, and manage AI settings without restarting the application
- **SC-010**: The system processes exercises with infinite loops or excessive resource usage without crashing or hanging, reporting appropriate timeout or resource limit errors
- **SC-011**: 95% of legitimate student solutions (correct algorithms with minor bugs) receive actionable feedback that leads to successful correction
- **SC-012**: Students can download and enable AI assistance within 5 minutes on systems with stable internet connections

### Assumptions

- Students have basic familiarity with command-line interfaces and can navigate directories
- Students have a C compiler (gcc or compatible) installed and accessible via system PATH
- Students use terminals that support UTF-8 encoding for proper display of Chinese characters
- Students have sufficient disk space for temporary compilation artifacts (approximately 10MB per exercise session)
- For AI features, students have stable internet access for initial model downloads
- For AI features, students have sufficient disk space for local model storage (5-20GB depending on model size)
- Exercise content (descriptions, test cases) is created by instructors or content developers following standardized formats
- Students work on exercises individually (not collaborative editing of the same files simultaneously)
- The system has permission to create temporary directories and execute compiled binaries
- Default timeout values (2 seconds per test case, 10 seconds per exercise) are sufficient for typical exercises on modern hardware
