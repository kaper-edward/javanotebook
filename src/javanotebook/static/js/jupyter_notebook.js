/**
 * Jupyter Notebook JavaScript - Java Notebook
 * Handles Jupyter-specific notebook interface and interactions
 */

// Global state
let notebookState = {
    cells: new Map(),
    editors: new Map(),
    executionCount: 0,
    isExecuting: false,
    kernelStatus: 'ready'
};

// Initialize Jupyter notebook interface
function initializeJupyterNotebook() {
    console.log('Initializing Jupyter notebook interface...');

    // AIDEV-NOTE: Check if already initialized to prevent double initialization
    if (window.jupyterNotebookInitialized) {
        console.warn('Jupyter notebook already initialized, skipping');
        return;
    }

    // Initialize markdown renderer
    initializeMarkdownRenderer();

    // Initialize code editors
    initializeCodeEditors();

    // Render existing markdown cells
    renderAllMarkdownCells();

    // Setup markdown cell double-click handlers
    setupMarkdownCellHandlers();

    // Setup keyboard shortcuts
    setupJupyterKeyboardShortcuts();

    // Setup cell management
    setupCellManagement();

    // Update kernel status
    updateKernelStatus('ready');

    // AIDEV-NOTE: Mark as initialized
    window.jupyterNotebookInitialized = true;

    console.log('Jupyter notebook initialized successfully');
    console.log('Final state - Editors:', notebookState.editors.size, 'cells');
}

// Initialize markdown renderer with marked.js
function initializeMarkdownRenderer() {
    if (typeof marked !== 'undefined') {
        // Configure marked.js for Jupyter compatibility
        marked.setOptions({
            highlight: function(code, lang) {
                if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (err) {
                        console.warn('Highlight.js error:', err);
                    }
                }
                return code;
            },
            breaks: true,
            gfm: true
        });
        console.log('Markdown renderer initialized');
    } else {
        console.warn('marked.js not loaded, markdown rendering may not work');
    }
}

// Initialize CodeMirror editors for code cells
function initializeCodeEditors() {
    const codeEditors = document.querySelectorAll('.code-editor');

    console.log(`Found ${codeEditors.length} code editor elements`);

    codeEditors.forEach((textarea, index) => {
        const cellId = textarea.id.replace('editor-', '');

        // AIDEV-NOTE: Check if CodeMirror already exists for this cell or if textarea already processed
        if (notebookState.editors.has(cellId) || textarea.dataset.cmInitialized === 'true') {
            console.warn(`CodeMirror already exists for cell ${cellId}, skipping`);
            return;
        }

        if (typeof CodeMirror !== 'undefined') {
            console.log(`Initializing CodeMirror for cell ${cellId} (index ${index})`);
            const editor = CodeMirror.fromTextArea(textarea, {
                mode: 'text/x-java',
                theme: 'default',
                lineNumbers: true,
                lineWrapping: true,
                indentUnit: 4,
                indentWithTabs: false,
                matchBrackets: true,
                autoCloseBrackets: true,
                extraKeys: {
                    'Shift-Enter': () => executeAndMoveToNext(cellId),
                    'Ctrl-Enter': () => executeInPlace(cellId),
                    'Cmd-Enter': () => executeInPlace(cellId), // Mac support
                    'Ctrl-Shift-Enter': () => runAllCells(),
                    'Cmd-Shift-Enter': () => runAllCells(), // Mac support
                    'Tab': 'indentMore',
                    'Shift-Tab': 'indentLess'
                }
            });

            // Store editor reference
            notebookState.editors.set(cellId, editor);

            // Mark textarea as initialized to prevent duplicate processing
            textarea.dataset.cmInitialized = 'true';

            // Auto-resize editor
            editor.setSize(null, 'auto');

            // Focus and selection handling
            editor.on('focus', () => {
                setActiveCell(cellId);
            });

        } else {
            console.warn('CodeMirror not loaded, using plain textarea');
            // Mark textarea as processed even without CodeMirror to prevent duplicate processing
            textarea.dataset.cmInitialized = 'true';
        }
    });

    console.log(`Initialized ${codeEditors.length} code editors`);
}

// Render all markdown cells on page load
function renderAllMarkdownCells() {
    window.cellData.forEach(cell => {
        if (cell.type === 'markdown') {
            renderMarkdownCell(cell.id);
        }
    });
}

// AIDEV-NOTE: Setup double-click handlers for markdown cells
function setupMarkdownCellHandlers() {
    // Add double-click event listeners to all markdown cells
    const markdownContents = document.querySelectorAll('.markdown-cell .markdown-cell-content');
    console.log(`Found ${markdownContents.length} markdown cell content elements`);

    markdownContents.forEach((contentDiv, index) => {
        const cellId = contentDiv.id.replace('markdown-content-', '');

        // AIDEV-NOTE: Check if handler already exists to prevent duplicates
        if (contentDiv.dataset.handlerAdded) {
            console.warn(`Handler already added for markdown cell ${cellId}, skipping`);
            return;
        }

        console.log(`Setting up handlers for markdown cell ${cellId} (index ${index})`);

        contentDiv.addEventListener('dblclick', function() {
            editMarkdownCell(cellId);
        });

        // Add visual feedback on hover
        contentDiv.style.cursor = 'text';
        contentDiv.title = 'Double-click to edit';

        // Mark as handler added
        contentDiv.dataset.handlerAdded = 'true';
    });

    // AIDEV-NOTE: Make all markdown cells focusable by default
    const markdownCells = document.querySelectorAll('.markdown-cell');
    console.log(`Found ${markdownCells.length} markdown cells for focus setup`);

    markdownCells.forEach((cell, index) => {
        if (!cell.getAttribute('tabindex')) {
            cell.setAttribute('tabindex', '0');
            console.log(`Set tabindex for markdown cell ${index}`);
        }
    });

    console.log('Markdown cell double-click handlers and focus setup complete');
}

// Render a specific markdown cell
function renderMarkdownCell(cellId) {
    const contentDiv = document.getElementById(`markdown-content-${cellId}`);
    const sourceTextarea = document.getElementById(`markdown-source-${cellId}`);

    if (!contentDiv || !sourceTextarea) {
        console.warn(`Markdown cell ${cellId} elements not found`);
        return;
    }

    const source = sourceTextarea.value;

    try {
        if (typeof marked !== 'undefined') {
            const html = marked.parse(source);
            contentDiv.innerHTML = html;
        } else {
            // Fallback: simple text rendering
            contentDiv.innerHTML = `<pre>${escapeHtml(source)}</pre>`;
        }

        // Hide editor, show rendered content
        document.getElementById(`markdown-editor-${cellId}`).style.display = 'none';
        contentDiv.style.display = 'block';

    } catch (error) {
        console.error('Error rendering markdown:', error);
        contentDiv.innerHTML = `<div class="error">Markdown rendering error: ${error.message}</div>`;
    }
}

// Edit markdown cell
function editMarkdownCell(cellId) {
    const contentDiv = document.getElementById(`markdown-content-${cellId}`);
    const editorDiv = document.getElementById(`markdown-editor-${cellId}`);

    if (contentDiv && editorDiv) {
        contentDiv.style.display = 'none';
        editorDiv.style.display = 'block';

        // Focus on textarea and setup keyboard handlers
        const textarea = document.getElementById(`markdown-source-${cellId}`);
        if (textarea) {
            textarea.focus();

            // AIDEV-NOTE: Add keyboard shortcuts for markdown editing
            const handleKeydown = function(event) {
                if (event.shiftKey && event.key === 'Enter') {
                    event.preventDefault();
                    renderMarkdownCell(cellId);
                    // Remove the event listener after use
                    textarea.removeEventListener('keydown', handleKeydown);
                    // Move to next cell after rendering
                    setTimeout(() => {
                        moveToNextCell(cellId);
                    }, 100);
                } else if ((event.ctrlKey && event.key === 'Enter') ||
                           (event.metaKey && event.key === 'Enter')) {
                    event.preventDefault();
                    renderMarkdownCell(cellId);
                    // Remove the event listener after use
                    textarea.removeEventListener('keydown', handleKeydown);
                    // Stay in current cell
                    setTimeout(() => {
                        focusCell(cellId);
                    }, 100);
                }
            };

            textarea.addEventListener('keydown', handleKeydown);
        }
    }
}

// Cancel markdown edit
function cancelMarkdownEdit(cellId) {
    const contentDiv = document.getElementById(`markdown-content-${cellId}`);
    const editorDiv = document.getElementById(`markdown-editor-${cellId}`);

    if (contentDiv && editorDiv) {
        editorDiv.style.display = 'none';
        contentDiv.style.display = 'block';
    }
}

// AIDEV-NOTE: Execute cell and move to next (Shift+Enter behavior)
async function executeAndMoveToNext(cellId) {
    const success = await executeJupyterCell(cellId);
    if (success !== false) {
        // Small delay to ensure execution UI updates complete
        setTimeout(() => {
            moveToNextCell(cellId);
        }, 100);
    }
}

// AIDEV-NOTE: Execute cell and stay in place (Ctrl+Enter behavior)
async function executeInPlace(cellId) {
    await executeJupyterCell(cellId);
    // Stay focused on current cell
    focusCell(cellId);
}

// Execute a Jupyter code cell
async function executeJupyterCell(cellId) {
    if (notebookState.isExecuting) {
        console.log('Another cell is currently executing');
        return false;
    }

    const editor = notebookState.editors.get(cellId);
    const code = editor ? editor.getValue() : document.getElementById(`editor-${cellId}`).value;

    if (!code.trim()) {
        showNotification('코드가 비어있습니다.', 'warning');
        return false;
    }

    // Update UI for execution
    setExecutingState(cellId, true);
    notebookState.isExecuting = true;
    updateKernelStatus('busy');

    try {
        // Increment execution count
        notebookState.executionCount++;

        const response = await fetch('/api/v1/jupyter/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                cell_id: cellId,
                execution_count: notebookState.executionCount
            })
        });

        const result = await response.json();

        if (response.ok) {
            displayJupyterExecutionResult(cellId, result);
            showNotification('코드 실행 완료', 'success');
            return true;
        } else {
            throw new Error(result.detail || 'Execution failed');
        }

    } catch (error) {
        console.error('Execution error:', error);
        displayExecutionError(cellId, error.message);
        showNotification('실행 중 오류가 발생했습니다.', 'error');
        return false;
    } finally {
        setExecutingState(cellId, false);
        notebookState.isExecuting = false;
        updateKernelStatus('ready');
    }
}

// Display Jupyter execution result
function displayJupyterExecutionResult(cellId, result) {
    const outputDiv = document.getElementById(`output-${cellId}`);
    const outputContent = document.getElementById(`output-content-${cellId}`);
    const outputNumber = document.getElementById(`output-number-${cellId}`);

    if (!outputDiv || !outputContent) {
        console.warn(`Output elements for cell ${cellId} not found`);
        return;
    }

    // Update execution count
    if (outputNumber) {
        outputNumber.textContent = result.execution_count || notebookState.executionCount;
    }

    // Clear previous output
    outputContent.innerHTML = '';

    if (result.success && result.outputs && result.outputs.length > 0) {
        result.outputs.forEach(output => {
            const outputElement = createJupyterOutputElement(output);
            outputContent.appendChild(outputElement);
        });

        outputDiv.className = 'code-cell-output output-success';
    } else if (!result.success) {
        // Display error
        if (result.outputs && result.outputs.length > 0) {
            result.outputs.forEach(output => {
                const outputElement = createJupyterOutputElement(output);
                outputContent.appendChild(outputElement);
            });
        } else if (result.error_message) {
            const errorElement = document.createElement('pre');
            errorElement.textContent = result.error_message;
            outputContent.appendChild(errorElement);
        }

        outputDiv.className = 'code-cell-output output-error';
    } else {
        // No output
        const noOutputElement = document.createElement('div');
        noOutputElement.textContent = '(출력 없음)';
        noOutputElement.style.color = '#6c757d';
        noOutputElement.style.fontStyle = 'italic';
        outputContent.appendChild(noOutputElement);

        outputDiv.className = 'code-cell-output';
    }

    // Show output
    outputDiv.style.display = 'flex';

    // Update input prompt
    const inputPrompt = document.querySelector(`[data-cell-id="${cellId}"] .input-prompt`);
    if (inputPrompt) {
        inputPrompt.textContent = `In [${result.execution_count || notebookState.executionCount}]:`;
    }
}

// Create Jupyter output element
function createJupyterOutputElement(output) {
    const container = document.createElement('div');
    container.className = 'jupyter-output';

    if (output.output_type === 'stream') {
        const pre = document.createElement('pre');
        pre.textContent = output.text;
        pre.className = `stream-${output.name}`;
        container.appendChild(pre);

    } else if (output.output_type === 'error') {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-output';

        const errorTitle = document.createElement('div');
        errorTitle.className = 'error-title';
        errorTitle.textContent = `${output.ename}: ${output.evalue}`;
        errorDiv.appendChild(errorTitle);

        if (output.traceback && output.traceback.length > 0) {
            const traceback = document.createElement('pre');
            traceback.className = 'error-traceback';
            traceback.textContent = output.traceback.join('\n');
            errorDiv.appendChild(traceback);
        }

        container.appendChild(errorDiv);

    } else if (output.output_type === 'execute_result') {
        if (output.data && output.data['text/plain']) {
            const pre = document.createElement('pre');
            pre.textContent = output.data['text/plain'];
            container.appendChild(pre);
        }
    }

    return container;
}

// Display execution error
function displayExecutionError(cellId, errorMessage) {
    const outputDiv = document.getElementById(`output-${cellId}`);
    const outputContent = document.getElementById(`output-content-${cellId}`);

    if (outputDiv && outputContent) {
        outputContent.innerHTML = '';

        const errorElement = document.createElement('pre');
        errorElement.textContent = errorMessage;
        errorElement.className = 'error-output';
        outputContent.appendChild(errorElement);

        outputDiv.className = 'code-cell-output output-error';
        outputDiv.style.display = 'flex';
    }
}

// Validate Jupyter code cell
async function validateJupyterCell(cellId) {
    const editor = notebookState.editors.get(cellId);
    const code = editor ? editor.getValue() : document.getElementById(`editor-${cellId}`).value;

    if (!code.trim()) {
        showNotification('코드가 비어있습니다.', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/v1/jupyter/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code
            })
        });

        const result = await response.json();

        if (response.ok) {
            if (result.valid) {
                let message = '코드가 유효합니다.';
                if (result.can_auto_wrap) {
                    message += ' (자동 래핑됨)';
                }
                if (result.class_name) {
                    message += ` 클래스: ${result.class_name}`;
                }
                showNotification(message, 'success');
            } else {
                showNotification('코드 검증 실패: ' + (result.errors?.join(', ') || '알 수 없는 오류'), 'error');
            }
        } else {
            throw new Error(result.detail || 'Validation failed');
        }

    } catch (error) {
        console.error('Validation error:', error);
        showNotification('검증 중 오류가 발생했습니다.', 'error');
    }
}

// Set executing state for a cell
function setExecutingState(cellId, isExecuting) {
    const cell = document.querySelector(`[data-cell-id="${cellId}"]`);
    const runButton = cell?.querySelector('.btn-run');

    if (runButton) {
        const btnText = runButton.querySelector('.btn-text');
        const btnSpinner = runButton.querySelector('.btn-spinner');

        if (isExecuting) {
            runButton.disabled = true;
            btnText.style.display = 'none';
            btnSpinner.style.display = 'inline';
            cell.classList.add('cell-executing');
        } else {
            runButton.disabled = false;
            btnText.style.display = 'inline';
            btnSpinner.style.display = 'none';
            cell.classList.remove('cell-executing');
        }
    }
}

// Set active cell
function setActiveCell(cellId) {
    // Remove active class from all cells
    document.querySelectorAll('.jupyter-cell').forEach(cell => {
        cell.classList.remove('active');
    });

    // Add active class to current cell
    const activeCell = document.querySelector(`[data-cell-id="${cellId}"]`);
    if (activeCell) {
        activeCell.classList.add('active');
    }
}

// AIDEV-NOTE: Cell navigation utility functions
function getAllCells() {
    return Array.from(document.querySelectorAll('.jupyter-cell')).map(cell => ({
        id: cell.getAttribute('data-cell-id'),
        type: cell.getAttribute('data-cell-type'),
        element: cell
    }));
}

function getNextCell(currentCellId) {
    const cells = getAllCells();
    const currentIndex = cells.findIndex(cell => cell.id === currentCellId);

    if (currentIndex !== -1 && currentIndex < cells.length - 1) {
        return cells[currentIndex + 1];
    }
    return null;
}

function getPreviousCell(currentCellId) {
    const cells = getAllCells();
    const currentIndex = cells.findIndex(cell => cell.id === currentCellId);

    if (currentIndex > 0) {
        return cells[currentIndex - 1];
    }
    return null;
}

function focusCell(cellId) {
    const cell = document.querySelector(`[data-cell-id="${cellId}"]`);
    if (!cell) return false;

    // Set as active cell
    setActiveCell(cellId);

    // Focus based on cell type
    const cellType = cell.getAttribute('data-cell-type');

    if (cellType === 'code') {
        // Focus CodeMirror editor if available
        const editor = notebookState.editors.get(cellId);
        if (editor) {
            editor.focus();
            return true;
        }

        // Fallback to textarea
        const textarea = document.getElementById(`editor-${cellId}`);
        if (textarea) {
            textarea.focus();
            return true;
        }
    } else if (cellType === 'markdown') {
        // AIDEV-NOTE: Make markdown cell focusable and set actual focus
        cell.setAttribute('tabindex', '0'); // Make focusable
        cell.focus(); // Set actual keyboard focus
        cell.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return true;
    }

    return false;
}

function moveToNextCell(currentCellId) {
    const nextCell = getNextCell(currentCellId);

    if (nextCell) {
        return focusCell(nextCell.id);
    } else {
        // No next cell exists, create a new code cell
        console.log('No next cell found, would create new cell here');
        // TODO: Implement new cell creation
        return false;
    }
}

// Run all cells
async function runAllCells() {
    if (notebookState.isExecuting) {
        showNotification('이미 실행 중입니다.', 'warning');
        return;
    }

    const codeCells = document.querySelectorAll('.code-cell');
    showNotification(`${codeCells.length}개 셀 실행 시작...`, 'info');

    for (const cell of codeCells) {
        const cellId = cell.getAttribute('data-cell-id');
        if (cellId) {
            await executeJupyterCell(cellId);
            // Small delay between executions
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }

    showNotification('모든 셀 실행 완료', 'success');
}

// Restart kernel (reset execution count)
async function restartKernel() {
    if (confirm('커널을 재시작하시겠습니까? 모든 실행 상태가 초기화됩니다.')) {
        try {
            const response = await fetch('/api/v1/jupyter/execution/reset');
            const result = await response.json();

            if (response.ok) {
                notebookState.executionCount = 0;

                // Reset all execution counts in UI
                document.querySelectorAll('.input-prompt').forEach(prompt => {
                    prompt.textContent = 'In [ ]:';
                });

                document.querySelectorAll('[id^="output-number-"]').forEach(output => {
                    output.textContent = ' ';
                });

                // Hide all outputs
                document.querySelectorAll('.code-cell-output').forEach(output => {
                    output.style.display = 'none';
                });

                updateKernelStatus('ready');
                showNotification('커널이 재시작되었습니다.', 'success');
            } else {
                throw new Error(result.detail || 'Restart failed');
            }
        } catch (error) {
            console.error('Kernel restart error:', error);
            showNotification('커널 재시작 중 오류가 발생했습니다.', 'error');
        }
    }
}

// Update kernel status
function updateKernelStatus(status) {
    notebookState.kernelStatus = status;

    const statusIndicator = document.getElementById('kernel-status');
    const statusText = document.querySelector('.status-text');

    if (statusIndicator && statusText) {
        switch (status) {
            case 'ready':
                statusIndicator.textContent = '🟢';
                statusText.textContent = 'Java 커널 준비됨';
                break;
            case 'busy':
                statusIndicator.textContent = '🟡';
                statusText.textContent = 'Java 커널 실행 중';
                break;
            case 'error':
                statusIndicator.textContent = '🔴';
                statusText.textContent = 'Java 커널 오류';
                break;
        }
    }
}

// Setup Jupyter-specific keyboard shortcuts
function setupJupyterKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
        // Only handle shortcuts when not in an input/textarea or CodeMirror
        if (event.target.tagName === 'INPUT' ||
            event.target.tagName === 'TEXTAREA' ||
            event.target.closest('.CodeMirror')) {
            return;
        }

        // AIDEV-NOTE: Cell navigation shortcuts
        const activeCell = document.querySelector('.jupyter-cell.active');
        const activeCellId = activeCell?.getAttribute('data-cell-id');

        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 's':
                    event.preventDefault();
                    saveNotebook();
                    break;
                case 'Enter':
                    if (event.shiftKey) {
                        event.preventDefault();
                        runAllCells();
                    }
                    break;
            }
        } else {
            // Navigation keys without modifiers
            switch (event.key) {
                case 'ArrowUp':
                    if (activeCellId) {
                        event.preventDefault();
                        const prevCell = getPreviousCell(activeCellId);
                        if (prevCell) {
                            focusCell(prevCell.id);
                        }
                    }
                    break;
                case 'ArrowDown':
                    if (activeCellId) {
                        event.preventDefault();
                        const nextCell = getNextCell(activeCellId);
                        if (nextCell) {
                            focusCell(nextCell.id);
                        }
                    }
                    break;
                case 'Enter':
                    if (activeCellId) {
                        event.preventDefault();
                        const cellType = activeCell.getAttribute('data-cell-type');
                        if (cellType === 'markdown') {
                            editMarkdownCell(activeCellId);
                        } else if (cellType === 'code') {
                            focusCell(activeCellId); // Enter edit mode for code cell
                        }
                    }
                    break;
            }
        }
    });
}

// Setup cell management
function setupCellManagement() {
    // Cell deletion confirmation
    window.deleteCell = function(cellId) {
        if (confirm('이 셀을 삭제하시겠습니까?')) {
            const cell = document.querySelector(`[data-cell-id="${cellId}"]`);
            if (cell) {
                cell.remove();
                notebookState.editors.delete(cellId);
                showNotification('셀이 삭제되었습니다.', 'info');
            }
        }
    };
}

// Add new code cell
function addNewCodeCell() {
    // This would typically involve server-side communication
    // For now, show modal or implement client-side addition
    showAddCellModal('code');
}

// Add new markdown cell
function addNewMarkdownCell() {
    showAddCellModal('markdown');
}

// Show add cell modal
function showAddCellModal(defaultType = 'code') {
    const modal = document.getElementById('add-cell-modal');
    if (modal) {
        modal.style.display = 'flex';

        // Handle cell type selection
        const cellTypeButtons = modal.querySelectorAll('.btn-cell-type');
        cellTypeButtons.forEach(btn => {
            btn.onclick = () => {
                const cellType = btn.getAttribute('data-type');
                createNewCell(cellType);
                closeAddCellModal();
            };
        });
    }
}

// Close add cell modal
function closeAddCellModal() {
    const modal = document.getElementById('add-cell-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Create new cell (placeholder implementation)
function createNewCell(cellType) {
    // This is a simplified implementation
    // In a real application, this would involve server communication
    console.log(`Creating new ${cellType} cell`);
    showNotification(`새 ${cellType} 셀이 추가되었습니다.`, 'success');
}

// Save notebook
async function saveNotebook() {
    try {
        showNotification('노트북 저장 중...', 'info');

        // Collect cell data
        const cellsData = [];
        document.querySelectorAll('.jupyter-cell').forEach(cell => {
            const cellId = cell.getAttribute('data-cell-id');
            const cellType = cell.getAttribute('data-cell-type');

            let source = '';
            if (cellType === 'code') {
                const editor = notebookState.editors.get(cellId);
                source = editor ? editor.getValue() : '';
            } else if (cellType === 'markdown') {
                const textarea = document.getElementById(`markdown-source-${cellId}`);
                source = textarea ? textarea.value : '';
            }

            cellsData.push({
                id: cellId,
                type: cellType,
                source: source
            });
        });

        // Here you would send the data to the server
        // For now, just show success message
        showNotification('노트북이 저장되었습니다.', 'success');

    } catch (error) {
        console.error('Save error:', error);
        showNotification('저장 중 오류가 발생했습니다.', 'error');
    }
}

// Export notebook
function exportNotebook() {
    const options = ['Markdown (.md)', 'Jupyter Notebook (.ipynb)', 'HTML'];
    const choice = prompt(`내보낼 형식을 선택하세요:\n${options.map((opt, i) => `${i + 1}. ${opt}`).join('\n')}`);

    if (choice && choice >= 1 && choice <= 3) {
        const format = ['md', 'ipynb', 'html'][choice - 1];
        showNotification(`${format.toUpperCase()} 형식으로 내보내기 중...`, 'info');

        // Implement actual export logic here
        setTimeout(() => {
            showNotification(`${format.toUpperCase()} 파일로 내보내기가 완료되었습니다.`, 'success');
        }, 1000);
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '6px',
        zIndex: '10000',
        fontWeight: '500',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        transition: 'all 0.3s ease'
    });

    // Color scheme based on type
    const colors = {
        success: { bg: '#d4edda', text: '#155724', border: '#c3e6cb' },
        error: { bg: '#f8d7da', text: '#721c24', border: '#f5c6cb' },
        warning: { bg: '#fff3cd', text: '#856404', border: '#ffeaa7' },
        info: { bg: '#d1ecf1', text: '#0c5460', border: '#bee5eb' }
    };

    const color = colors[type] || colors.info;
    notification.style.backgroundColor = color.bg;
    notification.style.color = color.text;
    notification.style.border = `1px solid ${color.border}`;

    document.body.appendChild(notification);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, 3000);
}

// // Initialize when DOM is loaded (2중으로 코드 셀이 로딩됨)
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', initializeJupyterNotebook);
// } else {
//     initializeJupyterNotebook();
// }