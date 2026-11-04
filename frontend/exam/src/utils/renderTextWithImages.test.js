import { parseGraphToken, renderTextWithImages } from './renderTextWithImages';

test('renders malformed markup without getting stuck in the parser', () => {
    const rendered = renderTextWithImages(
        '[TABLE:broken [IMAGE:not-a-number] [GRAPH:1:999999x999999cm]'
    );

    expect(rendered.length).toBeGreaterThan(0);
});

test('clamps oversized graph dimensions from stored question data', () => {
    expect(parseGraphToken('[GRAPH:1:999999x999999cm]')).toEqual({
        id: 1,
        widthCm: 21,
        heightCm: 30,
    });
});
