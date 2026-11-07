console.log("ApplyPilot AI Content Script Loaded");

// Types
interface ScannedField {
    id: string;
    name: string;
    type: string;
    label: string;
    options?: string[];
    value: string;
}

function getLabelForElement(element: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement): string {
    // 1. Check associated label by ID
    if (element.id) {
        const labelElem = document.querySelector(`label[for="${element.id}"]`);
        if (labelElem && labelElem.textContent) {
            return labelElem.textContent.trim();
        }
    }
    
    // 2. Check aria-label / accessible name
    if (element.getAttribute("aria-label")) {
        return element.getAttribute("aria-label")!.trim();
    }
    
    // 3. Check placeholder
    if (element.placeholder) {
        return element.placeholder.trim();
    }
    
    // 4. Check nearby preceding text nodes (simplified for MVP)
    const previousSibling = element.previousSibling;
    if (previousSibling && previousSibling.nodeType === Node.TEXT_NODE) {
        return (previousSibling.textContent || "").trim();
    }

    return element.name || "Unknown Field";
}

function scanForms(): ScannedField[] {
    const fields: ScannedField[] = [];
    const ignoreTypes = ['password', 'hidden', 'submit', 'button', 'reset', 'file', 'image'];
    
    // Scan standard inputs
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach((el, index) => {
        const element = el as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
        
        if (element.tagName === 'INPUT' && ignoreTypes.includes(element.type)) {
            return;
        }
        
        const label = getLabelForElement(element);
        let options: string[] | undefined = undefined;
        
        if (element.tagName === 'SELECT') {
            options = Array.from((element as HTMLSelectElement).options).map(o => o.value);
        }

        fields.push({
            id: element.id || `applypilot_field_${index}`,
            name: element.name,
            type: element.type,
            label: label,
            options: options,
            value: element.value
        });
        
        // Tag the element so we can find it later to fill
        if (!element.id) {
            element.dataset.applypilotId = `applypilot_field_${index}`;
        }
    });

    console.log("ApplyPilot AI Form Scanner found fields:", fields);
    return fields;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "SCAN_FORM") {
        const fields = scanForms();
        sendResponse({ fields });
    }
});
