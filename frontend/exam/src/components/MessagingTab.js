import { useState, useEffect } from 'react';
import SMSMessaging from './SMSMessaging';
import SystemMessaging from './SystemMessaging';
import * as messagingService from '../services/messagingService';

export default function MessagingTab() {
    const [activeSubTab, setActiveSubTab] = useState('sms'); // 'sms' or 'system'
    const [pendingSupportCount, setPendingSupportCount] = useState(0);

    // Debug: Log component mount
    // useEffect(() => {
    //     console.log('MessagingTab component mounted');
    // }, []);

    useEffect(() => {
        const loadPendingSupportCount = async () => {
            try {
                const count = await messagingService.getUnreadMessageCount();
                setPendingSupportCount(count || 0);
            } catch (error) {
                // console.error('Failed to load pending support count:', error);
            }
        };

        loadPendingSupportCount();
        const interval = setInterval(loadPendingSupportCount, 5000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6">
            {/* Sub-tab Navigation */}
            <div className="bg-white rounded-xl shadow-lg p-4">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                            </svg>
                            Messaging Center
                        </h2>
                        <p className="text-sm text-gray-600 mt-1">
                            Send SMS messages or manage support tickets
                        </p>
                    </div>
                    
                    {/* Info Badge */}
                    {/* <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-2">
                        <p className="text-xs text-blue-700 font-semibold">Admin Tools</p>
                        <p className="text-xs text-blue-600 mt-1">Multi-channel messaging</p>
                    </div> */}
                </div>

                {/* Sub-tabs */}
                <div className="flex gap-3">
                    <button
                        onClick={() => setActiveSubTab('sms')}
                        className={`flex-1 py-3 px-6 rounded-lg font-bold transition-all duration-200 flex items-center justify-center gap-2 ${
                            activeSubTab === 'sms'
                                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg transform scale-105'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        SMS Messaging
                    </button>
                    <button
                        onClick={() => setActiveSubTab('system')}
                        className={`flex-1 py-3 px-6 rounded-lg font-bold transition-all duration-200 flex items-center justify-center gap-2 ${
                            activeSubTab === 'system'
                                ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg transform scale-105'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                    >
                        <span className="relative inline-flex items-center">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            {pendingSupportCount > 0 && (
                                <span className="absolute -top-2 -right-3 bg-red-600 text-white text-[10px] leading-none font-bold rounded-full min-w-5 h-5 px-1 flex items-center justify-center">
                                    {pendingSupportCount > 99 ? '99+' : pendingSupportCount}
                                </span>
                            )}
                        </span>
                        Support Messages
                    </button>
                </div>

                {/* Description for active sub-tab */}
                <div className="mt-4 p-4 rounded-lg bg-gradient-to-r from-gray-50 to-gray-100">
                    {activeSubTab === 'sms' ? (
                        <div className="flex items-start gap-3">
                            <div className="bg-blue-100 rounded-full p-2">
                                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-900">SMS Messaging</p>
                                <p className="text-xs text-gray-600 mt-1">
                                    Send text messages to one or multiple users via their phone numbers. 
                                    Messages are sent from "Speedstar Exam" and support conversational tracking.
                                    You can also reply to specific messages in a conversation.
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="flex items-start gap-3">
                            <div className="bg-purple-100 rounded-full p-2">
                                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-900">Support Messages</p>
                                <p className="text-xs text-gray-600 mt-1">
                                    View and respond to support messages from users. 
                                    Messages are internal to the system and users can see your replies in their dashboard.
                                    Unread messages are highlighted and you can quote specific text when replying.
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Content Area */}
            <div>
                {activeSubTab === 'sms' ? (
                    <SMSMessaging />
                ) : (
                    <SystemMessaging />
                )}
            </div>
        </div>
    );
}
