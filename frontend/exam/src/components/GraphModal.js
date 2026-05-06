import React from 'react';
import { MAX_GRAPH_BOXES_X, MAX_GRAPH_BOXES_Y } from '../hooks/useDrawing';

const PX_PER_CM = 96 / 2.54;

const clampBoxes = (value, max) => Math.max(1, Math.min(max, parseInt(value, 10) || 1));

function GraphPreview({ widthBoxes, heightBoxes }) {
  const widthPx = Math.max(220, widthBoxes * PX_PER_CM);
  const heightPx = Math.max(220, heightBoxes * PX_PER_CM);

  return (
    <div className="overflow-auto rounded-xl border border-gray-200 bg-gray-50 p-3" style={{ maxHeight: '52vh' }}>
          <div
        className="mx-auto"
        style={{
          width: `${widthPx}px`,
          height: `${heightPx}px`,
          boxSizing: 'border-box',
          border: '2px solid #000',
          backgroundColor: '#fff',
          backgroundImage: [
            // 1mm thin (subtle gray)
            'repeating-linear-gradient(to right, rgba(156,163,175,0.75) 0, rgba(156,163,175,0.75) 0.9px, transparent 0.9px, transparent 1mm)',
            'repeating-linear-gradient(to bottom, rgba(156,163,175,0.75) 0, rgba(156,163,175,0.75) 0.9px, transparent 0.9px, transparent 1mm)',
            // 5mm medium (dark gray)
            'repeating-linear-gradient(to right, rgba(17,24,39,0.95) 0, rgba(17,24,39,0.95) 1.6px, transparent 1.6px, transparent 5mm)',
            'repeating-linear-gradient(to bottom, rgba(17,24,39,0.95) 0, rgba(17,24,39,0.95) 1.6px, transparent 1.6px, transparent 5mm)',
            // 10mm bold (black)
            'repeating-linear-gradient(to right, rgba(0,0,0,1) 0, rgba(0,0,0,1) 3px, transparent 3px, transparent 10mm)',
            'repeating-linear-gradient(to bottom, rgba(0,0,0,1) 0, rgba(0,0,0,1) 3px, transparent 3px, transparent 10mm)'
          ].join(', ')
        }}
      />
    </div>
  );
}

export default function GraphModal({
  open,
  onClose,
  onSave,
  section = 'question',
  graphBoxesX,
  setGraphBoxesX,
  graphBoxesY,
  setGraphBoxesY,
}) {
  if (!open) return null;

  const handleSave = () => {
    onSave({ type: 'graph', graphBoxesX, graphBoxesY }, section);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="flex max-h-[90vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-gray-200 bg-gradient-to-r from-emerald-50 to-sky-50 px-6 py-4">
          <div>
            <h2 className="text-xl font-bold text-gray-800">Graph Paper</h2>
            <p className="text-sm text-gray-600">Set the number of 1 cm squares before inserting the grid.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-2xl font-light text-gray-500 transition hover:text-gray-700"
            title="Close modal"
          >
            ✕
          </button>
        </div>

        <div className="grid flex-1 gap-6 overflow-auto p-6 lg:grid-cols-[320px_minmax(0,1fr)]">
          <div className="space-y-5 rounded-xl border border-gray-200 bg-gray-50 p-4">
            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-wide text-gray-600">
                Squares on X
              </label>
              <input
                type="number"
                min="1"
                max={MAX_GRAPH_BOXES_X}
                value={graphBoxesX}
                onChange={e => setGraphBoxesX(clampBoxes(e.target.value, MAX_GRAPH_BOXES_X))}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
              />
              <p className="mt-1 text-xs text-gray-500">Maximum: {MAX_GRAPH_BOXES_X} cm</p>
            </div>

            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-wide text-gray-600">
                Squares on Y
              </label>
              <input
                type="number"
                min="1"
                max={MAX_GRAPH_BOXES_Y}
                value={graphBoxesY}
                onChange={e => setGraphBoxesY(clampBoxes(e.target.value, MAX_GRAPH_BOXES_Y))}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
              />
              <p className="mt-1 text-xs text-gray-500">Maximum: {MAX_GRAPH_BOXES_Y} cm</p>
            </div>

            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-900">
              1 mm grid lines are visible, 5 mm lines are stronger, and each 10 mm line is bold black.
            </div>
          </div>

          <div className="rounded-xl border border-gray-200 bg-white p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-700">Preview</h3>
              <span className="text-xs text-gray-500">
                {graphBoxesX} cm x {graphBoxesY} cm
              </span>
            </div>
            <GraphPreview widthBoxes={graphBoxesX} heightBoxes={graphBoxesY} />
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 border-t border-gray-200 bg-gray-100 px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg bg-gray-300 px-6 py-2 font-medium text-gray-800 transition hover:bg-gray-400"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="rounded-lg bg-emerald-600 px-6 py-2 font-medium text-white transition hover:bg-emerald-700"
          >
            Insert Graph
          </button>
        </div>
      </div>
    </div>
  );
}
