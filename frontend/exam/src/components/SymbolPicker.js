import React, { useState } from 'react';
const SymbolPicker = ({ onInsert, onClose, targetType = 'question' }) => {
    const symbols = {
        'Greek Letters': [
            { symbol: 'α', name: 'alpha' },
            { symbol: 'β', name: 'beta' },
            { symbol: 'γ', name: 'gamma' },
            { symbol: 'δ', name: 'delta' },
            { symbol: 'ε', name: 'epsilon' },
            { symbol: 'ζ', name: 'zeta' },
            { symbol: 'η', name: 'eta' },
            { symbol: 'θ', name: 'theta' },
            { symbol: 'ι', name: 'iota' },
            { symbol: 'κ', name: 'kappa' },
            { symbol: 'λ', name: 'lambda' },
            { symbol: 'μ', name: 'mu' },
            { symbol: 'ν', name: 'nu' },
            { symbol: 'ξ', name: 'xi' },
            { symbol: 'π', name: 'pi' },
            { symbol: 'ρ', name: 'rho' },
            { symbol: 'σ', name: 'sigma' },
            { symbol: 'τ', name: 'tau' },
            { symbol: 'φ', name: 'phi' },
            { symbol: 'χ', name: 'chi' },
            { symbol: 'ψ', name: 'psi' },
            { symbol: 'ω', name: 'omega' },
            { symbol: 'Α', name: 'Alpha' },
            { symbol: 'Β', name: 'Beta' },
            { symbol: 'Γ', name: 'Gamma' },
            { symbol: 'Δ', name: 'Delta' },
            { symbol: 'Θ', name: 'Theta' },
            { symbol: 'Λ', name: 'Lambda' },
            { symbol: 'Ξ', name: 'Xi' },
            { symbol: 'Π', name: 'Pi' },
            { symbol: 'Σ', name: 'Sigma' },
            { symbol: 'Φ', name: 'Phi' },
            { symbol: 'Ψ', name: 'Psi' },
            { symbol: 'Ω', name: 'Omega' }
        ],
        'Mathematical Operators': [
            { symbol: '÷', name: 'division' },
            { symbol: '×', name: 'multiplication' },
            { symbol: '✓︎', name: 'tick/check mark' },
            { symbol: '±', name: 'plus-minus' },
            { symbol: '∓', name: 'minus-plus' },
            { symbol: '≠', name: 'not equal' },
            { symbol: '≈', name: 'approximately' },
            { symbol: '≡', name: 'identical' },
            { symbol: '≤', name: 'less than or equal' },
            { symbol: '≥', name: 'greater than or equal' },
            { symbol: '∞', name: 'infinity' },
            { symbol: '∑', name: 'summation' },
            { symbol: '∫', name: 'integral' },
            { symbol: '∂', name: 'partial derivative' },
            { symbol: '∇', name: 'nabla/del' },
            { symbol: '√', name: 'square root' },
            { symbol: '∛', name: 'cube root' },
            { symbol: '∜', name: 'fourth root' },
            { symbol: '∝', name: 'proportional to' },
            { symbol: '∈', name: 'element of' },
            { symbol: '∉', name: 'not element of' },
            { symbol: '∪', name: 'union' },
            { symbol: '∩', name: 'intersection' },
            { symbol: '⊂', name: 'subset' },
            { symbol: '⊃', name: 'superset' },
            { symbol: '∀', name: 'for all' },
            { symbol: '∃', name: 'there exists' },
            { symbol: '∄', name: 'there does not exist' },
            { symbol: '∅', name: 'empty set' },
            { symbol: '°', name: 'degree' },
            { symbol: '′', name: 'prime' },
            { symbol: '″', name: 'double prime' }
        ],
        'Arrows': [
            { symbol: '→', name: 'right arrow' },
            { symbol: '←', name: 'left arrow' },
            { symbol: '↑', name: 'up arrow' },
            { symbol: '↓', name: 'down arrow' },
            { symbol: '↔', name: 'left-right arrow' },
            { symbol: '⇒', name: 'right double arrow' },
            { symbol: '⇐', name: 'left double arrow' },
            { symbol: '⇔', name: 'left-right double arrow' }
        ],
        'Scientific Units': [
            { symbol: 'm', name: 'meter' },
            { symbol: 'kg', name: 'kilogram' },
            { symbol: 's', name: 'second' },
            { symbol: 'A', name: 'ampere' },
            { symbol: 'K', name: 'kelvin' },
            { symbol: 'mol', name: 'mole' },
            { symbol: 'cd', name: 'candela' },
            { symbol: 'Hz', name: 'hertz' },
            { symbol: 'N', name: 'newton' },
            { symbol: 'Pa', name: 'pascal' },
            { symbol: 'J', name: 'joule' },
            { symbol: 'W', name: 'watt' },
            { symbol: 'C', name: 'coulomb' },
            { symbol: 'V', name: 'volt' },
            { symbol: 'Ω', name: 'ohm' },
            { symbol: 'F', name: 'farad' },
            { symbol: 'T', name: 'tesla' },
            { symbol: 'Wb', name: 'weber' },
            { symbol: 'H', name: 'henry' },
            { symbol: '℃', name: 'celsius' },
            { symbol: 'm²', name: 'square meter' },
            { symbol: 'm³', name: 'cubic meter' },
            { symbol: 'm/s', name: 'meter per second' },
            { symbol: 'm/s²', name: 'meter per second squared' }
        ],
        'Common Superscripts': [
            { symbol: '⁰', name: 'superscript 0' },
            { symbol: '¹', name: 'superscript 1' },
            { symbol: '²', name: 'superscript 2' },
            { symbol: '³', name: 'superscript 3' },
            { symbol: '⁴', name: 'superscript 4' },
            { symbol: '⁵', name: 'superscript 5' },
            { symbol: '⁶', name: 'superscript 6' },
            { symbol: '⁷', name: 'superscript 7' },
            { symbol: '⁸', name: 'superscript 8' },
            { symbol: '⁹', name: 'superscript 9' },
            { symbol: '⁺', name: 'superscript plus' },
            { symbol: '⁻', name: 'superscript minus' }
        ],
        'Common Subscripts': [
            { symbol: '₀', name: 'subscript 0' },
            { symbol: '₁', name: 'subscript 1' },
            { symbol: '₂', name: 'subscript 2' },
            { symbol: '₃', name: 'subscript 3' },
            { symbol: '₄', name: 'subscript 4' },
            { symbol: '₅', name: 'subscript 5' },
            { symbol: '₆', name: 'subscript 6' },
            { symbol: '₇', name: 'subscript 7' },
            { symbol: '₈', name: 'subscript 8' },
            { symbol: '₉', name: 'subscript 9' },
            { symbol: '₊', name: 'subscript plus' },
            { symbol: '₋', name: 'subscript minus' }
        ]
    };

    const [activeCategory, setActiveCategory] = useState('Greek Letters');
    const [searchTerm, setSearchTerm] = useState('');

    const filteredSymbols = searchTerm 
        ? Object.entries(symbols).reduce((acc, [category, items]) => {
            const filtered = items.filter(item => 
                item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.symbol.includes(searchTerm)
            );
            if (filtered.length > 0) {
                acc[category] = filtered;
            }
            return acc;
        }, {})
        : { [activeCategory]: symbols[activeCategory] };

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
                            {Object.keys(symbols).map(category => (
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
                        {Object.entries(filteredSymbols).map(([category, items]) => (
                            <div key={category} className="mb-6">
                                {searchTerm && (
                                    <h4 className="text-sm font-bold text-gray-700 mb-3">{category}</h4>
                                )}
                                <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-10 gap-2">
                                    {items.map(({ symbol, name }) => (
                                        <button
                                            key={name}
                                            onClick={() => {
                                                onInsert(symbol);
                                                onClose();
                                            }}
                                            className="aspect-square bg-white border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition flex flex-col items-center justify-center p-2 group"
                                            title={name}
                                        >
                                            <span className="text-2xl">{symbol}</span>
                                            <span className="text-xs text-gray-500 mt-1 opacity-0 group-hover:opacity-100 transition truncate w-full text-center">
                                                {name}
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