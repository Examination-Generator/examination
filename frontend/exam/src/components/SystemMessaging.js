import { useState, useEffect, useRef } from 'react';
import * as messagingService from '../services/messagingService';
import AlertModal from './AlertModal';
import ConfirmModal from './ConfirmModal';

export default function SystemMessaging() {
    const [messages, setMessages] = useState([]);
    const [selectedMessage, setSelectedMessage] = useState(null);
    const [conversation, setConversation] = useState(null);
    const [replyText, setReplyText] = useState('');
    const [quotedText, setQuotedText] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isSending, setIsSending] = useState(false);
    const [showUnreadOnly, setShowUnreadOnly] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);
    const messageEndRef = useRef(null);
    
    // Alert modal state
    const [showAlert, setShowAlert] = useState(false);
    const [alertConfig, setAlertConfig] = useState({ title: '', message: '', type: 'info' });
    
    // Confirm modal state
    const [showConfirm, setShowConfirm] = useState(false);
    const [confirmConfig, setConfirmConfig] = useState({ title: '', message: '', onConfirm: null });

    useEffect(() => {
        loadMessages();
        loadUnreadCount();
        
        // Poll frequently so admin can see new support traffic quickly.
        const interval = setInterval(() => {
            if (selectedMessage) {
                loadConversation(selectedMessage.id, true);
            } else {
                loadMessages(true);
            }
            loadUnreadCount();
        }, 5000);

        return () => clearInterval(interval);
    }, [showUnreadOnly, selectedMessage]);

    useEffect(() => {
        messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    const loadMessages = async (silent = false) => {
        if (!silent) setIsLoading(true);
        try {
            const baseData = await messagingService.getSystemMessages(
                showUnreadOnly ? { unreadOnly: true } : {}
            );

            if (showUnreadOnly) {
                setMessages(baseData || []);
                return;
            }

            if (baseData && baseData.length > 0) {
                setMessages(baseData);
                return;
            }

            // Recovery path: keep list visible when only unread endpoint returns data.
            const unreadData = await messagingService.getSystemMessages({ unreadOnly: true });
            const merged = [...(baseData || []), ...(unreadData || [])];
            const uniqueById = Array.from(new Map(merged.map(item => [item.id, item])).values());
            setMessages(uniqueById);
        } catch (error) {
            console.error('Failed to load messages:', error);
        } finally {
            if (!silent) setIsLoading(false);
        }
    };

    const loadUnreadCount = async () => {
        try {
            const count = await messagingService.getUnreadMessageCount();
            setUnreadCount(count);
        } catch (error) {
            console.error('Failed to load unread count:', error);
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
            await loadMessages(silent);
            await loadUnreadCount();
        } catch (error) {
            console.error('Failed to load conversation:', error);
        }
    };

    const handleQuoteText = () => {
        const selectedText = window.getSelection().toString();
        if (selectedText) {
            setQuotedText(selectedText);
        }
    };

    const sendReply = async () => {
        if (!replyText.trim() || !selectedMessage) {
            return;
        }

        setIsSending(true);
        try {
            await messagingService.replyToSystemMessage(selectedMessage.id, {
                message: replyText,
                quotedText: quotedText || undefined
            });

            // Reload conversation
            await loadConversation(selectedMessage.id, true);
            
            setReplyText('');
            setQuotedText('');
            
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

    const deleteMessage = async (messageId) => {
        setConfirmConfig({
            title: 'Delete Message',
            message: 'Are you sure you want to delete this message?',
            onConfirm: async () => {
                setShowConfirm(false);
                try {
                    await messagingService.deleteSystemMessage(messageId);
                    
                    if (selectedMessage?.id === messageId) {
                        setSelectedMessage(null);
                        setConversation(null);
                    }
                    
                    await loadMessages();
                    await loadUnreadCount();
                } catch (error) {
                    console.error('Failed to delete message:', error);
                    setAlertConfig({
                        title: 'Error',
                        message: 'Failed to delete message. Please try again.',
                        type: 'error'
                    });
                    setShowAlert(true);
                }
            }
        });
        setShowConfirm(true);
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
        <span className={`inline-flex items-center gap-0.5 ${seen ? 'text-blue-600' : 'text-gray-400'}`} title={seen ? 'Seen by user' : 'Sent'}>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <svg className="w-3 h-3 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
        </span>
    );

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-250px)]">
            {/* Left Panel: Messages Inbox */}
            <div className="lg:col-span-1 bg-white rounded-xl shadow-lg overflow-hidden flex flex-col">
                <div className="bg-gradient-to-r from-purple-600 to-purple-700 p-4">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            Support Messages
                        </h3>
                        <button
                            onClick={() => loadMessages()}
                            className="text-white hover:bg-purple-800 rounded-full p-2 transition"
                            title="Refresh"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                        </button>
                    </div>
                    
                    {/* Filter Toggle */}
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setShowUnreadOnly(!showUnreadOnly)}
                            className={`flex-1 py-2 px-3 rounded-lg font-semibold text-sm transition ${
                                showUnreadOnly
                                    ? 'bg-white text-purple-700'
                                    : 'bg-purple-800 text-white'
                            }`}
                        >
                            {showUnreadOnly ? 'Show All' : `Unread (${unreadCount})`}
                        </button>
                    </div>
                </div>
                
                <div className="flex-1 overflow-y-auto">
                    {isLoading ? (
                        <div className="flex justify-center items-center h-full">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                        </div>
                    ) : messages.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">
                            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                            </svg>
                            <p className="font-semibold">No messages</p>
                            <p className="text-sm mt-1">
                                {showUnreadOnly ? 'No unread messages' : 'No messages yet'}
                            </p>
                        </div>
                    ) : (
                        <div className="divide-y divide-gray-200">
                            {messages.map(message => {
                                const hasUnreadIncoming = (message.unread_replies_count || 0) > 0 || !message.is_read;
                                const displayIdentity = message.sender_name || message.sender_phone_number || 'Unknown User';
                                const avatarSeed = displayIdentity;
                                return (
                                <button
                                    key={message.id}
                                    onClick={() => openMessage(message)}
                                    className={`w-full text-left p-4 hover:bg-gray-50 transition relative ${
                                        selectedMessage?.id === message.id ? 'bg-purple-50' : ''
                                    } ${hasUnreadIncoming ? 'bg-blue-50' : ''}`}
                                >
                                    {hasUnreadIncoming && (
                                        <div className="absolute top-4 left-2 w-2 h-2 bg-blue-600 rounded-full"></div>
                                    )}
                                    <div className="flex items-start gap-3 ml-3">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center flex-shrink-0">
                                            <span className="text-white font-bold text-sm">
                                                {avatarSeed ? avatarSeed[0].toUpperCase() : 'U'}
                                            </span>
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex justify-between items-start mb-1">
                                                <p className={`font-semibold text-gray-900 truncate ${!message.is_read ? 'font-bold' : ''}`}>
                                                    {displayIdentity}
                                                </p>
                                                <span className="text-xs text-gray-500 ml-2">
                                                    {formatDate(message.created_at)}
                                                </span>
                                            </div>
                                            <p className={`text-sm truncate ${!message.is_read ? 'font-semibold text-gray-900' : 'text-gray-600'}`}>
                                                {message.subject || 'No subject'}
                                            </p>
                                            <p className="text-xs text-gray-500 truncate mt-1">
                                                {message.message}
                                            </p>
                                            {(message.unread_replies_count || 0) > 0 && (
                                                <div className="mt-2 inline-flex items-center text-xs font-semibold text-blue-700 bg-blue-100 rounded-full px-2 py-0.5">
                                                    {message.unread_replies_count} {message.unread_replies_count > 1 ? 'new replies' : 'new reply'}
                                                </div>
                                            )}
                                            {message.replies_count > 0 && (
                                                <div className="mt-2 flex items-center gap-1 text-xs text-purple-600">
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                                                    </svg>
                                                    {message.replies_count} {message.replies_count === 1 ? 'reply' : 'replies'}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </button>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>

            {/* Right Panel: Conversation View */}
            <div className="lg:col-span-2 bg-white rounded-xl shadow-lg overflow-hidden flex flex-col">
                {!selectedMessage ? (
                    <div className="flex items-center justify-center h-full text-gray-500">
                        <div className="text-center">
                            <svg className="w-20 h-20 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                            </svg>
                            <p className="font-semibold text-lg">No message selected</p>
                            <p className="text-sm mt-1">Select a message to view conversation</p>
                        </div>
                    </div>
                ) : (
                    <>
                        {/* Header */}
                        <div className="bg-gradient-to-r from-purple-600 to-purple-700 p-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <button
                                        onClick={() => {
                                            setSelectedMessage(null);
                                            setConversation(null);
                                        }}
                                        className="text-white hover:bg-purple-800 rounded-full p-2 transition lg:hidden"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                        </svg>
                                    </button>
                                    <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
                                        <span className="text-purple-700 font-bold">
                                            {(selectedMessage.sender_name || selectedMessage.sender_phone_number || 'U')[0].toUpperCase()}
                                        </span>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-white">
                                            {selectedMessage.sender_name || selectedMessage.sender_phone_number || 'Unknown User'}
                                        </h3>
                                        <p className="text-sm text-purple-100">{selectedMessage.subject || 'No subject'}</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => deleteMessage(selectedMessage.id)}
                                    className="text-white hover:bg-purple-800 rounded-full p-2 transition"
                                    title="Delete"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50" onMouseUp={handleQuoteText}>
                            {!conversation ? (
                                <div className="flex justify-center items-center h-full">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                                </div>
                            ) : (
                                <>
                                    {/* Original Message */}
                                    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-600">
                                        <div className="flex items-start gap-4">
                                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center flex-shrink-0">
                                                <span className="text-white font-bold">
                                                    {conversation.sender_name ? conversation.sender_name[0].toUpperCase() : 'U'}
                                                </span>
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex justify-between items-start mb-2">
                                                    <div>
                                                        <p className="font-bold text-gray-900">{conversation.sender_name || 'User'}</p>
                                                        <p className="text-sm text-gray-500">{formatDate(conversation.created_at)}</p>
                                                    </div>
                                                    <span className="bg-purple-100 text-purple-800 text-xs px-3 py-1 rounded-full font-semibold">
                                                        Original Message
                                                    </span>
                                                </div>
                                                {conversation.subject && (
                                                    <p className="font-semibold text-gray-900 mb-2">{conversation.subject}</p>
                                                )}
                                                <p className="text-gray-700 whitespace-pre-wrap">{conversation.message}</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Replies */}
                                    {conversation.replies && conversation.replies.length > 0 && (
                                        <div className="space-y-4 ml-8">
                                            {conversation.replies.map((reply, idx) => (
                                                <div key={idx} className={`rounded-lg shadow-md p-4 ${
                                                    reply.is_from_admin 
                                                        ? 'bg-green-50 border-l-4 border-green-600' 
                                                        : 'bg-blue-50 border-l-4 border-blue-600'
                                                }`}>
                                                    <div className="flex items-start gap-3">
                                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                                                            reply.is_from_admin
                                                                ? 'bg-green-600'
                                                                : 'bg-blue-600'
                                                        }`}>
                                                            <span className="text-white font-bold text-sm">
                                                                {reply.sender_name ? reply.sender_name[0].toUpperCase() : 'A'}
                                                            </span>
                                                        </div>
                                                        <div className="flex-1">
                                                            <div className="flex justify-between items-start mb-2">
                                                                <div>
                                                                    <p className="font-semibold text-gray-900">{reply.sender_name || 'Admin'}</p>
                                                                    <p className="text-xs text-gray-500">{formatDate(reply.created_at)}</p>
                                                                </div>
                                                                <div className="flex items-center gap-2">
                                                                    {reply.is_from_admin && <ReadReceipt seen={reply.is_read} />}
                                                                    <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                                                                        reply.is_from_admin
                                                                            ? 'bg-green-200 text-green-800'
                                                                            : 'bg-blue-200 text-blue-800'
                                                                    }`}>
                                                                        {reply.is_from_admin ? 'Editor' : 'User'}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                            {reply.quoted_text && (
                                                                <div className="bg-white bg-opacity-50 border-l-2 border-gray-400 pl-3 py-1 mb-2">
                                                                    <p className="text-xs text-gray-600 italic">"{reply.quoted_text}"</p>
                                                                </div>
                                                            )}
                                                            <p className="text-gray-700 whitespace-pre-wrap">{reply.message}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                    <div ref={messageEndRef} />
                                </>
                            )}
                        </div>

                        {/* Reply Input */}
                        <div className="p-4 border-t border-gray-200 bg-white">
                            {quotedText && (
                                <div className="mb-3 p-3 bg-purple-50 rounded-lg border-l-4 border-purple-600 flex items-start justify-between">
                                    <div className="flex-1">
                                        <p className="text-xs text-purple-600 font-semibold mb-1">Replying to:</p>
                                        <p className="text-sm text-gray-700 italic">"{quotedText}"</p>
                                    </div>
                                    <button
                                        onClick={() => setQuotedText('')}
                                        className="text-gray-500 hover:text-gray-700 ml-2"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            )}
                            <div className="flex items-end gap-3">
                                <textarea
                                    value={replyText}
                                    onChange={(e) => setReplyText(e.target.value)}
                                    placeholder="Type your reply..."
                                    rows={3}
                                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
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
                                    className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-bold transition flex items-center gap-2"
                                >
                                    {isSending ? (
                                        <>
                                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                            Sending...
                                        </>
                                    ) : (
                                        <>
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                            </svg>
                                            Send
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>
            
            {/* Alert Modal */}
            <AlertModal
                isOpen={showAlert}
                onClose={() => setShowAlert(false)}
                title={alertConfig.title}
                message={alertConfig.message}
                type={alertConfig.type}
            />
            
            {/* Confirm Modal */}
            <ConfirmModal
                isOpen={showConfirm}
                onClose={() => setShowConfirm(false)}
                onConfirm={confirmConfig.onConfirm}
                title={confirmConfig.title}
                message={confirmConfig.message}
                type="warning"
            />
        </div>
    );
}
