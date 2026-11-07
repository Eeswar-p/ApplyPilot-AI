document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('scan-btn') as HTMLButtonElement;
    const statusDiv = document.getElementById('status') as HTMLDivElement;
    const fieldList = document.getElementById('field-list') as HTMLDivElement;

    scanBtn.addEventListener('click', async () => {
        statusDiv.textContent = "Scanning page...";
        fieldList.style.display = 'none';
        fieldList.innerHTML = '';

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab.id) throw new Error("No active tab");

            // Execute content script if not already loaded (for robust dev experience)
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['content.js']
                });
            } catch (e) {
                // Ignore error if already loaded
            }

            const response = await chrome.tabs.sendMessage(tab.id, { action: "SCAN_FORM" });
            
            if (response && response.fields) {
                statusDiv.textContent = `Found ${response.fields.length} form fields.`;
                fieldList.style.display = 'block';
                
                response.fields.forEach((field: any) => {
                    const div = document.createElement('div');
                    div.className = 'field-item';
                    div.innerHTML = `
                        <span style="font-weight: 500">${field.label || 'Unknown'}</span>
                        <span style="color: #64748b; font-size: 11px;">${field.type}</span>
                    `;
                    fieldList.appendChild(div);
                });
                
                // Trigger background matching logic
                chrome.runtime.sendMessage({ action: "MATCH_FIELDS", fields: response.fields }, (bgResponse) => {
                    console.log("Matching result:", bgResponse);
                });

            } else {
                statusDiv.textContent = "No fields found or error scanning.";
            }
        } catch (error) {
            console.error(error);
            statusDiv.textContent = "Cannot scan this page (likely restricted).";
        }
    });
});
