() => {
    const printPages = Array.from(document.querySelectorAll('.print-page'));
    const yTolerance = 8;

    if (!printPages.length) {
        return [];
    }

    return printPages.map((printPage) => {
        const pageItems = Array.from(printPage.querySelectorAll('.device-card-col'))
            .map((el) => {
                const r = el.getBoundingClientRect();
                return { top: r.top, left: r.left };
            })
            .sort((a, b) => a.top - b.top || a.left - b.left);

        const rows = [];

        for (const item of pageItems) {
            let row = rows.find((r) => Math.abs(r.y - item.top) <= yTolerance);
            if (!row) {
                row = { y: item.top, xs: [] };
                rows.push(row);
            }
            row.xs.push(item.left);
        }

        return rows.map((row) => row.xs.length);
    });
}