// Copy the CONTEXT.md preview to the clipboard.
document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-copy-target]");
  if (!button) return;

  const preview = document.getElementById(button.dataset.copyTarget);
  const status = document.querySelector(".copy-status");
  const label = "Copy";

  try {
    await navigator.clipboard.writeText(preview.textContent);
    button.textContent = "Copied";
    if (status) status.textContent = "CONTEXT.md is on your clipboard.";
    setTimeout(() => {
      button.textContent = label;
    }, 2000);
  } catch (error) {
    // Clipboard blocked (non-HTTPS page or browser permission): select the text instead.
    const range = document.createRange();
    range.selectNodeContents(preview);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    if (status) status.textContent = "Press Ctrl+C (Cmd+C on a Mac) to copy the selected text.";
  }
});
