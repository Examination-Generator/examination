import { useState, useEffect, useRef } from 'react';
import * as messagingService from '../services/messagingService';
import AlertModal from './AlertModal';

export default function SMSMessaging() {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [selectedContacts, setSelectedContacts] = useState([]);
    const [messageText, setMessageText] = useState('');
    const [isSending, setIsSending] = useState(false);
    const [isSearching, setIsSearching] = useState(false);
    const [conversations, setConversations] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [conversationMessages, setConversationMessages] = useState([]);
    const [isLoadingConversation, setIsLoadingConversation] = useState(false);
    const [quotedText, setQuotedText] = useState('');
    const searchTimeoutRef = useRef(null);
    const messageEndRef = useRef(null);
    
    // Alert modal state
    const [showAlert, setShowAlert] = useState(false);
    const [alertConfig, setAlertConfig] = useState({ title: '', message: '', type: 'info' });

    // Load all conversations on mount
    useEffect(() => {
        loadConversations();
    }, []);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversationMessages]);

    const loadConversations = async () => {
        try {
            const data = await messagingService.getAllSMSConversations();
            setConversations(data || []);
        } catch (error) {
            console.error('Failed to load conversations:', error);
        }
    };

    const handleSearch = async (query) => {
        setSearchQuery(query);
        
        if (query.trim().length < 2) {
            setSearchResults([]);
            return;
        }

        // Debounce search
        if (searchTimeoutRef.current) {
            clearTimeout(searchTimeoutRef.current);
        }

        searchTimeoutRef.current = setTimeout(async () => {
            setIsSearching(true);
            try {
                const results = await messagingService.searchContacts(query);
                setSearchResults(results || []);
            } catch (error) {
                console.error('Search failed:', error);
                setSearchResults([]);
            } finally {
                setIsSearching(false);
            }
        }, 300);
    };

    const addContact = (contact) => {
        if (!selectedContacts.find(c => c.phone_number === contact.phone_number)) {
            setSelectedContacts([...selectedContacts, contact]);
        }
        setSearchQuery('');
        setSearchResults([]);
    };

    const removeContact = (phoneNumber) => {
        setSelectedContacts(selectedContacts.filter(c => c.phone_number !== phoneNumber));
    };

    const handleSendMessage = async () => {
        if (!messageText.trim() || selectedContacts.length === 0) {
            return;
        }

        setIsSending(true);
        try {
            const recipients = selectedContacts.map(c => c.phone_number);
            await messagingService.sendSMS({
                recipients,
                message: messageText
            });

            // Clear form
            setMessageText('');
            setSelectedContacts([]);
            
            // Reload conversations
            await loadConversations();
            
            setAlertConfig({
                title: 'Success',
                message: 'Message sent successfully!',
                type: 'success'
            });
            setShowAlert(true);
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

    const openConversation = async (phoneNumber) => {
        setSelectedConversation(phoneNumber);
        setIsLoadingConversation(true);
        try {
            const messages = await messagingService.getSMSConversation(phoneNumber);
            setConversationMessages(messages || []);
        } catch (error) {
            console.error('Failed to load conversation:', error);
            setConversationMessages([]);
        } finally {
            setIsLoadingConversation(false);
        }
    };

    const handleQuoteText = () => {
        const selectedText = window.getSelection().toString();
        if (selectedText) {
            setQuotedText(selectedText);
        }
    };

    const replyToConversation = async () => {
        if (!messageText.trim() || !selectedConversation) {
            return;
        }

        setIsSending(true);
        try {
            await messagingService.sendSMS({
                recipients: [selectedConversation],
                message: quotedText 
                    ? `Re: "${quotedText}"\n\n${messageText}` 
                    : messageText
            });

            // Reload conversation
            await openConversation(selectedConversation);
            
            setMessageText('');
            setQuotedText('');
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

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-250px)]">
            {/* Left Panel: Conversations List */}
            <div className="lg:col-span-1 bg-white rounded-xl shadow-lg overflow-hidden flex flex-col">
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                        </svg>
                        SMS Conversations
                    </h3>
                </div>
                
                <div className="flex-1 overflow-y-auto">
                    {conversations.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">
                            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                            <p className="font-semibold">No conversations yet</p>
                            <p className="text-sm mt-1">Send a message to start</p>
                        </div>
                    ) : (
                        <div className="divide-y divide-gray-200">
                            {conversations.map(conv => (
                                <button
                                    key={conv.phone_number}
                                    onClick={() => openConversation(conv.phone_number)}
                                    className={`w-full text-left p-4 hover:bg-gray-50 transition ${
                                        selectedConversation === conv.phone_number ? 'bg-blue-50' : ''
                                    }`}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className="w-10 h-10 rounded-full bg-blue-200 flex items-center justify-center flex-shrink-0">
                                            <span className="text-blue-700 font-bold">
                                                {conv.name ? conv.name[0].toUpperCase() : '?'}
                                            </span>
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex justify-between items-start mb-1">
                                                <p className="font-semibold text-gray-900 truncate">
                                                    {conv.name || conv.phone_number}
                                                </p>
                                                <span className="text-xs text-gray-500 ml-2">
                                                    {new Date(conv.last_message_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-600 truncate">{conv.last_message}</p>
                                            <p className="text-xs text-gray-500 mt-1">{conv.phone_number}</p>
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Right Panel: Message Composition or Conversation View */}
            <div className="lg:col-span-2 bg-white rounded-xl shadow-lg overflow-hidden flex flex-col">
                {!selectedConversation ? (
                    // New Message Composition
                    <>
                        <div className="bg-gradient-to-r from-green-600 to-green-700 p-4">
                            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                </svg>
                                Send SMS Message
                            </h3>
                        </div>

                        <div className="flex-1 overflow-y-auto p-6">
                            {/* Contact Search */}
                            <div className="mb-6">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Search Contacts
                                </label>
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={searchQuery}
                                        onChange={(e) => handleSearch(e.target.value)}
                                        placeholder="Search by name or phone number..."
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                    />
                                    {isSearching && (
                                        <div className="absolute right-3 top-3">
                                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
                                        </div>
                                    )}
                                </div>

                                {/* Search Results */}
                                {searchResults.length > 0 && (
                                    <div className="mt-2 border border-gray-200 rounded-lg max-h-48 overflow-y-auto">
                                        {searchResults.map(contact => (
                                            <button
                                                key={contact.phone_number}
                                                onClick={() => addContact(contact)}
                                                className="w-full text-left p-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                                            >
                                                <p className="font-semibold text-gray-900">{contact.name}</p>
                                                <p className="text-sm text-gray-600">{contact.phone_number}</p>
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* Selected Contacts */}
                            {selectedContacts.length > 0 && (
                                <div className="mb-6">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Recipients ({selectedContacts.length})
                                    </label>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedContacts.map(contact => (
                                            <div
                                                key={contact.phone_number}
                                                className="bg-green-100 text-green-800 px-3 py-2 rounded-full flex items-center gap-2"
                                            >
                                                <span className="font-semibold">{contact.name}</span>
                                                <span className="text-sm">({contact.phone_number})</span>
                                                <button
                                                    onClick={() => removeContact(contact.phone_number)}
                                                    className="text-green-600 hover:text-green-800"
                                                >
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Message Input */}
                            <div className="mb-6">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Message
                                </label>
                                <textarea
                                    value={messageText}
                                    onChange={(e) => setMessageText(e.target.value)}
                                    placeholder="Type your message here..."
                                    rows={8}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                                />
                                <div className="mt-2 flex justify-between items-center text-sm">
                                    <span className="text-gray-500">
                                        {messageText.length} characters
                                    </span>
                                    <span className="text-gray-500">
                                        Source: Speedstar Exam
                                    </span>
                                </div>
                            </div>

                            {/* Send Button */}
                            <button
                                onClick={handleSendMessage}
                                disabled={isSending || !messageText.trim() || selectedContacts.length === 0}
                                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white py-3 rounded-lg font-bold transition flex items-center justify-center gap-2"
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
                                        Send Message
                                    </>
                                )}
                            </button>
                        </div>
                    </>
                ) : (
                    // Conversation View
                    <>
                        <div className="bg-gradient-to-r from-green-600 to-green-700 p-4 flex items-center gap-3">
                            <button
                                onClick={() => {
                                    setSelectedConversation(null);
                                    setConversationMessages([]);
                                }}
                                className="text-white hover:bg-green-800 rounded-full p-2 transition"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                </svg>
                            </button>
                            <div className="flex-1">
                                <h3 className="text-lg font-bold text-white">
                                    {conversations.find(c => c.phone_number === selectedConversation)?.name || selectedConversation}
                                </h3>
                                <p className="text-sm text-green-100">{selectedConversation}</p>
                            </div>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
                            {isLoadingConversation ? (
                                <div className="flex justify-center items-center h-full">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
                                </div>
                            ) : conversationMessages.length === 0 ? (
                                <div className="text-center text-gray-500">No messages yet</div>
                            ) : (
                                conversationMessages.map((msg, idx) => (
                                    <div
                                        key={idx}
                                        className={`flex ${msg.direction === 'outgoing' ? 'justify-end' : 'justify-start'}`}
                                        onMouseUp={handleQuoteText}
                                    >
                                        <div
                                            className={`max-w-md px-4 py-3 rounded-lg ${
                                                msg.direction === 'outgoing'
                                                    ? 'bg-green-600 text-white'
                                                    : 'bg-white text-gray-900 border border-gray-200'
                                            }`}
                                        >
                                            <p className="whitespace-pre-wrap">{msg.message}</p>
                                            <p className={`text-xs mt-2 ${
                                                msg.direction === 'outgoing' ? 'text-green-100' : 'text-gray-500'
                                            }`}>
                                                {new Date(msg.sent_at).toLocaleString()}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            )}
                            <div ref={messageEndRef} />
                        </div>

                        {/* Reply Input */}
                        <div className="p-4 border-t border-gray-200 bg-white">
                            {quotedText && (
                                <div className="mb-2 p-2 bg-gray-100 rounded-lg border-l-4 border-green-600 flex items-center justify-between">
                                    <div className="flex-1">
                                        <p className="text-xs text-gray-500 mb-1">Replying to:</p>
                                        <p className="text-sm text-gray-700 italic truncate">"{quotedText}"</p>
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
                            <div className="flex items-end gap-2">
                                <textarea
                                    value={messageText}
                                    onChange={(e) => setMessageText(e.target.value)}
                                    placeholder="Type a reply..."
                                    rows={2}
                                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            replyToConversation();
                                        }
                                    }}
                                />
                                <button
                                    onClick={replyToConversation}
                                    disabled={isSending || !messageText.trim()}
                                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white p-3 rounded-lg transition"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                    </svg>
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
        </div>
    );
}
