function copyToClipboard(text, appName) {
    // Use the modern clipboard API
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification(`Description for "${appName}" copied to clipboard!`);
            updateCopiedCount();
        }).catch(err => {
            console.error('Failed to copy: ', err);
            fallbackCopyTextToClipboard(text, appName);
        });
    } else {
        fallbackCopyTextToClipboard(text, appName);
    }
}

function fallbackCopyTextToClipboard(text, appName) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showNotification(`Description for "${appName}" copied to clipboard!`);
            updateCopiedCount();
        } else {
            showNotification('Failed to copy to clipboard');
        }
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
        showNotification('Failed to copy to clipboard');
    }
    
    document.body.removeChild(textArea);
}

function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

function updateCopiedCount() {
    const countElement = document.getElementById('copied-count');
    const currentCount = parseInt(countElement.textContent) || 0;
    countElement.textContent = currentCount + 1;
}

function refreshApplications() {
    const refreshBtn = document.getElementById('refresh-btn');
    const originalText = refreshBtn.textContent;
    
    // Disable button and show loading state
    refreshBtn.disabled = true;
    refreshBtn.textContent = '🔄 Refreshing...';
    
    // Show the status modal
    showStatusModal();
    
    // Start streaming the refresh process
    const eventSource = new EventSource('/refresh-applications-stream');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.type === 'output') {
            addStatusLine(data.message);
        } else if (data.type === 'success') {
            addStatusLine('✅ ' + data.message);
            showNotification(data.message);
            eventSource.close();
            
            // Enable close button
            document.getElementById('close-btn').style.display = 'inline-block';
            
            // Reload the page after a delay
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else if (data.type === 'error') {
            addStatusLine('❌ ' + data.message);
            showNotification('Error: ' + data.message);
            eventSource.close();
            
            // Enable close button
            document.getElementById('close-btn').style.display = 'inline-block';
            
            // Reset button
            refreshBtn.disabled = false;
            refreshBtn.textContent = originalText;
        }
    };
    
    eventSource.onerror = function() {
        addStatusLine('❌ Connection error');
        showNotification('Error: Connection lost');
        eventSource.close();
        
        // Enable close button
        document.getElementById('close-btn').style.display = 'inline-block';
        
        // Reset button
        refreshBtn.disabled = false;
        refreshBtn.textContent = originalText;
    };
}

function showStatusModal() {
    document.getElementById('status-modal').style.display = 'block';
    document.getElementById('status-output').innerHTML = '<div class="status-line">Starting refresh process...</div>';
    document.getElementById('close-btn').style.display = 'none';
}

function closeStatusModal() {
    document.getElementById('status-modal').style.display = 'none';
}

function addStatusLine(message) {
    const output = document.getElementById('status-output');
    const line = document.createElement('div');
    line.className = 'status-line';
    line.textContent = message;
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
}

// Add search functionality and copy event listeners
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input');
    const gridRows = document.querySelectorAll('.applications-grid .grid-row');
    
    // Add copy functionality for clickable descriptions
    document.querySelectorAll('.app-description.copyable').forEach(element => {
        element.addEventListener('click', function() {
            const description = this.getAttribute('data-description');
            const appName = this.getAttribute('data-app-name');
            copyToClipboard(description, appName);
        });
    });
    
    // Add copy functionality for copy buttons
    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', function() {
            const description = this.getAttribute('data-description');
            const appName = this.getAttribute('data-app-name');
            copyToClipboard(description, appName);
        });
    });
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        gridRows.forEach(row => {
            // Skip the header row
            if (row.querySelector('.grid-header')) {
                return;
            }
            
            const appName = row.querySelector('.app-name').textContent.toLowerCase();
            const description = row.querySelector('.app-description').textContent.toLowerCase();
            
            if (appName.includes(searchTerm) || description.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}); 