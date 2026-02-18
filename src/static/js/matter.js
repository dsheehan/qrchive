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

function showQRCode(code, product, precomputedQR, skipPushState = false, maximized = null) {
    currentCode = code;
    currentProduct = product;
    currentPrecomputedQR = precomputedQR;

    const modal = document.getElementById("qrModal");
    const modalContent = document.getElementById("modalContent");
    const qrcodeDiv = document.getElementById("qrcode");
    const productTitle = document.getElementById("productTitle");
    const codeText = document.getElementById("pairingCodeText");

    // Reset maximized state when opening a new QR code (or keep it?)
    // Let's reset it for consistency unless it's a popstate/load
    if (!skipPushState) {
        isMaximized = maximized !== null ? maximized : false;
    } else if (maximized !== null) {
        isMaximized = maximized;
    }

    if (isMaximized) {
        modalContent.classList.add("maximized");
        document.getElementById("maximizeBtn").innerHTML = "&#10529;"; // Restore (diagonal inwards)
    } else {
        modalContent.classList.remove("maximized");
        document.getElementById("maximizeBtn").innerHTML = "&#10530;"; // Maximize (diagonal outwards)
    }

    // Use precomputed QR if available, otherwise generate on the fly
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
    
    modal.style.display = "block";

    const size = isMaximized ? Math.min(window.innerWidth, window.innerHeight) * 0.7 : 200;

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
    const modal = document.getElementById("qrModal");
    if (modal) {
        modal.style.display = "none";
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
    const modal = document.getElementById("qrModal");
    if (event.target == modal) {
        closeModal();
    }
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
            const modal = document.getElementById("qrModal");
            if (modal && modal.style.display === "block") {
                modal.style.display = "none";
            }
        }
    }
});
