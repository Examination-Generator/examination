import React, { useRef, useCallback } from 'react';
import DrawingApp from './drawing/drawapp';


export default function DrawingModal({ isOpen, onClose, onSave, section = 'question' }) {
  const drawingAppRef = useRef(null);

  const handleSave = useCallback(() => {
    // Call DrawingApp's export method via ref
    if (!drawingAppRef.current) {
      console.error('DrawingApp ref not available');
      return;
    }

    try {
      // Export as data URL (PNG format)
      const imageUrl = drawingAppRef.current.exportImage();
      
      if (!imageUrl) {
        console.error('Failed to export image from DrawingApp');
        return;
      }
      
      // Return drawing data to form
      onSave({
        type: 'image',
        imageUrl,
        width: 794, 
        height: 1123, 
        section: section,
      });

      // Close modal
      onClose();
    } catch (error) {
      console.error('Error saving drawing:', error);
    }
  }, [onSave, onClose, section]);

  const handleCancel = useCallback(() => {
    onClose();
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/75 flex items-center justify-center z-50 p-4">
      {/* Modal container */}
      <div className="w-full h-full max-w-6xl max-h-[90vh] bg-white rounded-lg flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b-2 border-gray-200 bg-gradient-to-r from-purple-50 to-blue-50">
          <h2 className="text-xl font-bold text-gray-800">
            Drawing Tool - {section === 'question' ? 'Question' : 'Answer'}
          </h2>
          <button
            type="button"
            onClick={handleCancel}
            className="text-gray-500 hover:text-gray-700 text-2xl font-light transition"
            title="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Drawing app container - takes remaining space */}
        <div className="flex-1 overflow-hidden bg-gray-50">
          <DrawingApp ref={drawingAppRef} />
        </div>

        {/* Footer with action buttons */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t-2 border-gray-200 bg-gray-100">
          <button
            type="button"
            onClick={handleCancel}
            className="px-6 py-2 rounded-lg bg-gray-300 text-gray-800 font-medium hover:bg-gray-400 transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-6 py-2 rounded-lg bg-purple-600 text-white font-medium hover:bg-purple-700 transition"
          >
            Save & Insert Drawing
          </button>
        </div>
      </div>
    </div>
  );
}
