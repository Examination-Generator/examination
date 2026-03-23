import { useState, useEffect, useRef } from 'react';
import * as messagingService from '../services/messagingService';
import AlertModal from './AlertModal';

export default function UserMessagingFloat() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [selectedMessage, setSelectedMessage] = useState(null);
    const [conversation, setConversation] = useState(null);
    const [messageSubject, setMessageSubject] = useState('');
    const [messageText, setMessageText] = useState('');
    const [replyText, setReplyText] = useState('');
    const [isSending, setIsSending] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);
    const [showNewMessage, setShowNewMessage] = useState(false);
    const [forceNewConversation, setForceNewConversation] = useState(false);
    const messageEndRef = useRef(null);
    
    // Alert modal state
    const [showAlert, setShowAlert] = useState(false);
    const [alertConfig, setAlertConfig] = useState({ title: '', message: '', type: 'info' });

    // Debug: Log component mount
    useEffect(() => {
        console.log('UserMessagingFloat component mounted');
    }, []);

    useEffect(() => {
        loadUnreadCount();
        
        // Poll frequently so support conversation updates feel near real-time.
        const interval = setInterval(() => {
            loadUnreadCount();
            if (!isOpen) {
                return;
            }

            if (selectedMessage) {
                loadConversation(selectedMessage.id, true);
            } else {
                loadMessages(true);
            }
        }, 5000);

        return () => clearInterval(interval);
    }, [isOpen, selectedMessage]);

    useEffect(() => {
        if (isOpen && !selectedMessage) {
            loadMessages();
        }
    }, [isOpen]);

    useEffect(() => {
        // Keep user chat continuous by default: open latest thread automatically.
        if (isOpen && !showNewMessage && !selectedMessage && messages.length > 0) {
            openMessage(messages[0]);
        }
    }, [isOpen, showNewMessage, selectedMessage, messages]);

    useEffect(() => {
        messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    const loadUnreadCount = async () => {
        try {
            const count = await messagingService.getUnreadMessageCount();
            setUnreadCount(count);
        } catch (error) {
            console.error('Failed to load unread count:', error);
        }
    };

    const loadMessages = async (silent = false) => {
        if (!silent) setIsLoading(true);
        try {
            const data = await messagingService.getSystemMessages();
            const nextMessages = data || [];
            setMessages(nextMessages);
            return nextMessages;
        } catch (error) {
            console.error('Failed to load messages:', error);
            return [];
        } finally {
            if (!silent) setIsLoading(false);
        }
    };

    const openMessage = async (message) => {
        setSelectedMessage(message);
        try {
            await loadConversation(message.id);
        } catch (error) {
            console.error('Failed to load conversation:', error);
        }
    };

    const loadConversation = async (messageId, silent = false) => {
        try {
            const conv = await messagingService.getSystemMessageConversation(messageId);
            setConversation(conv);

            // Keep list/badges in sync after read-state updates on the backend.
            await loadMessages(silent);
            await loadUnreadCount();
        } catch (error) {
            console.error('Failed to load conversation:', error);
        }
    };

    const sendNewMessage = async () => {
        if (!messageText.trim()) {
            return;
        }

        setIsSending(true);
        try {
            const latestConversationId = selectedMessage?.id || messages?.[0]?.id;
            let createdConversationId = null;

            if (latestConversationId && !forceNewConversation) {
                await messagingService.replyToSystemMessage(latestConversationId, {
                    message: messageText
                });
            } else {
                const created = await messagingService.sendSystemMessage({
                    subject: messageSubject.trim() || 'Support Request',
                    message: messageText
                });
                createdConversationId = created?.id || null;
            }

            setMessageSubject('');
            setMessageText('');
            setShowNewMessage(false);
            setForceNewConversation(false);
            
            const refreshedMessages = await loadMessages();

            // Move into conversation view after first send/reply for continuous to-and-fro chat.
            const targetConversationId = latestConversationId || createdConversationId || refreshedMessages?.[0]?.id;
            if (targetConversationId) {
                await loadConversation(targetConversationId, true);
            }
            
        } catch (error) {
            console.error('Failed to send message:', error);
            setAlertConfig({
                title: 'Error',
                message: 'Failed to send message. Please try again.',
                type: 'error'
            });
            setShowAlert(true);
        } finally {
            setIsSending(false);
        }
    };

    const sendReply = async () => {
        if (!replyText.trim() || !selectedMessage) {
            return;
        }

        setIsSending(true);
        try {
            await messagingService.replyToSystemMessage(selectedMessage.id, {
                message: replyText
            });

            // Reload conversation
            await loadConversation(selectedMessage.id, true);
            
            setReplyText('');
            
            // Reload messages list
            await loadMessages(true);
        } catch (error) {
            console.error('Failed to send reply:', error);
            setAlertConfig({
                title: 'Error',
                message: 'Failed to send reply. Please try again.',
                type: 'error'
            });
            setShowAlert(true);
        } finally {
            setIsSending(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const hours = diff / (1000 * 60 * 60);
        
        if (hours < 24) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else if (hours < 168) {
            return date.toLocaleDateString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' });
        } else {
            return date.toLocaleDateString();
        }
    };

    const ReadReceipt = ({ seen }) => (
        <span className={`inline-flex items-center gap-0.5 ${seen ? 'text-blue-600' : 'text-gray-400'}`} title={seen ? 'Seen' : 'Sent'}>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {seen && (
                <svg className="w-3 h-3 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
            )}
        </span>
    );

    return (
        <>
            {/* Floating Button */}
            <div className="fixed bottom-6 right-6 z-50 print:hidden">
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className="relative bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-full p-4 shadow-2xl transition-all transform hover:scale-110"
                    title="Support Messages"
                >
                    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    
                    {unreadCount > 0 && (
                        <span className="absolute -top-2 -right-2 bg-red-600 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center animate-pulse">
                            {unreadCount > 9 ? '9+' : unreadCount}
                        </span>
                    )}
                </button>
            </div>

            {/* Messaging Panel */}
            {isOpen && (
                <div className="fixed bottom-6 left-[10%] right-[10%] sm:left-auto sm:right-6 z-50 w-[80%] sm:w-[460px] md:w-[520px] max-w-2xl h-[85vh] max-h-[36rem] bg-white rounded-xl shadow-2xl flex flex-col overflow-hidden border-2 border-gray-200 print:hidden">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-green-600 to-green-700 p-4 flex items-center justify-between">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                            </svg>
                            Support Messages
                        </h3>
                        <button
                            onClick={() => {
                                setIsOpen(false);
                                setSelectedMessage(null);
                                setConversation(null);
                                setShowNewMessage(false);
                            }}
                            className="text-white hover:bg-green-800 rounded-full p-1 transition"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Content */}
                    <div className="flex-1 overflow-hidden flex flex-col">
                        {showNewMessage ? (
                            // New Message Form
                            <div className="flex-1 flex flex-col p-4">
                                <div className="flex items-center justify-between mb-4">
                                    <h4 className="font-bold text-gray-900">New Message</h4>
                                    <button
                                        onClick={() => {
                                            setShowNewMessage(false);
                                            setForceNewConversation(false);
                                        }}
                                        className="text-gray-500 hover:text-gray-700"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                        </svg>
                                    </button>
                                </div>

                                <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-1">
                                            Subject (Optional)
                                        </label>
                                        <input
                                            type="text"
                                            value={messageSubject}
                                            onChange={(e) => setMessageSubject(e.target.value)}
                                            placeholder="Enter subject..."
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                        />
                                    </div>

                                    <div className="flex-1">
                                        <label className="block text-sm font-bold text-gray-700 mb-1">
                                            Message
                                        </label>
                                        <textarea
                                            value={messageText}
                                            onChange={(e) => setMessageText(e.target.value)}
                                            placeholder="Describe your issue or question..."
                                            rows={10}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                                        />
                                    </div>
                                </div>

                                <button
                                    onClick={sendNewMessage}
                                    disabled={isSending || !messageText.trim()}
                                    className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white py-2 rounded-lg font-bold transition flex items-center justify-center gap-2 mt-4 flex-shrink-0"
                                >
                                    {isSending ? (
                                        <>
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                            Sending...
                                        </>
                                    ) : (
                                        <>
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                            </svg>
                                            Send Message
                                        </>
                                    )}
                                </button>
                            </div>
                        ) : selectedMessage ? (
                            // Conversation View
                            <>
                                <div className="bg-gray-50 p-3 border-b border-gray-200">
                                    <button
                                        onClick={() => {
                                            setSelectedMessage(null);
                                            setConversation(null);
                                        }}
                                        className="text-gray-600 hover:text-gray-900 flex items-center gap-2 mb-2"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                        </svg>
                                        Back to messages
                                    </button>
                                    <p className="font-semibold text-gray-900 text-sm">{selectedMessage.subject || 'No subject'}</p>
                                </div>

                                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                                    {!conversation ? (
                                        <div className="flex justify-center items-center h-full">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                                        </div>
                                    ) : (
                                        <>
                                            {/* Original Message (sender - left) */}
                                            <div className="flex justify-start">
                                                <div className="w-[85%] bg-blue-50 rounded-2xl p-3 border-l-4 border-blue-600 shadow-sm">
                                                    <div className="flex items-center justify-between mb-1">
                                                        <p className="text-xs text-gray-500">You • {formatDate(conversation.created_at)}</p>
                                                        <ReadReceipt seen={conversation.is_read} />
                                                    </div>
                                                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{conversation.message}</p>
                                                </div>
                                            </div>

                                            {/* Replies */}
                                            {conversation.replies && conversation.replies.map((reply, idx) => (
                                                <div key={idx} className={`flex ${reply.is_from_admin ? 'justify-end' : 'justify-start'}`}>
                                                    <div
                                                        className={`w-[85%] rounded-2xl p-3 border-l-4 shadow-sm ${
                                                            reply.is_from_admin
                                                                ? 'bg-green-50 border-green-600'
                                                                : 'bg-blue-50 border-blue-600'
                                                        }`}
                                                    >
                                                        <p className="text-xs text-gray-600 mb-1 font-semibold">
                                                            {reply.is_from_admin ? 'Admin' : 'You'} • {formatDate(reply.created_at)}
                                                        </p>
                                                        {!reply.is_from_admin && (
                                                            <div className="mb-1">
                                                                <ReadReceipt seen={reply.is_read} />
                                                            </div>
                                                        )}
                                                        {reply.quoted_text && (
                                                            <div className="bg-white bg-opacity-50 border-l-2 border-gray-400 pl-2 py-1 mb-2">
                                                                <p className="text-xs text-gray-600 italic">"{reply.quoted_text}"</p>
                                                            </div>
                                                        )}
                                                        <p className="text-sm text-gray-700 whitespace-pre-wrap">{reply.message}</p>
                                                    </div>
                                                </div>
                                            ))}
                                            <div ref={messageEndRef} />
                                        </>
                                    )}
                                </div>

                                <div className="p-3 border-t border-gray-200 flex-shrink-0">
                                    <div className="flex items-end gap-2">
                                        <textarea
                                            value={replyText}
                                            onChange={(e) => setReplyText(e.target.value)}
                                            placeholder="Type a reply..."
                                            rows={2}
                                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none text-sm"
                                            onKeyPress={(e) => {
                                                if (e.key === 'Enter' && !e.shiftKey) {
                                                    e.preventDefault();
                                                    sendReply();
                                                }
                                            }}
                                        />
                                        <button
                                            onClick={sendReply}
                                            disabled={isSending || !replyText.trim()}
                                            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white p-2 rounded-lg transition flex-shrink-0"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </>
                        ) : (
                            // Messages List
                            <>
                                <div className="p-3 border-b border-gray-200">
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => {
                                                if (messages.length > 0) {
                                                    openMessage(messages[0]);
                                                    return;
                                                }
                                                setForceNewConversation(true);
                                                setShowNewMessage(true);
                                            }}
                                            className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg font-bold transition flex items-center justify-center gap-2"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                            </svg>
                                            {messages.length > 0 ? 'Continue Conversation' : 'New Message'}
                                        </button>
                                        {messages.length > 0 && (
                                            <button
                                                onClick={() => {
                                                    setForceNewConversation(true);
                                                    setShowNewMessage(true);
                                                }}
                                                className="px-3 py-2 rounded-lg border border-green-600 text-green-700 hover:bg-green-50 text-xs font-semibold"
                                                title="Start a separate conversation"
                                            >
                                                New Thread
                                            </button>
                                        )}
                                    </div>
                                </div>

                                <div className="flex-1 overflow-y-auto">
                                    {isLoading ? (
                                        <div className="flex justify-center items-center h-full">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                                        </div>
                                    ) : messages.length === 0 ? (
                                        <div className="p-6 text-center text-gray-500">
                                            <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                                            </svg>
                                            <p className="font-semibold">No messages</p>
                                            <p className="text-xs mt-1">Start a conversation</p>
                                        </div>
                                    ) : (
                                        <div className="divide-y divide-gray-200">
                                            {messages.map(message => {
                                                const hasUnreadIncoming = (message.unread_replies_count || 0) > 0;

                                                return (
                                                <button
                                                    key={message.id}
                                                    onClick={() => openMessage(message)}
                                                    className={`w-full text-left p-3 hover:bg-gray-50 transition relative ${
                                                        hasUnreadIncoming ? 'bg-blue-50' : ''
                                                    }`}
                                                >
                                                    {hasUnreadIncoming && (
                                                        <div className="absolute top-3 left-1 w-2 h-2 bg-blue-600 rounded-full"></div>
                                                    )}
                                                    <div className="ml-3">
                                                        <div className="flex justify-between items-start mb-1">
                                                            <p className={`text-sm font-semibold text-gray-900 truncate ${hasUnreadIncoming ? 'font-bold' : ''}`}>
                                                                {message.subject || 'No subject'}
                                                            </p>
                                                            <span className="text-xs text-gray-500 ml-2">
                                                                {formatDate(message.created_at)}
                                                            </span>
                                                        </div>
                                                        <p className="text-xs text-gray-600 truncate">{message.message}</p>
                                                        <div className="mt-1 flex items-center justify-between">
                                                            {(message.unread_replies_count || 0) > 0 ? (
                                                                <span className="text-[11px] font-semibold text-blue-700 bg-blue-100 rounded-full px-2 py-0.5">
                                                                    {message.unread_replies_count} {message.unread_replies_count > 1 ? 'new replies' : 'new reply'}
                                                                </span>
                                                            ) : (
                                                                <span className="text-[11px] text-gray-500">No new reply</span>
                                                            )}
                                                            <span className="inline-flex items-center gap-1 text-[11px] text-gray-500">
                                                                <ReadReceipt seen={message.is_read} />
                                                            </span>
                                                        </div>
                                                        {message.replies_count > 0 && (
                                                            <div className="mt-1 flex items-center gap-1 text-xs text-green-600">
                                                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                                                                </svg>
                                                                {message.replies_count}
                                                            </div>
                                                        )}
                                                    </div>
                                                </button>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
            
            {/* Alert Modal */}
            <AlertModal
                isOpen={showAlert}
                onClose={() => setShowAlert(false)}
                title={alertConfig.title}
                message={alertConfig.message}
                type={alertConfig.type}
            />
        </>
    );
}
                                                        </div>
                                                    )}
                                                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{reply.message}</p>
                                                </div>
                                            ))}
                                            <div ref={messageEndRef} />
                                        </>
                                    )}
                                </div>

                                <div className="p-3 border-t border-gray-200 flex-shrink-0">
                                    <div className="flex items-end gap-2">
                                        <textarea
                                            value={replyText}
                                            onChange={(e) => setReplyText(e.target.value)}
                                            placeholder="Type a reply..."
                                            rows={2}
                                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none text-sm"
                                            onKeyPress={(e) => {
                                                if (e.key === 'Enter' && !e.shiftKey) {
                                                    e.preventDefault();
                                                    sendReply();
                                                }
                                            }}
                                        />
                                        <button
                                            onClick={sendReply}
                                            disabled={isSending || !replyText.trim()}
                                            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white p-2 rounded-lg transition flex-shrink-0"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </>
                        ) : (
                            // Messages List
                            <>
                                <div className="p-3 border-b border-gray-200">
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => {
                                                if (messages.length > 0) {
                                                    openMessage(messages[0]);
                                                    return;
                                                }
                                                setForceNewConversation(true);
                                                setShowNewMessage(true);
                                            }}
                                            className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg font-bold transition flex items-center justify-center gap-2"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                            </svg>
                                            {messages.length > 0 ? 'Continue Conversation' : 'New Message'}
                                        </button>
                                        {messages.length > 0 && (
                                            <button
                                                onClick={() => {
                                                    setForceNewConversation(true);
                                                    setShowNewMessage(true);
                                                }}
                                                className="px-3 py-2 rounded-lg border border-green-600 text-green-700 hover:bg-green-50 text-xs font-semibold"
                                                title="Start a separate conversation"
                                            >
                                                New Thread
                                            </button>
                                        )}
                                    </div>
                                </div>

                                <div className="flex-1 overflow-y-auto">
                                    {isLoading ? (
                                        <div className="flex justify-center items-center h-full">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                                        </div>
                                    ) : messages.length === 0 ? (
                                        <div className="p-6 text-center text-gray-500">
                                            <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                                            </svg>
                                            <p className="font-semibold">No messages</p>
                                            <p className="text-xs mt-1">Start a conversation</p>
                                        </div>
                                    ) : (
                                        <div className="divide-y divide-gray-200">
                                            {messages.map(message => {
                                                const hasUnreadIncoming = (message.unread_replies_count || 0) > 0;

                                                return (
                                                <button
                                                    key={message.id}
                                                    onClick={() => openMessage(message)}
                                                    className={`w-full text-left p-3 hover:bg-gray-50 transition relative ${
                                                        hasUnreadIncoming ? 'bg-blue-50' : ''
                                                    }`}
                                                >
                                                    {hasUnreadIncoming && (
                                                        <div className="absolute top-3 left-1 w-2 h-2 bg-blue-600 rounded-full"></div>
                                                    )}
                                                    <div className="ml-3">
                                                        <div className="flex justify-between items-start mb-1">
                                                            <p className={`text-sm font-semibold text-gray-900 truncate ${hasUnreadIncoming ? 'font-bold' : ''}`}>
                                                                {message.subject || 'No subject'}
                                                            </p>
                                                            <span className="text-xs text-gray-500 ml-2">
                                                                {formatDate(message.created_at)}
                                                            </span>
                                                        </div>
                                                        <p className="text-xs text-gray-600 truncate">{message.message}</p>
                                                        <div className="mt-1 flex items-center justify-between">
                                                            {(message.unread_replies_count || 0) > 0 ? (
                                                                <span className="text-[11px] font-semibold text-blue-700 bg-blue-100 rounded-full px-2 py-0.5">
                                                                    {message.unread_replies_count} {message.unread_replies_count > 1 ? 'new replies' : 'new reply'}
                                                                </span>
                                                            ) : (
                                                                <span className="text-[11px] text-gray-500">No new reply</span>
                                                            )}
                                                            <span className="inline-flex items-center gap-1 text-[11px] text-gray-500">
                                                                <ReadReceipt seen={message.is_read} />
                                                            </span>
                                                        </div>
                                                        {message.replies_count > 0 && (
                                                            <div className="mt-1 flex items-center gap-1 text-xs text-green-600">
                                                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                                                                </svg>
                                                                {message.replies_count}
                                                            </div>
                                                        )}
                                                    </div>
                                                </button>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
            
            {/* Alert Modal */}
            <AlertModal
                isOpen={showAlert}
                onClose={() => setShowAlert(false)}
                title={alertConfig.title}
                message={alertConfig.message}
                type={alertConfig.type}
            />
        </>
    );
}
