() => {
    const allItems = Array.from(document.querySelectorAll('.print-page .device-card-col'));
    if (!allItems.length) {
        return [];
    }

    const yTolerance = 8;
    const inchPx = 96;
    const pageHeightPx = 11 * inchPx;
    const pageMarginPx = 0.35 * inchPx;
    const printableHeightPx = pageHeightPx - (2 * pageMarginPx);

    const buckets = new Map();

    for (const el of allItems) {
        const r = el.getBoundingClientRect();
        const physicalPageIndex = Math.max(0, Math.floor(r.top / printableHeightPx));

        if (!buckets.has(physicalPageIndex)) {
            buckets.set(physicalPageIndex, []);
        }
        buckets.get(physicalPageIndex).push({ top: r.top, left: r.left });
    }

    const maxPageIndex = Math.max(...Array.from(buckets.keys()));
    const result = [];

    for (let pageIndex = 0; pageIndex <= maxPageIndex; pageIndex++) {
        const items = (buckets.get(pageIndex) || [])
            .slice()
            .sort((a, b) => a.top - b.top || a.left - b.left);

        if (!items.length) {
            result.push([]);
            continue;
        }

        const rows = [];
        for (const item of items) {
            let row = rows.find((r) => Math.abs(r.y - item.top) <= yTolerance);
            if (!row) {
                row = { y: item.top, xs: [] };
                rows.push(row);
            }
            row.xs.push(item.left);
        }
        result.push(rows.map((row) => row.xs.length));
    }

    return result;
}