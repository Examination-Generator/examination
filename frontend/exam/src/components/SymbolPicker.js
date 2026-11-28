import React, { useMemo, useState } from 'react';

// Textbook-style (math italic) letters: variables such as x, y, h, u, v print slanted in books, not as plain typing.
const italic = ch => {
    if (ch === 'h') return '\u210E';
    const code = ch.charCodeAt(0);
    if (code >= 97 && code <= 122) return String.fromCodePoint(0x1D44E + code - 97);
    if (code >= 65 && code <= 90) return String.fromCodePoint(0x1D434 + code - 65);
    return ch;
};
const LOWER = 'abcdefghijklmnopqrstuvwxyz'.split('');
const MATH_FONT = "'Cambria Math','STIX Two Math','Latin Modern Math','Times New Roman',serif";

// [lower, upper, name]; some letters (final sigma, variants) only exist in one case.
const GREEK = [
    ['α', 'Α', 'alpha'], ['β', 'Β', 'beta'], ['γ', 'Γ', 'gamma'], ['δ', 'Δ', 'delta'], ['ε', 'Ε', 'epsilon'],
    ['ζ', 'Ζ', 'zeta'], ['η', 'Η', 'eta'], ['θ', 'Θ', 'theta'], ['ι', 'Ι', 'iota'], ['κ', 'Κ', 'kappa'],
    ['λ', 'Λ', 'lambda'], ['μ', 'Μ', 'mu'], ['ν', 'Ν', 'nu'], ['ξ', 'Ξ', 'xi'], ['ο', 'Ο', 'omicron'],
    ['π', 'Π', 'pi'], ['ρ', 'Ρ', 'rho'], ['σ', 'Σ', 'sigma'], ['τ', 'Τ', 'tau'], ['υ', 'Υ', 'upsilon'],
    ['φ', 'Φ', 'phi'], ['χ', 'Χ', 'chi'], ['ψ', 'Ψ', 'psi'], ['ω', 'Ω', 'omega'],
    ['ς', null, 'final sigma'], ['ϵ', null, 'epsilon (lunate)'], ['ϑ', 'ϴ', 'theta (script)'], ['ϰ', null, 'kappa (variant)'],
    ['ϕ', null, 'phi (variant)'], ['ϖ', null, 'pi (variant)'], ['ϱ', null, 'rho (variant)'], ['ϝ', 'Ϝ', 'digamma'],
];

const SI_PREFIXES = [
    ['Q', 'quetta', 30], ['R', 'ronna', 27], ['Y', 'yotta', 24], ['Z', 'zetta', 21], ['E', 'exa', 18], ['P', 'peta', 15],
    ['T', 'tera', 12], ['G', 'giga', 9], ['M', 'mega', 6], ['k', 'kilo', 3], ['h', 'hecto', 2], ['da', 'deca', 1],
    ['d', 'deci', -1], ['c', 'centi', -2], ['m', 'milli', -3], ['μ', 'micro', -6], ['n', 'nano', -9], ['p', 'pico', -12],
    ['f', 'femto', -15], ['a', 'atto', -18], ['z', 'zepto', -21], ['y', 'yocto', -24], ['r', 'ronto', -27], ['q', 'quecto', -30],
];
const SUP = { '-': '\u207B', 0: '\u2070', 1: '\u00B9', 2: '\u00B2', 3: '\u00B3', 4: '\u2074', 5: '\u2075', 6: '\u2076', 7: '\u2077', 8: '\u2078', 9: '\u2079' };
const sup = n => String(n).split('').map(c => SUP[c] || c).join('');

const LATIN_HINTS = {
    a: 'acceleration / area', b: 'constant b', c: 'speed of light', d: 'distance', e: 'energy / Euler number', f: 'function / frequency', g: 'gravity',
    h: 'height / Planck constant', i: 'current / index', j: 'index j', k: 'constant k', l: 'length', m: 'mass', n: 'number n', o: 'origin', p: 'momentum / pressure',
    q: 'charge', r: 'radius', s: 'displacement', t: 'time', u: 'initial velocity', v: 'velocity', w: 'weight / work', x: 'variable x', y: 'variable y', z: 'variable z',
};
const latinItems = upper => LOWER.map(ch => {
    const letter = upper ? ch.toUpperCase() : ch;
    return { symbol: italic(letter), name: `${letter} \u2013 ${LATIN_HINTS[ch]}` };
});

const list = (pairs) => pairs.map(([symbol, name]) => ({ symbol, name }));

const SymbolPicker = ({ onInsert, onClose, targetType = 'question' }) => {
    const symbols = {
        'Greek Letters': null,
        'Letters (a-z)': null, 
        'SI Prefixes': SI_PREFIXES.map(([symbol, name, power]) => ({ symbol, name: `${name} (${symbol}, 10${sup(power)})` })),
        'Mathematical Operators': list([
            ['+', 'plus / addition'], ['\u2212', 'minus / subtraction'], ['\u00D7', 'multiplication (times)'], ['\u00F7', 'division'],
            ['\u22C5', 'dot multiplication'], ['\u00B7', 'middle dot'], ['\u2217', 'asterisk operator'], ['*', 'asterisk'],
            ['/', 'slash division'], ['\u2215', 'division slash'], ['%', 'percent'], [' mod ', 'modulus (mod)'],
            ['|', 'vertical bar / modulus (absolute value)'], ['\u2223', 'divides / vertical bar'], ['\u2224', 'does not divide'], ['\u2016', 'norm / parallel bars'],
            ['\u00B1', 'plus-minus'], ['\u2213', 'minus-plus'], ['\u2218', 'composition / ring operator'], ['\u2219', 'bullet operator'],
            ['=', 'equals'], ['\u2260', 'not equal'], ['\u2248', 'approximately equal'], ['\u2249', 'not approximately equal'], ['\u2245', 'congruent'],
            ['\u2243', 'asymptotically equal'], ['\u223C', 'similar / tilde'], ['\u2261', 'identical'], ['\u2262', 'not identical'], ['\u225C', 'delta equals'],
            ['\u2254', 'colon equals'], ['<', 'less than'], ['>', 'greater than'], ['\u2264', 'less than or equal'], ['\u2265', 'greater than or equal'],
            ['\u226A', 'much less than'], ['\u226B', 'much greater than'], ['\u226E', 'not less than'], ['\u226F', 'not greater than'],
            ['\u221D', 'proportional to'], ['\u221E', 'infinity'], ['\u221A', 'square root'], ['\u221B', 'cube root'], ['\u221C', 'fourth root'],
            ['\u2211', 'summation'], ['\u220F', 'product'], ['\u2210', 'coproduct'], ['\u222B', 'integral'], ['\u222C', 'double integral'],
            ['\u222D', 'triple integral'], ['\u222E', 'contour integral'], ['\u2202', 'partial derivative'], ['\u2207', 'nabla / del'], ['\u2206', 'increment / delta'],
            ['\u2295', 'circled plus'], ['\u2297', 'circled times'], ['\u2296', 'circled minus'], ['\u2299', 'circled dot'],
            ['\u230A', 'floor left'], ['\u230B', 'floor right'], ['\u2308', 'ceiling left'], ['\u2309', 'ceiling right'], ['\u27E8', 'angle bracket left'], ['\u27E9', 'angle bracket right'],
            ['!', 'factorial'], ['\u2032', 'prime'], ['\u2033', 'double prime'], ['\u2034', 'triple prime'], ['\u00B0', 'degree'], ['\u2030', 'per mille'],
            ['\u2234', 'therefore'], ['\u2235', 'because'], ['\u2713', 'tick / check mark'], ['\u2717', 'cross'],
        ]),
        'Geometry & Angles': list([
            ['\u2220', 'angle'], ['\u2221', 'measured angle'], ['\u2222', 'spherical angle'], ['\u22BE', 'right angle with arc'], ['\u221F', 'right angle'],
            ['\u22A5', 'perpendicular'], ['\u27C2', 'perpendicular (long)'], ['\u2225', 'parallel'], ['\u2226', 'not parallel'],
            ['\u25B3', 'triangle'], ['\u25B1', 'parallelogram'], ['\u25A1', 'square'], ['\u25CB', 'circle'], ['\u2312', 'arc'], ['\u2245', 'congruent to'],
            ['\u223C', 'similar to'], ['\u2299', 'circle dot'], ['\u00B0', 'degree'], ['\u2032', 'minutes / prime'], ['\u2033', 'seconds / double prime'],
            ['\u22BF', 'right triangle'], ['\u2316', 'position indicator'], ['\u2194', 'line through points'], ['\u21C4', 'reflection arrows'],
        ]),
        'Set Theory & Logic': list([
            ['\u2208', 'element of'], ['\u2209', 'not element of'], ['\u220B', 'contains as member'], ['\u222A', 'union'], ['\u2229', 'intersection'],
            ['\u2282', 'subset'], ['\u2283', 'superset'], ['\u2286', 'subset or equal'], ['\u2287', 'superset or equal'], ['\u2284', 'not subset'],
            ['\u2205', 'empty set'], ['\u2216', 'set minus'], ['\u2200', 'for all'], ['\u2203', 'there exists'], ['\u2204', 'there does not exist'],
            ['\u2227', 'and'], ['\u2228', 'or'], ['\u00AC', 'not'], ['\u22BB', 'xor'], ['\u22A2', 'proves'], ['\u22A8', 'models'],
            ['\u2115', 'natural numbers'], ['\u2124', 'integers'], ['\u211A', 'rationals'], ['\u211D', 'real numbers'], ['\u2102', 'complex numbers'], ['\u2119', 'primes / power set'],
        ]),
        'Arrows': list([
            ['\u2192', 'right arrow'], ['\u2190', 'left arrow'], ['\u2191', 'up arrow'], ['\u2193', 'down arrow'], ['\u2194', 'left-right arrow'], ['\u2195', 'up-down arrow'],
            ['\u21D2', 'right double arrow'], ['\u21D0', 'left double arrow'], ['\u21D4', 'left-right double arrow'], ['\u27F6', 'long right arrow'],
            ['\u27F5', 'long left arrow'], ['\u27F7', 'long left-right arrow'], ['\u21CC', 'equilibrium arrows'], ['\u21C0', 'harpoon right'], ['\u21BC', 'harpoon left'],
            ['\u21A6', 'maps to'], ['\u2197', 'north-east arrow'], ['\u2198', 'south-east arrow'],
        ]),
        'Scientific Units': list([
            ['m', 'meter'], ['kg', 'kilogram'], ['g', 'gram'], ['s', 'second'], ['A', 'ampere'], ['K', 'kelvin'], ['mol', 'mole'], ['cd', 'candela'], ['Hz', 'hertz'],
            ['N', 'newton'], ['Pa', 'pascal'], ['J', 'joule'], ['W', 'watt'], ['C', 'coulomb'], ['V', 'volt'], ['\u03A9', 'ohm'], ['F', 'farad'], ['T', 'tesla'], ['Wb', 'weber'],
            ['H', 'henry'], ['S', 'siemens'], ['Bq', 'becquerel'], ['Gy', 'gray'], ['Sv', 'sievert'], ['L', 'litre'], ['eV', 'electron-volt'], ['\u2103', 'celsius'],
            ['m\u00B2', 'square meter'], ['m\u00B3', 'cubic meter'], ['m/s', 'meter per second'], ['m/s\u00B2', 'meter per second squared'], ['\u00C5', 'angstrom'],
        ]),
        'Common Superscripts': list('\u2070\u00B9\u00B2\u00B3\u2074\u2075\u2076\u2077\u2078\u2079\u207A\u207B\u207F'.split('').map((c, i) => [c, `superscript ${['0','1','2','3','4','5','6','7','8','9','plus','minus','n'][i]}`])),
        'Common Subscripts': list('\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089\u208A\u208B\u2099'.split('').map((c, i) => [c, `subscript ${['0','1','2','3','4','5','6','7','8','9','plus','minus','n'][i]}`])),
        'Physics Variables': list([
            ['\u2113', 'length (script l)'], ['\u210F', 'h-bar (reduced Planck constant)'], ['\u03BB\u2080', 'lambda sub 0'],
            [italic('E') + '_f', 'energy E sub f'], [italic('F') + '_c', 'force F sub c'], [italic('m') + '\u2091', 'mass m sub e'],
            [italic('f') + '\u2080', 'f sub 0'], [italic('W') + '\u2080', 'W sub 0'], [italic('K') + italic('E') + '\u2098\u2090\u2093', 'max kinetic energy'],
            [italic('v') + '\u2080', 'initial velocity v sub 0'], [italic('x') + '\u2080', 'x sub 0'], [italic('h') + '\u03BD', 'photon energy hf'],
        ]),
    };

    const [activeCategory, setActiveCategory] = useState('Greek Letters');
    const [searchTerm, setSearchTerm] = useState('');
    const [upperCase, setUpperCase] = useState(false);

    // Greek honours the case toggle; in search both cases are searched.
    const greekItems = useMemo(() => GREEK
        .map(([lower, upper, name]) => (upperCase ? (upper && { symbol: upper, name: `${name.charAt(0).toUpperCase()}${name.slice(1)} (capital)` }) : { symbol: lower, name }))
        .filter(Boolean), [upperCase]);
    const greekAll = useMemo(() => GREEK.flatMap(([lower, upper, name]) => [{ symbol: lower, name }, upper && { symbol: upper, name: `${name} capital` }].filter(Boolean)), []);
    const resolved = {
        ...symbols,
        'Greek Letters': searchTerm ? greekAll : greekItems,
        'Letters (a-z)': searchTerm ? [...latinItems(false), ...latinItems(true)] : latinItems(upperCase),
    };

    const filteredSymbols = searchTerm
        ? Object.entries(resolved).reduce((acc, [category, items]) => {
            const term = searchTerm.toLowerCase();
            const filtered = items.filter(item => item.name.toLowerCase().includes(term) || item.symbol.includes(searchTerm));
            if (filtered.length > 0) acc[category] = filtered;
            return acc;
        }, {})
        : { [activeCategory]: resolved[activeCategory] };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xl font-bold">Insert Special Symbol</h3>
                        <button
                            onClick={onClose}
                            className="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded-lg transition"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    {/* Search Bar */}
                    <div className="mt-3">
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Search symbols (e.g., 'pi', 'alpha', 'integral')..."
                            className="w-full px-4 py-2 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white"
                        />
                    </div>
                </div>

                <div className="flex flex-1 overflow-hidden">
                    {/* Category Sidebar */}
                    {!searchTerm && (
                        <div className="w-48 bg-gray-50 border-r border-gray-200 overflow-y-auto">
                            {Object.keys(resolved).map(category => (
                                <button
                                    key={category}
                                    onClick={() => setActiveCategory(category)}
                                    className={`w-full text-left px-4 py-3 text-sm font-medium transition ${
                                        activeCategory === category
                                            ? 'bg-indigo-100 text-indigo-700 border-l-4 border-indigo-600'
                                            : 'text-gray-700 hover:bg-gray-100'
                                    }`}
                                >
                                    {category}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Symbols Grid */}
                    <div className="flex-1 p-6 overflow-y-auto">
                        {!searchTerm && ['Greek Letters', 'Letters (a-z)'].includes(activeCategory) && (
                            <div className="mb-4 inline-flex rounded-lg border border-gray-300 overflow-hidden text-sm font-semibold">
                                <button type="button" onClick={() => setUpperCase(false)} className={`px-4 py-1.5 ${!upperCase ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700'}`}>lower case</button>
                                <button type="button" onClick={() => setUpperCase(true)} className={`px-4 py-1.5 ${upperCase ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700'}`}>UPPER CASE</button>
                            </div>
                        )}
                        {Object.entries(filteredSymbols).map(([category, items]) => (
                            <div key={category} className="mb-6">
                                {searchTerm && (
                                    <h4 className="text-sm font-bold text-gray-700 mb-3">{category}</h4>
                                )}
                                <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-10 gap-2">
                                    {items.map(({ symbol, name }) => (
                                        <button
                                            key={`${name}-${symbol}`}
                                            onClick={() => {
                                                onInsert(symbol);
                                                onClose();
                                            }}
                                            className="aspect-square bg-white border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition flex flex-col items-center justify-center p-2 group"
                                            title={name}
                                        >
                                            <span className="text-2xl" style={{ fontFamily: MATH_FONT }}>{symbol}</span>
                                            <span className={`text-[10px] text-gray-500 mt-1 transition truncate w-full text-center ${category === 'SI Prefixes' ? '' : 'opacity-0 group-hover:opacity-100'}`}>
                                                {category === 'SI Prefixes' ? name.split(' ')[0] : name}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        ))}
                        
                        {Object.keys(filteredSymbols).length === 0 && (
                            <div className="text-center py-12 text-gray-500">
                                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <p className="font-semibold">No symbols found</p>
                                <p className="text-sm">Try a different search term</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer with Quick Info */}
                <div className="bg-gray-50 px-6 py-3 border-t border-gray-200">
                    <p className="text-xs text-gray-600">
                        💡 <strong>Tip:</strong> You can also use formatting buttons for superscript (x²) and subscript (H₂O) with custom text
                    </p>
                </div>
            </div>
        </div>
    );
};

export default SymbolPicker;