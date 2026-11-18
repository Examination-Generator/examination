export function createFormulaToken({ superscriptBefore = '', subscriptBefore = '', mainText = '', superscriptAfter = '', subscriptAfter = '', squareRoot = false }) {
    return `[FORMULA:${[
        superscriptBefore,
        subscriptBefore,
        mainText,
        superscriptAfter,
        subscriptAfter,
        squareRoot ? 'true' : 'false',
    ].map(value => encodeURIComponent(value.trim())).join('|')}]`;
}

export function parseFormulaToken(token) {
    if (!token.startsWith('[FORMULA:') || !token.endsWith(']')) return null;
    const values = token.slice(9, -1).split('|');
    if (values.length !== 5 && values.length !== 6) return null;

    try {
        const decoded = values.map(decodeURIComponent);
        const [superscriptBefore, subscriptBefore, mainText, superscriptAfter, subscriptAfter] = decoded;
        const squareRoot = decoded[5] === 'true';
        if (!mainText) return null;
        return { superscriptBefore, subscriptBefore, mainText, superscriptAfter, subscriptAfter, squareRoot };
    } catch {
        return null;
    }
}
