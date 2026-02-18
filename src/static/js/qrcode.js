let qrCode;

function generateQRCode() {
    const textElement = document.getElementById("text");
    if (!textElement) return;

    const text = textElement.value.trim();

    // Input validation
    if (!text) {
        alert("Please enter some text or a URL.");
        return;
    }

    // Clear previous QR code
    const qrcodeDiv = document.getElementById("qrcode");
    if (qrcodeDiv) {
        qrcodeDiv.innerHTML = "";
    } else {
        return;
    }

    try {
        qrCode = new QRCodeStyling({
            width: 200,
            height: 200,
            type: "canvas",
            data: text,
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
    } catch (err) {
        console.error("QR Code generation failed:", err);
        alert("Error generating QR code. Please try again.");
    }
}
