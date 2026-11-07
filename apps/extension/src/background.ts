console.log("ApplyPilot AI Background Service Worker Loaded");

chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed");
});

// Example background listener
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "MATCH_FIELDS") {
        // Here we would call the backend API /api/v1/forms/match
        console.log("Mocking backend matching...");
        setTimeout(() => {
            sendResponse({ matched: true, message: "Matched 5 fields" });
        }, 1000);
        return true; // Keep channel open for async response
    }
});
