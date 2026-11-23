import React, { useState } from 'react';

let nodeCounter = 0;
const nextId = () => { nodeCounter += 1; return `n${nodeCounter}`; };

// ---- node factories -------------------------------------------------------------------------------------------
export const textNode = (value = '', fresh = false) => ({ id: nextId(), type: 'text', value, fresh });
export const scriptsNode = () => ({ id: nextId(), type: 'scripts', base: '', sup: '', sub: '', fresh: true });
export const fracNode = () => ({ id: nextId(), type: 'frac', num: [textNode('', true)], den: [textNode('')] });
export const rootNode = () => ({ id: nextId(), type: 'root', degree: '', body: [textNode('', true)] });
export const groupNode = shape => ({ id: nextId(), type: 'group', shape, body: [textNode('', true)] });
export const scriptBlockNode = type => ({ id: nextId(), type, body: [textNode('', true)] });

export const defaultExpression = () => [{ id: nextId(), type: 'frac', num: [textNode('', true)], den: [textNode('')] }];

// ---- serialisation to the existing tokens -----------------------------------------------------------------------
// ':' is the numerator/denominator separator and cannot appear in fraction text, so it becomes the ratio sign.
const serializeText = (value, inFrac) => (inFrac ? value.replace(/:/g, '∶') : value);

export function serialize(nodes, inFrac = false) {
    return nodes.map(node => {
        switch (node.type) {
            case 'text':
                return serializeText(node.value, inFrac);
            case 'scripts': {
                if (!node.sup && !node.sub) return serializeText(node.base, inFrac);
                const enc = value => encodeURIComponent(value);
                return `[FORMULA:||${enc(node.base)}|${enc(node.sup)}|${enc(node.sub)}]`;
            }
            case 'frac':
                return `[FRAC:${serialize(node.num, true).trim()}:${serialize(node.den, true).trim()}]`;
            case 'root':
                return `[ROOT:${encodeURIComponent(node.degree.trim())}|${serialize(node.body, inFrac)}]`;
            case 'group':
                return `[BRACKET:both|${node.shape}|0|${encodeURIComponent(serialize(node.body, false))}]`;
            case 'sup':
                return `[SUP]${serialize(node.body, inFrac)}[/SUP]`;
            case 'sub':
                return `[SUB]${serialize(node.body, inFrac)}[/SUB]`;
            default:
                return '';
        }
    }).join('');
}

// Every fraction/root/group/script block must contain something before the expression can be inserted.
export function isComplete(nodes) {
    return nodes.every(node => {
        if (node.type === 'frac') return serialize(node.num).trim() !== '' && serialize(node.den).trim() !== '' && isComplete(node.num) && isComplete(node.den);
        if (['root', 'group', 'sup', 'sub'].includes(node.type)) return serialize(node.body).trim() !== '' && isComplete(node.body);
        return true;
    });
}

// ---- editor ---------------------------------------------------------------------------------------------------
const SHAPES = ['rounded', 'square', 'curly'];
const SHAPE_LABEL = { rounded: '( )', square: '[ ]', curly: '{ }' };

const miniInput = 'border border-gray-300 rounded px-1 py-0.5 text-sm bg-white focus:outline-none focus:ring-1 focus:ring-blue-500';

function Chrome({ children, onLeft, onRight, onRemove, canLeft, canRight, onWrap, onUnwrap }) {
    return (
        <span className="relative inline-flex group align-middle">
            {children}
            <span className="absolute -top-5 left-0 z-20 hidden group-hover:flex group-focus-within:flex items-center gap-px bg-white border border-gray-300 rounded shadow text-[10px] leading-none">
                <button type="button" disabled={!canLeft} onClick={onLeft} className="px-1 py-0.5 disabled:opacity-30 hover:bg-gray-100" title="Move left">‹</button>
                <button type="button" disabled={!canRight} onClick={onRight} className="px-1 py-0.5 disabled:opacity-30 hover:bg-gray-100" title="Move right">›</button>
                {onWrap && SHAPES.map(shape => (
                    <button key={shape} type="button" onClick={() => onWrap(shape)} className="px-1 py-0.5 hover:bg-green-50 font-semibold" title={`Wrap in ${SHAPE_LABEL[shape]} spanning the whole part`}>{SHAPE_LABEL[shape]}</button>
                ))}
                {onUnwrap && <button type="button" onClick={onUnwrap} className="px-1 py-0.5 hover:bg-gray-100" title="Remove the brackets but keep the content">⤢</button>}
                <button type="button" onClick={onRemove} className="px-1 py-0.5 text-red-600 hover:bg-red-50" title="Remove">×</button>
            </span>
        </span>
    );
}

function Palette({ onAdd }) {
    const [open, setOpen] = useState(false);
    const add = node => { onAdd(node); setOpen(false); };
    const btn = 'px-1.5 py-0.5 rounded border text-xs bg-white hover:bg-blue-50 border-gray-300';
    if (!open) {
        return <button type="button" onClick={() => setOpen(true)} className="px-1.5 py-0.5 rounded border border-dashed border-gray-400 text-xs text-gray-600 hover:bg-gray-100 align-middle" title="Add">+</button>;
    }
    return (
        <span className="inline-flex flex-wrap items-center gap-1 p-1 bg-blue-50 border border-blue-200 rounded align-middle">
            <button type="button" className={btn} onClick={() => add(textNode('', true))} title="Text or number">T</button>
            <button type="button" className={btn} onClick={() => add(scriptsNode())} title="Letter with superscript / subscript stacked">a<sup>n</sup><sub>m</sub></button>
            <button type="button" className={btn} onClick={() => add(fracNode())} title="Fraction">a⁄b</button>
            <button type="button" className={btn} onClick={() => add(rootNode())} title="Root">√</button>
            {SHAPES.map(shape => (
                <button key={shape} type="button" className={btn} onClick={() => add(groupNode(shape))} title="Brackets that stretch around their content">{SHAPE_LABEL[shape]}</button>
            ))}
            <button type="button" className={btn} onClick={() => add(scriptBlockNode('sup'))} title="Superscript (e.g. power after a bracket)">x<sup>n</sup></button>
            <button type="button" className={btn} onClick={() => add(scriptBlockNode('sub'))} title="Subscript">x<sub>n</sub></button>
            <button type="button" className="px-1 text-xs text-gray-500" onClick={() => setOpen(false)} title="Close">×</button>
        </span>
    );
}

export function Slot({ nodes, onChange, compact = false }) {
    const update = (index, node) => onChange(nodes.map((n, i) => (i === index ? node : n)));
    const remove = index => onChange(nodes.filter((_, i) => i !== index));
    const move = (index, delta) => {
        const copy = [...nodes];
        const [item] = copy.splice(index, 1);
        copy.splice(index + delta, 0, item);
        onChange(copy);
    };
    const wrap = (index, shape) => onChange(nodes.map((n, i) => (i === index ? { ...groupNode(shape), body: [n] } : n)));
    const unwrap = index => onChange(nodes.flatMap((n, i) => (i === index ? n.body : [n])));
    const insertAtEnd = node => onChange([...nodes, node]);

    return (
        <span className={`inline-flex flex-wrap items-center ${compact ? 'gap-1' : 'gap-1.5'} min-w-[2rem]`}>
            {nodes.map((node, index) => (
                <Chrome key={node.id} canLeft={index > 0} canRight={index < nodes.length - 1}
                    onLeft={() => move(index, -1)} onRight={() => move(index, 1)} onRemove={() => remove(index)}
                    onWrap={node.type === 'text' ? null : shape => wrap(index, shape)}
                    onUnwrap={node.type === 'group' ? () => unwrap(index) : null}>
                    <NodeEditor node={node} onChange={updated => update(index, updated)} />
                </Chrome>
            ))}
            <Palette onAdd={insertAtEnd} />
        </span>
    );
}

function NodeEditor({ node, onChange }) {
    const set = patch => onChange({ ...node, ...patch });

    switch (node.type) {
        case 'text':
            return (
                <input autoFocus={node.fresh} value={node.value} onChange={event => set({ value: event.target.value, fresh: false })}
                    className={miniInput} style={{ width: `${Math.max(3, node.value.length + 2)}ch` }} placeholder="…" />
            );
        case 'scripts':
            return (
                <span className="inline-flex items-center gap-0.5">
                    <input autoFocus={node.fresh} value={node.base} onChange={event => set({ base: event.target.value, fresh: false })}
                        className={miniInput} style={{ width: `${Math.max(3, node.base.length + 2)}ch` }} placeholder="a" />
                    <span className="inline-flex flex-col gap-0.5">
                        <input value={node.sup} onChange={event => set({ sup: event.target.value })} className={`${miniInput} text-xs`} style={{ width: `${Math.max(3, node.sup.length + 2)}ch` }} placeholder="ⁿ" title="Superscript" />
                        <input value={node.sub} onChange={event => set({ sub: event.target.value })} className={`${miniInput} text-xs`} style={{ width: `${Math.max(3, node.sub.length + 2)}ch` }} placeholder="ₙ" title="Subscript" />
                    </span>
                </span>
            );
        case 'frac':
            return (
                <span className="inline-flex flex-col items-center border border-blue-200 rounded bg-blue-50/40 px-1.5 py-1 gap-1 align-middle">
                    <Slot nodes={node.num} onChange={num => set({ num })} compact />
                    <span className="w-full border-t-2 border-gray-700" />
                    <Slot nodes={node.den} onChange={den => set({ den })} compact />
                </span>
            );
        case 'root':
            return (
                <span className="inline-flex items-start gap-0.5 border border-purple-200 rounded bg-purple-50/40 px-1 py-1 align-middle">
                    <input value={node.degree} onChange={event => set({ degree: event.target.value })} className={`${miniInput} text-xs`} style={{ width: '3ch' }} placeholder="n" title="Root degree (blank = square root)" />
                    <span className="text-xl leading-none">√</span>
                    <span className="border-t-2 border-gray-700 pt-0.5"><Slot nodes={node.body} onChange={body => set({ body })} compact /></span>
                </span>
            );
        case 'group':
            return (
                <span className="inline-flex items-center gap-1 border border-green-200 rounded bg-green-50/40 px-1 py-1 align-middle">
                    <button type="button" onClick={() => set({ shape: SHAPES[(SHAPES.indexOf(node.shape) + 1) % SHAPES.length] })}
                        className="text-sm font-semibold px-1 rounded hover:bg-green-100" title="Change bracket shape">{SHAPE_LABEL[node.shape]}</button>
                    <Slot nodes={node.body} onChange={body => set({ body })} compact />
                </span>
            );
        case 'sup':
        case 'sub':
            return (
                <span className="inline-flex items-start gap-0.5 border border-orange-200 rounded bg-orange-50/40 px-1 py-0.5 align-middle">
                    <span className="text-xs text-gray-500">{node.type === 'sup' ? '↑' : '↓'}</span>
                    <Slot nodes={node.body} onChange={body => set({ body })} compact />
                </span>
            );
        default:
            return null;
    }
}