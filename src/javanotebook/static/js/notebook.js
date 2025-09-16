// Java Notebook JavaScript

class NotebookManager {
    constructor() {
        this.editors = new Map();
        this.executionInProgress = new Set();
        this.cellCounter = 1000; // Start from 1000 to avoid conflicts with existing cells
        // AIDEV-NOTE: Markdown is now rendered server-side, no client processing needed
    }

    initializeCodeEditors() {
        // AIDEV-NOTE: Initialize CodeMirror for all code cells
        document.querySelectorAll('.code-cell .code-editor').forEach(textarea => {
            const cellId = textarea.id.replace('editor-', '');
            
            const editor = CodeMirror.fromTextArea(textarea, {
                mode: 'text/x-java',
                lineNumbers: true,
                theme: 'default',
                indentUnit: 4,
                lineWrapping: true,
                autoCloseBrackets: true,
                matchBrackets: true,
                foldGutter: true,
                gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
                // Enhanced editor options
                indentWithTabs: false,
                smartIndent: true,
                electricChars: true,
                autocorrect: false,
                spellcheck: false,
                tabSize: 4,
                showTrailingSpace: true,
                highlightSelectionMatches: {showToken: /\w/, annotateScrollbar: true}
            });

            // Store editor reference
            this.editors.set(cellId, editor);

            // Enhanced keyboard shortcuts
            editor.setOption('extraKeys', {
                // Execution shortcuts
                'Ctrl-Enter': () => this.executeCell(cellId),
                'Shift-Enter': () => this.executeCell(cellId),
                'Ctrl-Shift-Enter': () => this.executeAllCells(),
                
                // Code editing shortcuts
                'Ctrl-/': 'toggleComment',
                'Ctrl-]': 'indentMore',
                'Ctrl-[': 'indentLess',
                'Ctrl-A': 'selectAll',
                'Ctrl-D': 'deleteLine',
                'Ctrl-Shift-D': 'duplicateLine',
                
                // Validation shortcut
                'Ctrl-Shift-V': () => this.validateCell(cellId),
                
                // Format shortcut
                'Ctrl-Shift-F': (cm) => this.formatJavaCode(cm),
                
                // Navigation shortcuts
                'Ctrl-G': 'jumpToLine',
                'Ctrl-F': 'findPersistent',
                'F3': 'findNext',
                'Shift-F3': 'findPrev',
                
                // Auto-complete (basic)
                'Ctrl-Space': 'autocomplete'
            });

            // Auto-resize editor
            this.autoResizeEditor(editor);
            
            // Add change listener for auto-save functionality
            editor.on('change', () => {
                this.onEditorChange(cellId, editor);
            });
        });
    }

    async executeCell(cellId) {
        if (this.executionInProgress.has(cellId)) {
            return; // Already executing
        }

        const editor = this.editors.get(cellId);
        if (!editor) {
            console.error(`Editor not found for cell ${cellId}`);
            return;
        }

        const code = editor.getValue().trim();
        if (!code) {
            this.showError(cellId, '실행할 코드가 없습니다.');
            return;
        }

        try {
            this.setExecutionState(cellId, true);
            
            const response = await fetch('/api/v1/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: code,
                    cell_id: cellId
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.displayResult(cellId, result);
            } else {
                this.showError(cellId, result.detail || '실행 중 오류가 발생했습니다.');
            }

        } catch (error) {
            console.error('Execution error:', error);
            this.showError(cellId, `네트워크 오류: ${error.message}`);
        } finally {
            this.setExecutionState(cellId, false);
        }
    }

    async validateCell(cellId) {
        const editor = this.editors.get(cellId);
        if (!editor) {
            console.error(`Editor not found for cell ${cellId}`);
            return;
        }

        const code = editor.getValue().trim();
        if (!code) {
            this.showError(cellId, '검증할 코드가 없습니다.');
            return;
        }

        try {
            const response = await fetch('/api/v1/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: code,
                    cell_id: cellId
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.displayValidationResult(cellId, result);
            } else {
                this.showError(cellId, result.detail || '검증 중 오류가 발생했습니다.');
            }

        } catch (error) {
            console.error('Validation error:', error);
            this.showError(cellId, `네트워크 오류: ${error.message}`);
        }
    }

    setExecutionState(cellId, isExecuting) {
        const runButton = document.querySelector(`[onclick="executeCell('${cellId}')"]`);
        const spinner = runButton.querySelector('.btn-spinner');
        const text = runButton.querySelector('.btn-text');

        if (isExecuting) {
            this.executionInProgress.add(cellId);
            runButton.disabled = true;
            spinner.style.display = 'inline';
            text.textContent = '실행 중...';
            runButton.classList.add('loading');
        } else {
            this.executionInProgress.delete(cellId);
            runButton.disabled = false;
            spinner.style.display = 'none';
            text.textContent = '실행';
            runButton.classList.remove('loading');
        }
    }

    displayResult(cellId, result) {
        const outputDiv = document.getElementById(`output-${cellId}`);
        const outputContent = outputDiv.querySelector('.output-content');
        
        outputDiv.style.display = 'block';
        
        // Clear previous classes
        outputDiv.classList.remove('output-success', 'output-error');
        
        if (result.success) {
            outputDiv.classList.add('output-success');
            
            // AIDEV-NOTE: Display both stdout and stderr for successful executions
            let outputHtml = '';
            
            // Standard output
            if (result.stdout && result.stdout.trim()) {
                outputHtml += `
                    <div class="output-stdout">
                        <pre>${this.escapeHtml(result.stdout)}</pre>
                    </div>
                `;
            }
            
            // Standard error (정상 실행이지만 System.err.println() 등의 출력)
            if (result.stderr && result.stderr.trim()) {
                outputHtml += `
                    <div class="output-stderr">
                        <div class="stderr-label">표준 에러:</div>
                        <pre>${this.escapeHtml(result.stderr)}</pre>
                    </div>
                `;
            }
            
            // 출력이 전혀 없는 경우
            if (!outputHtml) {
                outputHtml = `
                    <div class="output-stdout">
                        <pre>(출력 없음)</pre>
                    </div>
                `;
            }
            
            outputContent.innerHTML = `
                ${outputHtml}
                ${result.execution_time ? `<div class="execution-info">
                    <span class="execution-time">⏱️ ${result.execution_time.toFixed(3)}초</span>
                    <span class="execution-status">✅ 성공</span>
                </div>` : ''}
            `;
        } else {
            outputDiv.classList.add('output-error');
            let errorContent = this.formatError(result);
            
            outputContent.innerHTML = `
                <div class="output-error-content">
                    ${errorContent}
                </div>
                ${result.execution_time ? `<div class="execution-info">
                    <span class="execution-time">⏱️ ${result.execution_time.toFixed(3)}초</span>
                    <span class="execution-status">❌ 실패</span>
                </div>` : ''}
            `;
        }
    }

    formatError(result) {
        if (result.compilation_error) {
            return this.formatCompilationError(result.compilation_error);
        } else if (result.stderr) {
            return this.formatRuntimeError(result.stderr);
        } else if (result.error_message) {
            return `<div class="error-message">
                <div class="error-type">⚠️ 실행 오류</div>
                <pre>${this.escapeHtml(result.error_message)}</pre>
            </div>`;
        } else {
            return `<div class="error-message">
                <div class="error-type">❓ 알 수 없는 오류</div>
                <pre>오류 정보를 확인할 수 없습니다.</pre>
            </div>`;
        }
    }

    formatCompilationError(error) {
        // Display original compilation error message without parsing
        let formattedError = '<div class="error-message compilation-error">';
        formattedError += '<div class="error-type">🔨 컴파일 오류</div>';
        
        // Show the complete original error message
        formattedError += `<div class="error-original">
            <pre>${this.escapeHtml(error)}</pre>
        </div>`;
        
        formattedError += '</div>';
        return formattedError;
    }

    formatRuntimeError(error) {
        // AIDEV-NOTE: Display complete runtime error including stack trace immediately
        let formattedError = '<div class="error-message runtime-error">';
        formattedError += '<div class="error-type">⚡ 실행 오류</div>';
        
        // Display the complete original error message including stack trace
        formattedError += `<div class="error-original">
            <pre>${this.escapeHtml(error)}</pre>
        </div>`;
        
        formattedError += '</div>';
        return formattedError;
    }

    displayValidationResult(cellId, result) {
        const outputDiv = document.getElementById(`output-${cellId}`);
        const outputContent = outputDiv.querySelector('.output-content');
        
        outputDiv.style.display = 'block';
        outputDiv.classList.remove('output-success', 'output-error');
        
        if (result.valid) {
            outputDiv.classList.add('output-success');
            outputContent.innerHTML = `
                <pre>✅ 코드 구조가 올바릅니다.
클래스명: ${result.class_name || 'N/A'}
main 메소드: ${result.has_main_method ? '있음' : '없음'}</pre>
            `;
        } else {
            outputDiv.classList.add('output-error');
            const errors = result.errors || ['검증 실패'];
            outputContent.innerHTML = `
                <pre>❌ 코드 구조에 문제가 있습니다:
${errors.map(error => `• ${error}`).join('\n')}

클래스명: ${result.class_name || 'N/A'}
main 메소드: ${result.has_main_method ? '있음' : '없음'}</pre>
            `;
        }
    }

    showError(cellId, message) {
        const outputDiv = document.getElementById(`output-${cellId}`);
        const outputContent = outputDiv.querySelector('.output-content');
        
        outputDiv.style.display = 'block';
        outputDiv.classList.remove('output-success');
        outputDiv.classList.add('output-error');
        
        outputContent.innerHTML = `<pre>${this.escapeHtml(message)}</pre>`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Additional utility methods
    formatJavaCode(editor) {
        // Basic Java code formatting
        const code = editor.getValue();
        const formatted = this.basicJavaFormat(code);
        editor.setValue(formatted);
    }

    basicJavaFormat(code) {
        // Simple Java code formatting
        let formatted = code;
        
        // Add space after keywords
        formatted = formatted.replace(/\b(if|for|while|switch|catch)\(/g, '$1 (');
        
        // Fix spacing around operators
        formatted = formatted.replace(/([^=!<>])=([^=])/g, '$1 = $2');
        formatted = formatted.replace(/([^<>])>=?([^=])/g, '$1 >= $2');
        formatted = formatted.replace(/([^<>])<=?([^=])/g, '$1 <= $2');
        
        // Fix spacing around braces
        formatted = formatted.replace(/\)\{/g, ') {');
        
        return formatted;
    }

    onEditorChange(cellId, editor) {
        // Simple change tracking for future features
        const content = editor.getValue();
        const cell = document.querySelector(`[data-cell-id="${cellId}"]`);
        
        if (content.trim()) {
            cell.classList.add('has-content');
        } else {
            cell.classList.remove('has-content');
        }
        
        // Clear any previous output when code changes
        const outputDiv = document.getElementById(`output-${cellId}`);
        if (outputDiv && outputDiv.style.display === 'block') {
            outputDiv.classList.add('outdated');
        }
    }

    autoResizeEditor(editor) {
        const updateHeight = () => {
            const lineCount = editor.lineCount();
            const lineHeight = editor.defaultTextHeight();
            const minHeight = 150;
            const maxHeight = 500;
            const newHeight = Math.min(maxHeight, Math.max(minHeight, lineCount * lineHeight + 20));
            
            editor.setSize(null, newHeight);
        };

        editor.on('change', updateHeight);
        editor.on('viewportChange', updateHeight);
        
        // Initial resize
        setTimeout(updateHeight, 100);
    }

    // Global keyboard shortcuts
    setupGlobalShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Prevent default browser shortcuts that conflict
            if (event.ctrlKey && event.key === 's') {
                event.preventDefault();
                this.showShortcutHelp();
            }
            
            // Ctrl+Shift+A to run all cells
            if (event.ctrlKey && event.shiftKey && event.key === 'A') {
                event.preventDefault();
                this.executeAllCells();
            }
            
            // Escape to clear all outputs
            if (event.key === 'Escape' && event.shiftKey) {
                event.preventDefault();
                this.clearAllOutputs();
            }
            
            // F1 for help
            if (event.key === 'F1') {
                event.preventDefault();
                this.showShortcutHelp();
            }
        });
    }

    showShortcutHelp() {
        const shortcuts = `
키보드 단축키:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

실행:
• Ctrl+Enter / Shift+Enter : 현재 셀 실행
• Ctrl+Shift+Enter : 모든 셀 실행
• Ctrl+Shift+V : 현재 셀 검증

편집:
• Ctrl+/ : 주석 토글
• Ctrl+] : 들여쓰기 증가
• Ctrl+[ : 들여쓰기 감소
• Ctrl+D : 현재 라인 삭제
• Ctrl+Shift+D : 현재 라인 복제
• Ctrl+Shift+F : 코드 포맷팅

탐색:
• Ctrl+F : 찾기
• F3 : 다음 찾기
• Shift+F3 : 이전 찾기
• Ctrl+G : 라인으로 이동

기타:
• F1 : 이 도움말 표시
• Shift+Esc : 모든 출력 지우기
        `;
        
        alert(shortcuts.trim());
    }

    clearAllOutputs() {
        document.querySelectorAll('.cell-output').forEach(output => {
            output.style.display = 'none';
            output.classList.remove('outdated');
        });
        
        console.log('모든 출력이 지워졌습니다.');
    }

    async executeAllCells() {
        const codeCells = document.querySelectorAll('.code-cell');
        for (const cell of codeCells) {
            const cellId = cell.dataset.cellId;
            if (cellId && !this.executionInProgress.has(cellId)) {
                await this.executeCell(cellId);
                // Add small delay between executions
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        }
    }

    addNewCodeCell() {
        // AIDEV-NOTE: Add new Java code cell dynamically
        const cellId = `cell-new-${this.cellCounter++}`;
        
        // Create new cell HTML
        const cellHtml = `
            <div class="cell code-cell" data-cell-id="${cellId}">
                <div class="cell-header">
                    <span class="cell-type">☕ Java Code</span>
                    <div class="cell-actions">
                        <button class="btn btn-run" onclick="executeCell('${cellId}')">
                            <span class="btn-text">실행</span>
                            <span class="btn-spinner" style="display: none;">⚡</span>
                        </button>
                        <button class="btn btn-validate" onclick="validateCell('${cellId}')">검증</button>
                        <button class="btn btn-delete" onclick="deleteCell('${cellId}')">삭제</button>
                    </div>
                </div>
                <div class="cell-content">
                    <textarea class="code-editor" id="editor-${cellId}">// Java 코드를 입력하세요
System.out.println("Hello, World!");</textarea>
                </div>
                <div class="cell-output" id="output-${cellId}" style="display: none;">
                    <div class="output-header">실행 결과:</div>
                    <div class="output-content"></div>
                </div>
            </div>
        `;
        
        // Insert the new cell at the end of the notebook
        const notebook = document.querySelector('.notebook');
        notebook.insertAdjacentHTML('beforeend', cellHtml);
        
        // Initialize CodeMirror editor for the new cell
        this.initializeNewCellEditor(cellId);
        
        // Scroll to the new cell
        const newCell = document.querySelector(`[data-cell-id="${cellId}"]`);
        newCell.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Focus on the new editor
        setTimeout(() => {
            const editor = this.editors.get(cellId);
            if (editor) {
                editor.focus();
                editor.setCursor(editor.lineCount(), 0); // Move cursor to end
            }
        }, 100);
        
        console.log(`새로운 코드 셀 추가됨: ${cellId}`);
    }

    initializeNewCellEditor(cellId) {
        // AIDEV-NOTE: Initialize CodeMirror for a specific new cell
        const textarea = document.getElementById(`editor-${cellId}`);
        if (!textarea) {
            console.error(`Editor textarea not found for cell ${cellId}`);
            return;
        }

        const editor = CodeMirror.fromTextArea(textarea, {
            mode: 'text/x-java',
            lineNumbers: true,
            theme: 'default',
            indentUnit: 4,
            lineWrapping: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            foldGutter: true,
            gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
            indentWithTabs: false,
            smartIndent: true,
            electricChars: true,
            autocorrect: false,
            spellcheck: false,
            tabSize: 4,
            showTrailingSpace: true,
            highlightSelectionMatches: {showToken: /\w/, annotateScrollbar: true}
        });

        // Store editor reference
        this.editors.set(cellId, editor);

        // Enhanced keyboard shortcuts
        editor.setOption('extraKeys', {
            'Ctrl-Enter': () => this.executeCell(cellId),
            'Shift-Enter': () => this.executeCell(cellId),
            'Ctrl-Shift-Enter': () => this.executeAllCells(),
            'Ctrl-/': 'toggleComment',
            'Ctrl-]': 'indentMore',
            'Ctrl-[': 'indentLess',
            'Ctrl-A': 'selectAll',
            'Ctrl-D': 'deleteLine',
            'Ctrl-Shift-D': 'duplicateLine',
            'Ctrl-Shift-V': () => this.validateCell(cellId),
            'Ctrl-Shift-F': (cm) => this.formatJavaCode(cm),
            'Ctrl-G': 'jumpToLine',
            'Ctrl-F': 'findPersistent',
            'F3': 'findNext',
            'Shift-F3': 'findPrev',
            'Ctrl-Space': 'autocomplete'
        });

        // Auto-resize editor
        this.autoResizeEditor(editor);
        
        // Add change listener
        editor.on('change', () => {
            this.onEditorChange(cellId, editor);
        });
    }

    deleteCell(cellId) {
        // AIDEV-NOTE: Delete a dynamically created cell
        if (confirm('이 셀을 삭제하시겠습니까?')) {
            // Remove editor reference
            if (this.editors.has(cellId)) {
                this.editors.delete(cellId);
            }
            
            // Remove execution state
            this.executionInProgress.delete(cellId);
            
            // Remove cell from DOM
            const cell = document.querySelector(`[data-cell-id="${cellId}"]`);
            if (cell) {
                cell.remove();
                console.log(`셀 삭제됨: ${cellId}`);
            }
        }
    }
}

// Global functions for button onclick handlers
let notebookManager;

function executeCell(cellId) {
    if (notebookManager) {
        notebookManager.executeCell(cellId);
    }
}

function validateCell(cellId) {
    if (notebookManager) {
        notebookManager.validateCell(cellId);
    }
}

function addNewCodeCell() {
    if (notebookManager) {
        notebookManager.addNewCodeCell();
    }
}

function deleteCell(cellId) {
    if (notebookManager) {
        notebookManager.deleteCell(cellId);
    }
}

function initializeNotebook() {
    notebookManager = new NotebookManager();
    notebookManager.initializeCodeEditors();
    notebookManager.setupGlobalShortcuts();
    
    console.log('Java Notebook initialized successfully');
}

// Auto-resize CodeMirror editors
function autoResizeEditor(editor) {
    editor.on('change', function() {
        const lineCount = editor.lineCount();
        const minHeight = 200;
        const lineHeight = 20;
        const newHeight = Math.max(minHeight, lineCount * lineHeight + 40);
        
        editor.setSize(null, newHeight);
    });
}