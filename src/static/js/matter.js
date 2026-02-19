// Simple Bootstrap-compatible theme toggle with persistence
(function() {
    const html = document.documentElement;
    const storageKey = 'theme';
    // Initialize theme from localStorage or system preference
    function getPreferredTheme() {
        const saved = localStorage.getItem(storageKey);
        if (saved === 'light' || saved === 'dark') return saved;
        // fallback to current attribute or system
        if (html.getAttribute('data-bs-theme')) return html.getAttribute('data-bs-theme');
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    function setTheme(t) {
        html.setAttribute('data-bs-theme', t);
        localStorage.setItem(storageKey, t);
    }
    window.toggleTheme = function() {
        const current = html.getAttribute('data-bs-theme') || getPreferredTheme();
        setTheme(current === 'dark' ? 'light' : 'dark');
    }
    // Apply on load
    setTheme(getPreferredTheme());
    // Keep in sync with OS changes when no explicit preference stored
    if (!localStorage.getItem(storageKey) && window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            setTheme(e.matches ? 'dark' : 'light');
        });
    }
})();

const BASE38_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ -.";

function encodeBase38(val) {
    let res = "";
    while (val > 0n) {
        res += BASE38_CHARS[Number(val % 38n)];
        val /= 38n;
    }
    return res;
}

function formatMatterQR(pairingCode) {
    // Remove dashes
    const digits = pairingCode.replace(/-/g, "");
    if (digits.length !== 11) return pairingCode;

    const passcode = parseInt(digits, 10);
    
    // Default values if not provided
    const version = 0;
    const vendorId = 0xFFF1; // Test VID
    const productId = 0x8000; // Test PID
    const commissioningFlow = 0; // Standard
    const discoveryCapabilities = 2; // BLE
    const discriminator = 3840; // Default

    // Matter QR Code Bit Layout (LSB first):
    // 0-2: Version (3 bits)
    // 3-14: Discriminator (12 bits)
    // 15-41: Passcode (27 bits)
    // 42-43: Commissioning Flow (2 bits)
    // 44-51: Discovery Capabilities (8 bits)
    // 52-67: Vendor ID (16 bits)
    // 68-83: Product ID (16 bits)
    // Total: 84 bits

    let val = 0n;
    val |= BigInt(version & 0x7);
    val |= BigInt(discriminator & 0xFFF) << 3n;
    val |= BigInt(passcode & 0x7FFFFFF) << 15n;
    val |= BigInt(commissioningFlow & 0x3) << 42n;
    val |= BigInt(discoveryCapabilities & 0xFF) << 44n;
    val |= BigInt(vendorId & 0xFFFF) << 52n;
    val |= BigInt(productId & 0xFFFF) << 68n;

    return "MT:" + encodeBase38(val);
}

let qrCode;
let isMaximized = false;
let currentCode, currentProduct, currentPrecomputedQR;
let bootstrapModal;

function showQRCode(code, product, precomputedQR, skipPushState = false, maximized = null) {
    currentCode = code;
    currentProduct = product;
    currentPrecomputedQR = precomputedQR;

    const modalEl = document.getElementById("qrModal");
    const modalDialog = document.getElementById("modalDialog");
    const qrcodeDiv = document.getElementById("qrcode");
    const productTitle = document.getElementById("productTitle");
    const codeText = document.getElementById("pairingCodeText");

    if (!bootstrapModal) {
        bootstrapModal = new bootstrap.Modal(modalEl);
    }

    if (!skipPushState) {
        isMaximized = maximized !== null ? maximized : false;
    } else if (maximized !== null) {
        isMaximized = maximized;
    }

    if (isMaximized) {
        modalDialog.classList.add("modal-fullscreen");
        document.getElementById("maximizeBtn").innerHTML = '<i class="fa-solid fa-down-left-and-up-right-to-center"></i>'; // Restore/Minimize
        document.getElementById("maximizeBtn").title = "Restore";
    } else {
        modalDialog.classList.remove("modal-fullscreen");
        document.getElementById("maximizeBtn").innerHTML = '<i class="fa-solid fa-up-right-and-down-left-from-center"></i>'; // Maximize
        document.getElementById("maximizeBtn").title = "Maximize";
    }

    const matterCode = precomputedQR || formatMatterQR(code);

    if (productTitle) {
        productTitle.innerText = product;
    }
    codeText.innerText = "Setup Code: " + code; 
    const matterText = document.getElementById("matterCodeText");
    if (matterText) {
        matterText.innerText = "QR Data: " + matterCode;
    }
    qrcodeDiv.innerHTML = "";
    
    bootstrapModal.show();

    const size = isMaximized ? Math.min(window.innerWidth, window.innerHeight) * 0.7 : 250;

    qrCode = new QRCodeStyling({
        width: size,
        height: size,
        type: "canvas",
        data: matterCode,
        dotsOptions: {
            color: "#000000",
            type: "square"
        },
        backgroundOptions: {
            color: "#ffffff",
        },
        qrOptions: {
            errorCorrectionLevel: "H"
        }
    });

    qrCode.append(qrcodeDiv);

    if (!skipPushState) {
        const params = new URLSearchParams(window.location.search);
        params.set("code", code);
        params.set("product", product);
        if (precomputedQR) {
            params.set("qr", precomputedQR);
        } else {
            params.delete("qr");
        }
        if (isMaximized) {
            params.set("maximized", "true");
        } else {
            params.delete("maximized");
        }
        const newUrl = window.location.pathname + "?" + params.toString();
        window.history.pushState({ code, product, qr: precomputedQR, maximized: isMaximized }, "", newUrl);
    }
}

function toggleMaximize() {
    isMaximized = !isMaximized;
    
    // Update URL and history state
    if (currentCode) {
        const params = new URLSearchParams(window.location.search);
        if (isMaximized) {
            params.set("maximized", "true");
        } else {
            params.delete("maximized");
        }
        const newUrl = window.location.pathname + "?" + params.toString();
        window.history.pushState({ code: currentCode, product: currentProduct, qr: currentPrecomputedQR, maximized: isMaximized }, "", newUrl);
        
        // Re-render QR code with new size
        showQRCode(currentCode, currentProduct, currentPrecomputedQR, true, isMaximized);
    }
}

function closeModal() {
    if (bootstrapModal) {
        bootstrapModal.hide();
    }
    const params = new URLSearchParams(window.location.search);
    if (params.has("code") || params.has("product") || params.has("qr") || params.has("maximized")) {
        params.delete("code");
        params.delete("product");
        params.delete("qr");
        params.delete("maximized");
        const search = params.toString();
        const newUrl = window.location.pathname + (search ? "?" + search : "");
        window.history.pushState({}, "", newUrl);
    }
}

window.onclick = function(event) {
    // Bootstrap handles closing on backdrop click
}

function checkUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const product = params.get("product");
    const qr = params.get("qr");
    const maximized = params.get("maximized") === "true";
    if (code && product) {
        showQRCode(code, product, qr, true, maximized);
    }
}

window.addEventListener("load", checkUrlParams);
window.addEventListener("popstate", (event) => {
    if (event.state && event.state.code && event.state.product) {
        showQRCode(event.state.code, event.state.product, event.state.qr, true, event.state.maximized);
    } else {
        const params = new URLSearchParams(window.location.search);
        const code = params.get("code");
        const product = params.get("product");
        const qr = params.get("qr");
        const maximized = params.get("maximized") === "true";
        if (code && product) {
            showQRCode(code, product, qr, true, maximized);
        } else {
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        }
    }
});

// ---- Advanced table features: filtering, sorting, column hiding ----
(function(){
    function getTable() {
        return document.getElementById('devicesTable');
    }
    function getHeaderCells(table){
        return table ? table.tHead.querySelectorAll('th[data-col-index]') : [];
    }
    function getBodyRows(table){
        return table ? table.tBodies[0].rows : [];
    }
    function isColumnVisible(idx){
        const cb = document.getElementById('col-toggle-' + idx);
        return !cb || cb.checked; // default visible if control missing
    }
    function applyColumnVisibility(){
        const table = getTable();
        if (!table) return;
        const headers = getHeaderCells(table);
        headers.forEach((th)=>{
            const idx = parseInt(th.getAttribute('data-col-index'));
            const show = isColumnVisible(idx);
            th.style.display = show ? '' : 'none';
        });
        const rows = getBodyRows(table);
        Array.from(rows).forEach((tr)=>{
            Array.from(tr.cells).forEach((td, i)=>{
                // last column is QR Code button; do not control it here
                if (i < headers.length) {
                    const show = isColumnVisible(i);
                    td.style.display = show ? '' : 'none';
                }
            });
        });
    }
    function normalize(val){
        return (val||'').toString().trim();
    }
    function cmp(a,b){
        const an = parseFloat(a); const bn = parseFloat(b);
        const aNum = !isNaN(an) && a.match(/^[-+]?\d+(?:\.\d+)?$/);
        const bNum = !isNaN(bn) && b.match(/^[-+]?\d+(?:\.\d+)?$/);
        if (aNum && bNum) return an - bn;
        return a.localeCompare(b, undefined, { sensitivity: 'base', numeric: true });
    }
    function clearSortIndicators(table){
        getHeaderCells(table).forEach(th=>{
            th.setAttribute('aria-sort','none');
            const icon = th.querySelector('i.fa-solid');
            if (icon){ icon.classList.remove('fa-sort-up','fa-sort-down'); icon.classList.add('fa-sort'); }
        });
    }
    function setSortIndicator(th, asc){
        th.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
        const icon = th.querySelector('i.fa-solid');
        if (icon){ icon.classList.remove('fa-sort'); icon.classList.add(asc ? 'fa-sort-up' : 'fa-sort-down'); }
    }
    function sortTableByColumn(table, column, asc){
        const tbody = table.tBodies[0];
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort((r1, r2)=>{
            const c1 = normalize((r1.cells[column] || {}).innerText || '');
            const c2 = normalize((r2.cells[column] || {}).innerText || '');
            const res = cmp(c1, c2);
            return asc ? res : -res;
        });
        rows.forEach(r=>tbody.appendChild(r));
    }
    function applyGlobalFilter(){
        const table = getTable();
        if (!table) return;
        const q = (document.getElementById('globalFilter')?.value || '').toLowerCase().trim();
        const words = q.split(/\s+/).filter(w => w.length > 0);
        const headers = getHeaderCells(table);
        const rows = getBodyRows(table);
        
        Array.from(rows).forEach(tr=>{
            let match = true;
            if (words.length > 0) {
                // For each word, we must find it in at least one visible column
                for (const word of words) {
                    let wordFound = false;
                    for (let i=0; i<headers.length; i++) {
                        if (!isColumnVisible(i)) continue;
                        const text = (tr.cells[i]?.innerText || '').toLowerCase();
                        if (text.includes(word)) {
                            wordFound = true;
                            break;
                        }
                    }
                    if (!wordFound) {
                        match = false;
                        break;
                    }
                }
            }
            tr.style.display = match ? '' : 'none';
        });
    }
    function bindSorting(){
        const table = getTable();
        if (!table) return;
        const headers = getHeaderCells(table);
        const state = {};
        headers.forEach((th)=>{
            const idx = parseInt(th.getAttribute('data-col-index'));
            function activate(){
                const asc = !(state[idx] === true); // toggle
                clearSortIndicators(table);
                sortTableByColumn(table, idx, asc);
                setSortIndicator(th, asc);
                state[idx] = asc;
            }
            th.addEventListener('click', activate);
            th.addEventListener('keypress', (e)=>{ if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); }});
        });
    }
    function bindColumnToggles(){
        const toggles = document.querySelectorAll('.column-toggle');
        toggles.forEach(cb=>{
            cb.addEventListener('change', ()=>{
                applyColumnVisibility();
                applyGlobalFilter();
            });
        });
    }
    function bindFilter(){
        const input = document.getElementById('globalFilter');
        if (input){ input.addEventListener('input', applyGlobalFilter); }
    }
    function init(){
        applyColumnVisibility();
        bindSorting();
        bindColumnToggles();
        bindFilter();
    }
    if (document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
