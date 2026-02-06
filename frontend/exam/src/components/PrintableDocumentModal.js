import React, { useState } from 'react';
import html2pdf from 'html2pdf.js';

export default function PrintableDocumentModal({ isOpen, onClose, htmlContent, topicName, paperName }) {
    const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
    
    if (!isOpen) return null;

    const handlePrint = () => {
        const iframe = document.getElementById('printable-document-iframe');
        if (iframe && iframe.contentWindow) {
            try {
                // Try to print the iframe
                iframe.contentWindow.focus();
                iframe.contentWindow.print();
            } catch (error) {
                console.error('Print error:', error);
                // Fallback: open in new window
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
                            margin: 20px; 
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
            
            // Create a temporary container with proper styling
            const tempContainer = document.createElement('div');
            tempContainer.style.position = 'absolute';
            tempContainer.style.left = '-9999px';
            tempContainer.style.top = '0';
            tempContainer.style.width = '210mm'; // A4 width
            tempContainer.style.padding = '20px';
            tempContainer.style.background = 'white';
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
            console.error('Error generating PDF:', error);
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
                                onClick={handleDownload}
                                disabled={isGeneratingPdf}
                                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isGeneratingPdf ? (
                                    <>
                                        <svg className="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Generating PDF...
                                    </>
                                ) : (
                                    <>
                                        <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                        </svg>
                                        Download PDF
                                    </>
                                )}
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
                                        iframe.contentDocument.body.style.margin = '20px';
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
