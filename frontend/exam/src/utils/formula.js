export function createFormulaToken({ superscriptBefore = '', subscriptBefore = '', mainText = '', superscriptAfter = '', subscriptAfter = '' }) {
    return `[FORMULA:${[
        superscriptBefore,
        subscriptBefore,
        mainText,
        superscriptAfter,
        subscriptAfter,
    ].map(value => encodeURIComponent(value.trim())).join('|')}]`;
}

export function parseFormulaToken(token) {
    if (!token.startsWith('[FORMULA:') || !token.endsWith(']')) return null;
    const values = token.slice(9, -1).split('|');
    if (values.length !== 5) return null;

    try {
        const [superscriptBefore, subscriptBefore, mainText, superscriptAfter, subscriptAfter] = values.map(decodeURIComponent);
        if (!mainText) return null;
        return { superscriptBefore, subscriptBefore, mainText, superscriptAfter, subscriptAfter };
    } catch {
        return null;
    }
}
