# CLAUDE.md - Java Notebook (jvnb)
*Last updated 2025-09-17*

> **purpose** – This file is the onboarding manual for every AI assistant (Claude, Cursor, GPT, etc.) and every human who edits this repository.
> It encodes our coding standards, guard-rails, and workflow tricks for the Java Jupyter-style notebook project.

---

## 0. Project overview

Java Notebook (jvnb)는 Java 코드를 Jupyter 스타일의 노트북 환경에서 실행할 수 있도록 하는 Python 패키지입니다. 주요 기능:

### Core Features
- **듀얼 포맷 지원**: 마크다운(.md)과 Jupyter(.ipynb) 형식 모두 지원
- **FastAPI 웹 서버**: 현대적이고 빠른 FastAPI 기반 로컬 웹 서버
- **Java 코드 실행**: Python이 JDK를 오케스트레이션하여 Java 코드 컴파일 및 실행
- **향상된 UI/UX**: 각 형식에 최적화된 별도 인터페이스
- **자동 main 래핑**: main 메소드가 없는 간단한 코드를 자동으로 실행 가능한 클래스로 감싸기
- **완전한 출력 표시**: stdout과 stderr 모두 실행 결과에 표시
- **pip 설치 가능**: `pip install javanotebook` 명령으로 설치 가능한 Python 패키지

### Format-Specific Features

#### 마크다운(.md) 형식
- **서버사이드 렌더링**: Python markdown + Pygments로 서버에서 HTML 변환
- **동적 셀 추가**: 런타임에 새로운 Java 코드 셀을 추가/삭제 가능
- **커스텀 인터페이스**: 교육용에 최적화된 심플한 UI

#### Jupyter(.ipynb) 형식
- **표준 호환성**: nbformat 라이브러리 기반으로 완전한 Jupyter 호환성
- **클라이언트사이드 렌더링**: marked.js를 활용한 실시간 마크다운 렌더링
- **표준 Jupyter UI**: In[]/Out[] 프롬프트, execution_count 관리
- **키보드 단축키**: Shift+Enter, Ctrl+Enter 등 표준 Jupyter 단축키

**Golden rule**: When unsure about implementation details or requirements, ALWAYS consult the developer rather than making assumptions.

---

## 1. Non-negotiable golden rules

| #: | AI *may* do                                                            | AI *must NOT* do                                                                    |
|---|------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| G-0 | Whenever unsure about something that's related to the project, ask the developer for clarification before making changes.    |  ❌ Write changes or use tools when you are not sure about something project specific, or if you don't have context for a particular feature/decision. |
| G-1 | Generate code **only inside** relevant source directories (e.g., `src/` for main code, `examples/` for example notebooks)    | ❌ Touch `tests/`, or any test files (humans own tests & specs). |
| G-2 | Add/update **`# AIDEV-NOTE:` anchor comments** near non-trivial edited code. | ❌ Delete or mangle existing `AIDEV-` comments.                                     |
| G-3 | Follow lint/style configs (black, flake8, existing code style). Use project's configured testing framework (pytest). | ❌ Re-format code to any other style or introduce new testing frameworks.                |
| G-4 | For changes >300 LOC or >3 files, **ask for confirmation**.            | ❌ Refactor large modules without human guidance.                                     |
| G-5 | Stay within the current task context. Inform the dev if it'd be better to start afresh.                                  | ❌ Continue work from a prior prompt after "new task" – start a fresh session.      |

---

## 2. Build, test & utility commands

Use modern development tools with our configured setup:

```bash
# Installation and setup
make install                     # Install production dependencies
make install-dev                 # Install development dependencies + pre-commit
make check-java                  # Verify Java JDK installation

# Development server
make dev                         # Start server with basic_java.md example (markdown)
make example-algorithms          # Run algorithms example (markdown)
make example-data-structures     # Run data structures example (markdown)

# Format-specific execution
python -m javanotebook notebook.md      # Markdown format
python -m javanotebook notebook.ipynb   # Jupyter format
python -m javanotebook notebook.md --format md    # Explicit markdown
python -m javanotebook notebook.ipynb --format ipynb  # Explicit Jupyter
python -m javanotebook notebook.md --format auto  # Auto-detect format

# With custom options
python -m javanotebook notebook.ipynb --port 8080 --host 0.0.0.0

# Testing
make test                        # Run all tests
make test-unit                   # Unit tests only  
make test-integration            # Integration tests only
make coverage                    # Tests with coverage report

# Code quality
black src/                         # Format code with black
flake8 src/                       # Lint with flake8
mypy src/                         # Type checking with mypy
isort src/                        # Sort imports

# Development server (for debugging)
python src/javanotebook/server.py  # Start development server directly
```

---

## 3. Coding standards

*   **Python**: 3.8+, FastAPI for web server, `subprocess` for Java execution.
*   **Code Quality**: Enforced via black (formatting), flake8 (linting), mypy (type checking).
*   **Formatting**: Automated with black (88 char line length, double quotes, 4-space indentation).
*   **Typing**: Type hints preferred, especially for public interfaces.
*   **Naming**: `snake_case` (functions/variables), `PascalCase` (classes), `SCREAMING_SNAKE` (constants).
*   **Error Handling**: Use custom exceptions, proper subprocess error handling.
*   **Documentation**: Clear docstrings for public functions/classes.
*   **Testing**: pytest framework with coverage reporting.
*   **UI/UX**: Server-side markdown rendering, enhanced error formatting, keyboard shortcuts.

**Java execution patterns**:
- Use `subprocess.run()` with `capture_output=True` for Java compilation/execution
- Extract class name from Java code using regex patterns
- Auto-wrap simple code without main method using `wrap_code_with_main()`
- Handle compilation errors before attempting execution
- Display both stdout and stderr in execution results
- Clean up temporary files after execution

Example:
```python
import subprocess
import tempfile
import re
from pathlib import Path

def compile_and_run_java(java_code: str) -> dict:
    """Compile and run Java code, return results."""
    # AIDEV-NOTE: Extract class name from Java code
    class_match = re.search(r'public class\s+(\w+)', java_code)
    if not class_match:
        return {"error": "No public class found"}
    
    class_name = class_match.group(1)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        java_file = Path(temp_dir) / f"{class_name}.java"
        java_file.write_text(java_code)
        
        # Compile
        compile_result = subprocess.run(
            ["javac", str(java_file)], 
            capture_output=True, 
            text=True
        )
        
        if compile_result.returncode != 0:
            return {"error": compile_result.stderr}
        
        # Run
        run_result = subprocess.run(
            ["java", "-cp", temp_dir, class_name],
            capture_output=True,
            text=True
        )
        
        return {
            "stdout": run_result.stdout,
            "stderr": run_result.stderr,
            "returncode": run_result.returncode
        }
```

---

## 4. Project layout & Core Components

| Directory               | Description                                       |
| ----------------------- | ------------------------------------------------- |
| `src/javanotebook/`     | Main package source code                         |
| `├── __main__.py`       | Entry point for `python -m javanotebook`        |
| `├── main.py`           | FastAPI web application with dual format routing |
| `├── parser.py`         | Markdown notebook parser (legacy format)        |
| `├── nb_parser.py`      | **NEW**: Jupyter notebook parser (nbformat)     |
| `├── executor.py`       | Java code compilation and execution (markdown)  |
| `├── nb_executor.py`    | **NEW**: Jupyter-compatible Java executor       |
| `├── models.py`         | Pydantic models for markdown format             |
| `├── nb_models.py`      | **NEW**: Jupyter notebook models (nbformat)     |
| `├── format_detector.py`| **NEW**: File format detection (.md vs .ipynb) |
| `├── static/`           | CSS, JavaScript, images for web interface       |
| `│   ├── css/style.css` | Styles for markdown format                      |
| `│   ├── css/jupyter_notebook.css` | **NEW**: Jupyter-specific styles |
| `│   ├── js/notebook.js`| JavaScript for markdown format                  |
| `│   └── js/jupyter_notebook.js` | **NEW**: Jupyter-specific JavaScript |
| `├── templates/`        | HTML templates for web interface                |
| `│   ├── notebook.html` | Template for markdown format                    |
| `│   └── jupyter_notebook.html` | **NEW**: Template for Jupyter format |
| `├── routers/`          | FastAPI route handlers                          |
| `└── exceptions.py`     | Custom exception definitions                     |
| `examples/`             | Example notebook files (.md and .ipynb)         |
| `tests/`                | Test suite (unit, integration)                  |
| `docs/`                 | Documentation files                              |

**Key domain models**:

### Markdown Format (Legacy)
- **Notebook**: Collection of cells parsed from markdown file
- **Cell**: Base class for notebook cells (markdown or code)
- **MarkdownCell**: Cell containing server-rendered HTML content
- **JavaCodeCell**: Cell containing Java code for execution
- **ExecutionResult**: Result of Java code compilation and execution
- **ExecutionRequest**: Request model for code execution with validation

### Jupyter Format (New)
- **JupyterNotebook**: Standard Jupyter notebook with nbformat compliance
- **JupyterCell**: Base class for Jupyter cells (markdown, code, raw)
- **JupyterMarkdownCell**: Markdown cell with client-side rendering
- **JupyterCodeCell**: Code cell with execution_count and standard outputs
- **JupyterRawCell**: Raw cell for unformatted content
- **JupyterExecutionResult**: Jupyter-compatible execution results
- **JupyterOutput**: Standard Jupyter output types (stream, error, execute_result)

**Latest Features (2025-09-17)**:
- **Dual Format Support**: Complete .md and .ipynb format support with separate interfaces
- **Format Auto-Detection**: Automatic detection based on file extension and content
- **Jupyter Standard Compliance**: Full nbformat library integration
- **Client-side Markdown Rendering**: marked.js integration for Jupyter cells
- **Standard Jupyter UI**: In[]/Out[] prompts, execution_count management
- **Keyboard Shortcuts**: Standard Jupyter shortcuts (Shift+Enter, Ctrl+Enter, etc.)
- **Template Separation**: Dedicated templates and assets for each format

---

## 5. Anchor comments

Add specially formatted comments throughout the codebase for AI and developer reference:

### Guidelines:

- Use `# AIDEV-NOTE:`, `# AIDEV-TODO:`, or `# AIDEV-QUESTION:` for AI/developer comments.
- Keep them concise (≤ 120 chars).
- **Important:** Before scanning files, always first try to **locate existing anchors** `AIDEV-*` in relevant subdirectories.
- **Update relevant anchors** when modifying associated code.
- **Do not remove `AIDEV-NOTE`s** without explicit human instruction.

Example:
```python
# AIDEV-NOTE: Java class name extraction must handle edge cases like inner classes
def extract_class_name(java_code: str) -> str:
    ...
```

---

## 6. Commit discipline

*   **Granular commits**: One logical change per commit.
*   **Tag AI-generated commits**: e.g., `feat: add Java code execution engine [AI]`.
*   **Clear commit messages**: Explain the *why* in Korean or English.
*   **Review AI-generated code**: Never merge code you don't understand.

---

## 7. Web Interface & API Patterns

*   **Backend**: Flask or FastAPI for lightweight web server.
*   **Frontend**: Vanilla JavaScript with CodeMirror/Monaco Editor for code editing.
*   **API structure**: RESTful endpoints for notebook operations.

**API pattern examples**:
```python
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Render notebook interface."""
    return render_template('notebook.html')

@app.route('/api/execute', methods=['POST'])
def execute_java():
    """Execute Java code and return results."""
    java_code = request.json.get('code', '')
    result = compile_and_run_java(java_code)
    return jsonify(result)
```

---

## 8. Java Integration

*   All Java operations use `subprocess` module for external process management.
*   Each code cell runs as independent Java program with `main` method.
*   No state sharing between cells (unlike Python notebooks).
*   Temporary file management for compilation artifacts.

**Java execution requirements**:
- JDK must be installed and accessible via PATH
- Each code cell can contain either:
  - Complete, runnable Java program with main method
  - Simple Java statements (auto-wrapped with Main class and main method)
- Class name must match filename for successful compilation

---

## 9. Notebook File Format

*   Uses standard **Markdown** format for maximum compatibility.
*   Java code cells defined with ` ```java ` code blocks.
*   No custom file extensions required - standard `.md` files work.

**Example notebook structure**:
```markdown
# My Java Notebook

This is a markdown cell with documentation.

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

Simple statements are automatically wrapped (NEW FEATURE):

```java
// This code will be auto-wrapped with Main class and main method
System.out.println("Hello from simple statement!");
int x = 10;
int y = 20;
System.out.println("Sum: " + (x + y));
```

Another markdown cell explaining the next example.

```java
public class Calculator {
    public static void main(String[] args) {
        int sum = 5 + 3;
        System.out.println("5 + 3 = " + sum);
    }
}
```
```

---

## 10. Packaging & Distribution

*   **Setup**: Use `pyproject.toml` for modern Python packaging.
*   **Dependencies**: Flask/FastAPI, markdown parsing libraries.
*   **Entry points**: Command-line interface via `python -m javanotebook`.
*   **Distribution**: PyPI package for `pip install` compatibility.

**Package structure**:
```
javanotebook/
├── pyproject.toml
├── src/javanotebook/
│   ├── __init__.py
│   ├── __main__.py
│   └── ...
├── examples/
├── tests/
└── docs/
```

---

## 11. Environment Configuration

*   **Java requirement**: JDK 8+ must be installed and accessible.
*   **Python requirement**: Python 3.8+.
*   **Optional config**: Environment variables for default settings.
*   **Port configuration**: Default web server port with override option.

---

## 12. Common pitfalls

*   Don't assume JDK is installed - provide clear error messages.
*   Always clean up temporary files after Java execution.
*   Handle Java compilation errors gracefully.
*   Each Java code cell can be either self-contained program or simple statements (auto-wrapped).
*   Don't introduce complex state management between cells.
*   Validate Java code structure before attempting compilation.
*   When adding dynamic cells, ensure proper CodeMirror initialization and event binding.
*   Display both stdout and stderr for complete execution results.

---

## 13. Key File & Pattern References

**Important Files**:
*   `src/javanotebook/__main__.py`: Command-line entry point
*   `src/javanotebook/server.py`: Web server implementation
*   `src/javanotebook/parser.py`: Markdown notebook parser
*   `src/javanotebook/executor.py`: Java code execution engine
*   `pyproject.toml`: Package configuration and dependencies

**Common Patterns**:
*   Subprocess management for Java compilation/execution
*   Temporary file handling for Java source files
*   Markdown parsing for cell extraction
*   Web API for code execution requests
*   Error handling for compilation and runtime errors
*   Dynamic DOM manipulation for cell management
*   Auto-wrapping of simple Java statements
*   Dual output display (stdout + stderr)

---

## 14. Domain-Specific Terminology

*   **Notebook**: Markdown file containing mix of documentation and Java code
*   **Cell**: Individual unit of notebook content (markdown or Java code)
*   **Dynamic Cell**: Code cell added at runtime via web interface
*   **Execution**: Process of compiling and running Java code cell
*   **Code Block**: Markdown fenced code block with `java` language specifier
*   **Class Extraction**: Process of finding public class name in Java code
*   **Auto-wrapping**: Automatic wrapping of simple statements with Main class
*   **Orchestration**: Python managing Java compilation and execution workflow
*   **Dual Output**: Display of both stdout and stderr in execution results

---

## AI Assistant Workflow: Step-by-Step Methodology

When responding to user instructions:

1. **Consult Relevant Guidance**: Check this CLAUDE.md for project-specific context.
2. **Clarify Ambiguities**: Ask targeted questions if requirements are unclear.
3. **Break Down & Plan**: Create a plan referencing project conventions.
4. **Trivial Tasks**: Execute immediately for simple requests.
5. **Non-Trivial Tasks**: Present plan for user review first.
6. **Track Progress**: Use todo lists for multi-step tasks.
7. **If Stuck, Re-plan**: Return to planning if blocked.
8. **Update Documentation**: Update anchor comments and this file as needed.
9. **User Review**: Ask for review after completion.
10. **Session Boundaries**: Suggest fresh start for unrelated contexts.