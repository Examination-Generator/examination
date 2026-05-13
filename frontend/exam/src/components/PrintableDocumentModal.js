import React, { useState } from 'react';
import html2pdf from 'html2pdf.js';
import { parseGraphToken } from '../utils/renderTextWithImages';

const PX_PER_CM = 96 / 2.54;
const GRAPH_TOKEN_RE = /\[GRAPH:[\d.]+:[\d.]+x[\d.]+cm\]/g;
const LINES_TOKEN_RE = /\[LINES:([\d.]+)\]/g;
const IMAGE_TOKEN_NEW_RE = /\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/g;
const IMAGE_TOKEN_OLD_RE = /\[IMAGE:([\d.]+):(\d+)px\]/g;

function drawGraphPaperCanvas(canvas, widthCm, heightCm, doc) {
    if (!canvas) return;

    const widthPx = Math.max(1, Math.round(widthCm * PX_PER_CM));
    const heightPx = Math.max(1, Math.round(heightCm * PX_PER_CM));
    const dpr = doc?.defaultView?.devicePixelRatio || 1;

    canvas.width = Math.max(1, Math.round(widthPx * dpr));
    canvas.height = Math.max(1, Math.round(heightPx * dpr));
    canvas.style.width = `${widthCm}cm`;
    canvas.style.height = `${heightCm}cm`;
    canvas.style.display = 'block';
    canvas.style.boxSizing = 'border-box';
    canvas.style.background = '#ffffff';
    canvas.style.border = '2px solid #000000';

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, widthPx, heightPx);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, widthPx, heightPx);

    const pxPerMm = PX_PER_CM / 10;

    for (let i = 0; i <= Math.ceil(widthPx / pxPerMm); i++) {
        const x = i * pxPerMm + 0.5;
        if (i % 10 === 0) {
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 2;
        } else if (i % 5 === 0) {
            ctx.strokeStyle = 'rgba(17,24,39,0.9)';
            ctx.lineWidth = 1;
        } else {
            ctx.strokeStyle = 'rgba(156,163,175,0.6)';
            ctx.lineWidth = 1;
        }
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, heightPx);
        ctx.stroke();
    }

    for (let j = 0; j <= Math.ceil(heightPx / pxPerMm); j++) {
        const y = j * pxPerMm + 0.5;
        if (j % 10 === 0) {
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 2;
        } else if (j % 5 === 0) {
            ctx.strokeStyle = 'rgba(17,24,39,0.9)';
            ctx.lineWidth = 1;
        } else {
            ctx.strokeStyle = 'rgba(156,163,175,0.6)';
            ctx.lineWidth = 1;
        }
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(widthPx, y);
        ctx.stroke();
    }

    ctx.lineWidth = 2;
    ctx.strokeStyle = '#000000';
    ctx.strokeRect(0, 0, widthPx, heightPx);
}

function drawAnswerLines(doc, lineConfig, lineId) {
    const wrapper = doc.createElement('div');
    wrapper.className = 'print-answer-lines';
    wrapper.style.margin = '8px 0';
    wrapper.style.maxWidth = '700px';

    const numberOfLines = Number.isFinite(Number(lineConfig?.numberOfLines)) ? Number(lineConfig.numberOfLines) : 5;
    const lineHeight = Number.isFinite(Number(lineConfig?.lineHeight)) ? Number(lineConfig.lineHeight) : 30;
    const lineStyle = lineConfig?.lineStyle || 'dotted';
    const opacity = Number.isFinite(Number(lineConfig?.opacity)) ? Number(lineConfig.opacity) : 0.5;

    if (!lineConfig) {
        const fallback = doc.createElement('div');
        fallback.textContent = `Answer Lines (ID: ${Number(lineId).toFixed(0)})`;
        fallback.style.fontSize = '11px';
        fallback.style.color = '#92400e';
        fallback.style.marginBottom = '4px';
        fallback.style.padding = '4px 0';
        wrapper.appendChild(fallback);
    }

    const fullLines = Math.max(0, Math.floor(numberOfLines));
    const hasHalfLine = numberOfLines % 1 !== 0;

    for (let i = 0; i < fullLines; i++) {
        const line = doc.createElement('div');
        line.style.height = `${lineHeight}px`;
        line.style.width = '100%';
        line.style.margin = '0';
        line.style.padding = '0';
        line.style.boxSizing = 'border-box';
        line.style.borderBottom = `2px ${lineStyle} rgba(0, 0, 0, ${opacity})`;
        wrapper.appendChild(line);
    }

    if (hasHalfLine) {
        const half = doc.createElement('div');
        half.style.height = `${lineHeight / 2}px`;
        half.style.width = '100%';
        half.style.margin = '0';
        half.style.padding = '0';
        half.style.boxSizing = 'border-box';
        half.style.borderBottom = `2px ${lineStyle} rgba(0, 0, 0, ${opacity})`;
        wrapper.appendChild(half);
    }

    return wrapper;
}

function preparePrintableContent(root, docParam, images = [], imagePositions = {}, answerLines = []) {
    const doc = root?.ownerDocument || docParam || document;
    if (!doc || !root) return;

    const answerLinesById = new Map((answerLines || []).map((line) => [Number(line?.id), line]));

    const nodeFilter = doc.defaultView?.NodeFilter?.SHOW_TEXT || 4;
    const walker = doc.createTreeWalker(root, nodeFilter);
    const textNodes = [];

    let currentNode = walker.nextNode();
    while (currentNode) {
        textNodes.push(currentNode);
        currentNode = walker.nextNode();
    }

    textNodes.forEach((textNode) => {
        const value = textNode.nodeValue || '';
        // If no graph or image tokens present quickly continue
        if (!GRAPH_TOKEN_RE.test(value) && !IMAGE_TOKEN_NEW_RE.test(value) && !IMAGE_TOKEN_OLD_RE.test(value) && !LINES_TOKEN_RE.test(value)) return;

        // Reset regex states
        GRAPH_TOKEN_RE.lastIndex = 0;
        IMAGE_TOKEN_NEW_RE.lastIndex = 0;
        IMAGE_TOKEN_OLD_RE.lastIndex = 0;
        LINES_TOKEN_RE.lastIndex = 0;

        const fragment = doc.createDocumentFragment();
        let lastIndex = 0;
        // Combined regex to find either token sequentially
        const combined = new RegExp(`${GRAPH_TOKEN_RE.source}|${LINES_TOKEN_RE.source}|${IMAGE_TOKEN_NEW_RE.source}|${IMAGE_TOKEN_OLD_RE.source}`, 'g');
        let match;

        while ((match = combined.exec(value)) !== null) {
            if (match.index > lastIndex) {
                fragment.appendChild(doc.createTextNode(value.slice(lastIndex, match.index)));
            }

            const token = match[0];

            // Graph token
            if (GRAPH_TOKEN_RE.test(token)) {
                const graphData = parseGraphToken(token);
                if (graphData) {
                    const canvas = doc.createElement('canvas');
                    drawGraphPaperCanvas(canvas, graphData.widthCm, graphData.heightCm, doc);
                    const wrapper = doc.createElement('span');
                    wrapper.style.display = 'inline-block';
                    wrapper.style.verticalAlign = 'middle';
                    wrapper.style.margin = '8px 4px';
                    wrapper.appendChild(canvas);
                    fragment.appendChild(wrapper);
                } else {
                    fragment.appendChild(doc.createTextNode(token));
                }
            }

            // Answer lines token
            else if (LINES_TOKEN_RE.test(token)) {
                const lineMatch = token.match(/\[LINES:([\d.]+)\]/);
                const lineId = lineMatch ? Number(lineMatch[1]) : NaN;
                const lineConfig = answerLinesById.get(lineId);
                fragment.appendChild(drawAnswerLines(doc, lineConfig, lineId));
            }

            // Image token (new format)
            else if (IMAGE_TOKEN_NEW_RE.test(token) || IMAGE_TOKEN_OLD_RE.test(token)) {
                // extract id and dimensions
                let idMatch = token.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
                let oldMatch = token.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
                const imageId = parseFloat(idMatch ? idMatch[1] : (oldMatch ? oldMatch[1] : NaN));
                const w = idMatch ? parseInt(idMatch[2], 10) : (oldMatch ? parseInt(oldMatch[2], 10) : null);
                const h = idMatch ? parseInt(idMatch[3], 10) : null;

                const image = (images || []).find(i => Math.abs(i.id - imageId) < 0.001);
                const pos = (imagePositions || {})[imageId];

                if (image) {
                    const imgEl = doc.createElement('img');
                    imgEl.src = image.url;
                    imgEl.alt = image.name || 'image';
                    if (w) imgEl.style.width = `${w}px`;
                    if (h) imgEl.style.height = `${h}px`;
                    imgEl.style.display = 'block';
                    imgEl.className = 'print-inline-image';

                    const wrapper = doc.createElement('span');
                    wrapper.style.display = pos ? 'block' : 'inline-block';
                    wrapper.style.margin = '8px 4px';
                    if (pos) {
                        wrapper.style.position = 'absolute';
                        wrapper.style.left = `${pos.x}px`;
                        wrapper.style.top = `${pos.y}px`;
                    }
                    wrapper.appendChild(imgEl);
                    fragment.appendChild(wrapper);
                } else {
                    fragment.appendChild(doc.createTextNode(token));
                }
            }

            lastIndex = match.index + token.length;
            // reset inner regex states for next loop
            GRAPH_TOKEN_RE.lastIndex = 0;
            LINES_TOKEN_RE.lastIndex = 0;
            IMAGE_TOKEN_NEW_RE.lastIndex = 0;
            IMAGE_TOKEN_OLD_RE.lastIndex = 0;
        }

        if (lastIndex < value.length) {
            fragment.appendChild(doc.createTextNode(value.slice(lastIndex)));
        }

        textNode.parentNode?.replaceChild(fragment, textNode);
    });
}

export default function PrintableDocumentModal({ isOpen, onClose, htmlContent, topicName, paperName, images = [], imagePositions = {}, answerLines = [] }) {
    const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
    
    if (!isOpen) return null;

    const handlePrint = () => {
        const iframe = document.getElementById('printable-document-iframe');
        if (iframe && iframe.contentWindow) {
            try {
                if (iframe.contentDocument?.body) {
                    preparePrintableContent(iframe.contentDocument.body, iframe.contentDocument, images, imagePositions, answerLines);
                }
                // Try to print the iframe
                iframe.contentWindow.focus();
                iframe.contentWindow.print();
            } catch (error) {
                handlePrintInNewWindow();
            }
        }
    };

    const handlePrintInNewWindow = () => {
        if (!htmlContent) return;
        
        // Open content in new window for printing
        const printWindow = window.open('', '_blank');
        if (printWindow) {
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>${topicName || paperName || 'Questions'}</title>
                    <style>
                        body { 
                            margin:5px; 
                            font-family: Arial, sans-serif; 
                            background: white;
                        }
                        @media print {
                            body { margin: 15mm; }
                        }
                    </style>
                </head>
                <body>
                    ${htmlContent}
                </body>
                </html>
            `);
            printWindow.document.close();
            if (printWindow.document.body) {
                preparePrintableContent(printWindow.document.body, printWindow.document, images, imagePositions, answerLines);
            }
            printWindow.focus();
            
            // Wait for content to load before printing
            setTimeout(() => {
                printWindow.print();
            }, 250);
        }
    };

    const handleDownload = async () => {
        if (!htmlContent || isGeneratingPdf) return;
        
        try {
            setIsGeneratingPdf(true);
            
            // Get content from the iframe that's already rendered
            const iframe = document.getElementById('printable-document-iframe');
            if (!iframe || !iframe.contentWindow || !iframe.contentDocument) {
                throw new Error('Unable to access document content');
            }
            
            // Get the body content from the iframe
            const iframeBody = iframe.contentDocument.body;
            if (!iframeBody) {
                throw new Error('No content found in document');
            }
            
            // Clone the content to avoid modifying the original
            const contentClone = iframeBody.cloneNode(true);
            preparePrintableContent(contentClone, iframe.contentDocument, images, imagePositions, answerLines);
            
            // Create a temporary container with proper styling
            const tempContainer = document.createElement('div');
            tempContainer.style.position = 'absolute';
            tempContainer.style.left = '-9999px';
            tempContainer.style.top = '0';
            tempContainer.style.width = '210mm'; // A4 width
            tempContainer.style.padding = '5px';
            tempContainer.style.background = 'white';
            tempContainer.style.border = 'none';
            tempContainer.style.fontFamily = 'Arial, sans-serif';
            tempContainer.appendChild(contentClone);
            document.body.appendChild(tempContainer);
            
            // Wait a bit for content to be fully ready
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Configure PDF options
            const options = {
                margin: [10, 10, 10, 10],
                filename: `${topicName || paperName || 'questions'}.pdf`,
                image: { type: 'jpeg', quality: 0.95 },
                html2canvas: { 
                    scale: 2,
                    useCORS: true,
                    letterRendering: true,
                    logging: false,
                    backgroundColor: '#ffffff'
                },
                jsPDF: { 
                    unit: 'mm', 
                    format: 'a4', 
                    orientation: 'portrait',
                    compress: true
                },
                pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
            };
            
            // Generate and download PDF
            await html2pdf().set(options).from(tempContainer).save();
            
            // Cleanup
            document.body.removeChild(tempContainer);
        } catch (error) {
            alert(`Failed to generate PDF: ${error.message}. Please try using the Print button instead.`);
        } finally {
            setIsGeneratingPdf(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
            <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                {/* Background overlay */}
                <div 
                    className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
                    aria-hidden="true"
                    onClick={onClose}
                ></div>

                {/* Center modal */}
                <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

                {/* Modal panel */}
                <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-6xl sm:w-full">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-lg leading-6 font-bold text-white" id="modal-title">
                                    📄 Printable Document
                                </h3>
                                {topicName && paperName && (
                                    <p className="mt-1 text-sm text-purple-100">
                                        {topicName} - {paperName}
                                    </p>
                                )}
                            </div>
                            <button
                                onClick={onClose}
                                className="text-white hover:text-gray-200 transition"
                            >
                                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
                        <div className="flex justify-end gap-3">
                            <button
                                onClick={handlePrintInNewWindow}
                                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                            >
                                <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                                Open in New Tab
                            </button>
                            
                            <button
                                onClick={handlePrint}
                                className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            >
                                <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                                </svg>
                                Print
                            </button>
                        </div>
                    </div>

                    {/* Content */}
                    <div className="bg-white px-6 py-4" style={{ maxHeight: '70vh', overflow: 'auto' }}>
                        {htmlContent ? (
                            <iframe
                                id="printable-document-iframe"
                                srcDoc={htmlContent}
                                className="w-full border-2 border-gray-300 rounded-lg bg-white"
                                style={{ minHeight: '600px', height: '100%' }}
                                title="Printable Document"
                                sandbox="allow-same-origin allow-scripts allow-modals allow-popups"
                                onLoad={(e) => {
                                    // Ensure iframe content is accessible
                                    const iframe = e.target;
                                    if (iframe.contentDocument) {
                                        if (iframe.contentDocument.body) {
                                            preparePrintableContent(iframe.contentDocument.body, iframe.contentDocument, images, imagePositions, answerLines);
                                        }
                                        iframe.contentDocument.body.style.margin = '5px';
                                        iframe.contentDocument.body.style.fontFamily = 'Arial, sans-serif';
                                    }
                                }}
                            />
                        ) : (
                            <div className="flex items-center justify-center py-12">
                                <div className="text-center">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                                    <p className="mt-4 text-gray-600">Loading document...</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="bg-gray-50 px-6 py-3 sm:flex sm:flex-row-reverse border-t border-gray-200">
                        <button
                            type="button"
                            onClick={onClose}
                            className="w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
                        >
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
