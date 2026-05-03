// src/utils/renderTextWithImages.jsx
import React from 'react';

export function parseGraphToken(token) {
    const match = token.match(/^\[GRAPH:([\d.]+):([\d.]+)x([\d.]+)cm\]$/);
    if (!match) return null;
    return {
        id: parseFloat(match[1]),
        widthCm: Math.max(1, parseFloat(match[2])),
        heightCm: Math.max(1, parseFloat(match[3])),
    };
}

export function renderGraphBlock(graphId, widthCm, heightCm, key, onRemove) {
    return (
        <span key={key} className="inline-block align-middle my-2 mx-1">
            <span className="relative inline-block group">
                <span
                    style={{
                        width: `${widthCm}cm`,
                        height: `${heightCm}cm`,
                        display: 'block',
                        border: '2px solid #0f766e',
                        borderRadius: 4,
                        boxSizing: 'border-box',
                        backgroundColor: 'white',
                        backgroundImage: [
                            'repeating-linear-gradient(to right,rgba(15,118,110,.18) 0,rgba(15,118,110,.18) 1px,transparent 1px,transparent 1mm)',
                            'repeating-linear-gradient(to bottom,rgba(15,118,110,.18) 0,rgba(15,118,110,.18) 1px,transparent 1px,transparent 1mm)',
                            'repeating-linear-gradient(to right,rgba(15,23,42,.42) 0,rgba(15,23,42,.42) 1px,transparent 1px,transparent 1cm)',
                            'repeating-linear-gradient(to bottom,rgba(15,23,42,.42) 0,rgba(15,23,42,.42) 1px,transparent 1px,transparent 1cm)',
                        ].join(','),
                    }}
                />
                {onRemove && (
                    <button
                        type="button"
                        onClick={() => onRemove(graphId)}
                        className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-xs font-bold z-10"
                    >✕</button>
                )}
            </span>
        </span>
    );
}

export function renderTextWithImages(
    text,
    images = [],
    imagePositions = {},
    answerLines = [],
    onRemoveImage = null,
    onRemoveLines = null,
    context = 'preview',
) {
    if (!text) return [];

    const findClosing = (str) => {
        let depth = 0;
        for (let i = 0; i < str.length; i++) {
            if (str[i] === '[') depth++;
            else if (str[i] === ']') {
                if (depth === 0) return i;
                depth--;
            }
        }
        return -1;
    };

    const splitByDelim = (content, delim = ':') => {
        const parts = [];
        let cur = '';
        let depth = 0;
        for (const ch of content) {
            if (ch === '[') { depth++; cur += ch; }
            else if (ch === ']') { depth--; cur += ch; }
            else if (ch === delim && depth === 0) { parts.push(cur); cur = ''; }
            else cur += ch;
        }
        if (cur) parts.push(cur);
        return parts;
    };

    const parseText = (str, base = 0) => {
        if (!str) return [];
        const results = [];
        let idx = 0;
        let kc = base;

        const startsPattern = (s) =>
            /^(\[TABLE:|\[MATRIX:|\[FRAC:|\[MIX:|\[SUP\]|\[SUB\]|\*\*|__|\*|_|\[LINES:|\[SPACE:|\[GRAPH:|\[IMAGE:)/.test(s);

        while (idx < str.length) {
            const rem = str.slice(idx);

            // TABLE
            if (rem.startsWith('[TABLE:')) {
                const cs = 7;
                const ci = findClosing(rem.slice(cs));
                if (ci !== -1) {
                    results.push(parseTable(rem.slice(cs, cs + ci), kc++));
                    idx += cs + ci + 1;
                    continue;
                }
            }

            // MATRIX
            if (rem.startsWith('[MATRIX:')) {
                const cs = 8;
                const ci = findClosing(rem.slice(cs));
                if (ci !== -1) {
                    results.push(parseMatrix(rem.slice(cs, cs + ci), kc++));
                    idx += cs + ci + 1;
                    continue;
                }
            }

            // FRAC
            if (rem.startsWith('[FRAC:')) {
                const cs = 6;
                const ci = findClosing(rem.slice(cs));
                if (ci !== -1) {
                    const parts = splitByDelim(rem.slice(cs, cs + ci));
                    if (parts.length === 2) {
                        results.push(
                            <span key={kc++} style={{ display: 'inline-block', verticalAlign: 'middle', textAlign: 'center', lineHeight: 1 }}>
                                <span style={{ display: 'block', fontSize: '0.85em' }}>{parseText(parts[0], kc * 1000)}</span>
                                <span style={{ display: 'block', borderTop: '1px solid', fontSize: '0.85em' }}>{parseText(parts[1], kc * 1000)}</span>
                            </span>
                        );
                        idx += cs + ci + 1;
                        continue;
                    }
                }
            }

            // MIX
            if (rem.startsWith('[MIX:')) {
                const cs = 5;
                const ci = findClosing(rem.slice(cs));
                if (ci !== -1) {
                    const parts = splitByDelim(rem.slice(cs, cs + ci));
                    if (parts.length === 3) {
                        results.push(
                            <span key={kc++} style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                                <span>{parseText(parts[0], kc * 1000)}</span>
                                <span style={{ display: 'inline-block', verticalAlign: 'middle', textAlign: 'center', lineHeight: 1 }}>
                                    <span style={{ display: 'block', fontSize: '0.85em' }}>{parseText(parts[1], kc * 1000)}</span>
                                    <span style={{ display: 'block', borderTop: '1px solid', fontSize: '0.85em' }}>{parseText(parts[2], kc * 1000)}</span>
                                </span>
                            </span>
                        );
                        idx += cs + ci + 1;
                        continue;
                    }
                }
            }

            // SUP
            if (rem.startsWith('[SUP]')) {
                const end = findMatchingClose(rem, '[SUP]', '[/SUP]');
                if (end !== -1) {
                    results.push(<sup key={kc++} className="text-sm">{parseText(rem.slice(5, end), kc * 1000)}</sup>);
                    idx += end + 6;
                    continue;
                }
            }

            // SUB
            if (rem.startsWith('[SUB]')) {
                const end = findMatchingClose(rem, '[SUB]', '[/SUB]');
                if (end !== -1) {
                    results.push(<sub key={kc++} className="text-sm">{parseText(rem.slice(5, end), kc * 1000)}</sub>);
                    idx += end + 6;
                    continue;
                }
            }

            // BOLD **
            if (rem.startsWith('**')) {
                const end = findDelim(rem, '**', 2);
                if (end !== -1) {
                    results.push(<strong key={kc++}>{parseText(rem.slice(2, end), kc * 1000)}</strong>);
                    idx += end + 2;
                    continue;
                }
            }

            // UNDERLINE __
            if (rem.startsWith('__')) {
                const end = findDelim(rem, '__', 2);
                if (end !== -1) {
                    results.push(<u key={kc++}>{parseText(rem.slice(2, end), kc * 1000)}</u>);
                    idx += end + 2;
                    continue;
                }
            }

            // ITALIC *
            if (rem.startsWith('*') && !rem.startsWith('**')) {
                const end = findDelim(rem, '*', 1);
                if (end !== -1) {
                    results.push(<em key={kc++}>{parseText(rem.slice(1, end), kc * 1000)}</em>);
                    idx += end + 1;
                    continue;
                }
            }

            // LINES
            const linesM = rem.match(/^\[LINES:([\d.]+)\]/);
            if (linesM) {
                results.push(renderLines(parseFloat(linesM[1]), kc++, answerLines, onRemoveLines));
                idx += linesM[0].length;
                continue;
            }

            // SPACE
            const spaceM = rem.match(/^\[SPACE:([\d.]+)\]/);
            if (spaceM) {
                results.push(renderSpace(parseFloat(spaceM[1]), kc++));
                idx += spaceM[0].length;
                continue;
            }

            // GRAPH
            const graphM = rem.match(/^\[GRAPH:([\d.]+):([\d.]+)x([\d.]+)cm\]/);
            if (graphM) {
                const gd = parseGraphToken(graphM[0]);
                if (gd) {
                    results.push(renderGraphBlock(gd.id, gd.widthCm, gd.heightCm, kc++));
                    idx += graphM[0].length;
                    continue;
                }
            }

            // IMAGE
            const imgNew = rem.match(/^\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
            const imgOld = rem.match(/^\[IMAGE:([\d.]+):(\d+)px\]/);
            if (imgNew || imgOld) {
                const m = imgNew || imgOld;
                results.push(renderImage(m, kc++, images, imagePositions, onRemoveImage, context));
                idx += m[0].length;
                continue;
            }

            // plain text
            let plain = '';
            while (idx < str.length && !startsPattern(str.slice(idx))) {
                plain += str[idx++];
            }
            if (plain) results.push(<span key={kc++}>{plain}</span>);
        }
        return results;
    };

    const findMatchingClose = (str, open, close) => {
        let depth = 1, i = open.length;
        while (i < str.length && depth > 0) {
            if (str.slice(i).startsWith(open)) { depth++; i += open.length; }
            else if (str.slice(i).startsWith(close)) { depth--; if (depth === 0) return i; i += close.length; }
            else i++;
        }
        return -1;
    };

    const findDelim = (str, delim, offset) => {
        let i = offset;
        while (i < str.length) {
            if (str.slice(i).startsWith(delim)) return i;
            i++;
        }
        return -1;
    };

    const parseTable = (inner, key) => {
        try {
            const parts = splitByDelim(inner);
            const dm = parts[0].match(/(\d+)x(\d+)/);
            if (!dm) return <span key={key}>{`[TABLE:${inner}]`}</span>;
            const rows = +dm[1], cols = +dm[2];
            let cells = [];
            if (parts[1]) {
                let cur = '', d = 0;
                for (const ch of parts[1]) {
                    if (ch === '[') { d++; cur += ch; }
                    else if (ch === ']') { d--; cur += ch; }
                    else if (ch === '|' && d === 0) { cells.push(cur); cur = ''; }
                    else cur += ch;
                }
                if (cur) cells.push(cur);
            }
            const wi = parts.findIndex(p => p === 'W');
            const hi = parts.findIndex(p => p === 'H');
            const mi = parts.findIndex(p => p === 'M');
            const colWidths = wi !== -1 ? splitByDelim(parts[wi + 1] || '', ',').map(w => +w || 60) : Array(cols).fill(60);
            const rowHeights = hi !== -1 ? splitByDelim(parts[hi + 1] || '', ',').map(h => +h || 30) : Array(rows).fill(30);
            let merged = {};
            if (mi !== -1) {
                splitByDelim(parts[mi + 1] || '', ';').forEach(m => {
                    const [r, c, cs, rs] = splitByDelim(m, ',').map(Number);
                    if (!merged[r]) merged[r] = {};
                    merged[r][c] = { colspan: cs, rowspan: rs };
                });
            }
            const isMerged = (r, c) => {
                for (let rr = 0; rr <= r; rr++) for (let cc = 0; cc <= c; cc++) {
                    const cell = merged[rr]?.[cc];
                    if (cell && (cell.colspan > 1 || cell.rowspan > 1)) {
                        if (r >= rr && r <= rr + (cell.rowspan || 1) - 1 && c >= cc && c <= cc + (cell.colspan || 1) - 1) {
                            if (rr === r && cc === c) return false;
                            return true;
                        }
                    }
                }
                return false;
            };
            return (
                <table key={key} style={{ border: '1px solid #000', borderCollapse: 'collapse', margin: '8px 0', display: 'inline-table' }}>
                    <tbody>
                        {[...Array(rows)].map((_, r) => (
                            <tr key={r}>
                                {[...Array(cols)].map((_, c) => {
                                    if (isMerged(r, c)) return null;
                                    const ci = r * cols + c;
                                    const mi2 = merged[r]?.[c] || { colspan: 1, rowspan: 1 };
                                    return (
                                        <td key={c} colSpan={mi2.colspan} rowSpan={mi2.rowspan}
                                            style={{ border: '1px solid #000', padding: 8, width: colWidths[c], height: rowHeights[r], minWidth: 60, minHeight: 30 }}>
                                            {parseText(cells[ci] || '', key * 10000 + ci * 100)}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            );
        } catch { return <span key={key}>{`[TABLE:${inner}]`}</span>; }
    };

    const parseMatrix = (inner, key) => {
        try {
            const parts = splitByDelim(inner);
            const dm = parts[0].match(/(\d+)x(\d+)/);
            if (!dm) return <span key={key}>{`[MATRIX:${inner}]`}</span>;
            const rows = +dm[1], cols = +dm[2];
            let cells = [];
            if (parts[1]) {
                let cur = '', d = 0;
                for (const ch of parts[1]) {
                    if (ch === '[') { d++; cur += ch; }
                    else if (ch === ']') { d--; cur += ch; }
                    else if (ch === '|' && d === 0) { cells.push(cur); cur = ''; }
                    else cur += ch;
                }
                if (cur) cells.push(cur);
            }
            return (
                <span key={key} style={{ display: 'inline-flex', alignItems: 'center', margin: '8px 4px', fontSize: '1.2em' }}>
                    <span style={{ fontSize: '2em', lineHeight: 1 }}>⎡</span>
                    <table style={{ borderCollapse: 'collapse', margin: '0 4px' }}>
                        <tbody>
                            {[...Array(rows)].map((_, r) => (
                                <tr key={r}>
                                    {[...Array(cols)].map((_, c) => (
                                        <td key={c} style={{ padding: '4px 8px', textAlign: 'center', minWidth: 40 }}>
                                            {parseText(cells[r * cols + c] || '', key * 10000 + (r * cols + c) * 100)}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <span style={{ fontSize: '2em', lineHeight: 1 }}>⎤</span>
                </span>
            );
        } catch { return <span key={key}>{`[MATRIX:${inner}]`}</span>; }
    };

    const renderLines = (lineId, key, lines, onRemove) => {
        const cfg = lines.find(l => l.id === lineId);
        if (!cfg) return (
            <div key={key} className="my-2 p-3 bg-yellow-50 border-2 border-dashed border-yellow-400 rounded text-xs text-yellow-800">
                Answer Lines (config missing — ID: {lineId.toFixed(0)})
            </div>
        );
        const full = Math.floor(cfg.numberOfLines);
        const half = cfg.numberOfLines % 1 !== 0;
        return (
            <div key={key} className="my-2 relative group" style={{ maxWidth: 700 }}>
                {[...Array(full)].map((_, i) => (
                    <div key={i} style={{ height: cfg.lineHeight, borderBottom: `2px ${cfg.lineStyle} rgba(0,0,0,${cfg.opacity})`, width: '100%' }} />
                ))}
                {half && <div style={{ height: cfg.lineHeight / 2, borderBottom: `2px ${cfg.lineStyle} rgba(0,0,0,${cfg.opacity})`, width: '100%' }} />}
                {onRemove && (
                    <button type="button" onClick={() => onRemove(lineId)}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-xs z-10">
                        ✕
                    </button>
                )}
            </div>
        );
    };

    const renderSpace = (spaceId, key) => (
        <div key={key} className="my-2" style={{ maxWidth: 700 }}>
            <div style={{ height: 189, width: '100%', background: 'white' }} />
        </div>
    );

    const renderImage = (match, key, imgs, positions, onRemove, ctx) => {
        const isNew = match[0].match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
        const id = parseFloat(isNew ? isNew[1] : match[1]);
        const w = parseInt(isNew ? isNew[2] : match[2]);
        const h = isNew ? parseInt(isNew[3]) : null;
        const img = imgs.find(i => Math.abs(i.id - id) < 0.001);
        const pos = positions[id];

        if (!img) return (
            <div key={key} className="my-2 p-4 bg-red-50 border-2 border-dashed border-red-300 rounded inline-block">
                <p className="text-sm text-red-800 font-medium">Image Not Found (ID: {id.toFixed(0)})</p>
            </div>
        );

        return (
            <span key={key}
                className={pos ? 'absolute z-10' : 'inline-block align-middle my-2 mx-1'}
                style={pos ? { left: pos.x, top: pos.y } : {}}>
                <span className="relative inline-block group">
                    <img src={img.url} alt={img.name || 'image'}
                        style={{ width: w, height: h || 'auto', maxWidth: ctx === 'similar' ? 200 : '100%', display: 'block' }}
                        className="border-2 border-blue-400 rounded shadow-sm select-none" />
                    {onRemove && (
                        <button type="button" onClick={() => onRemove(id)}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-xs z-10">
                            ✕
                        </button>
                    )}
                </span>
            </span>
        );
    };

    return parseText(text, 0);
}