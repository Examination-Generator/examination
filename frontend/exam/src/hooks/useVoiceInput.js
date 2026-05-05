
import { useState, useRef, useCallback, useEffect } from 'react';

export function useVoiceInput(onTranscript, onError) {
    const [isListening, setIsListening] = useState(false);
    const recognitionRef = useRef(null);

    const toggle = useCallback(() => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            onError?.('Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }
        if (isListening) {
            recognitionRef.current?.stop();
            setIsListening(false);
            return;
        }
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SR();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        recognition.onstart = () => setIsListening(true);
        recognition.onresult = (e) => {
            let final = '';
            for (let i = e.resultIndex; i < e.results.length; i++) {
                if (e.results[i].isFinal) {
                    final += e.results[i][0].transcript + ' ';
                }
            }
            if (final) {
                onTranscript(final);
            }
        };
        recognition.onerror = (event) => {
            setIsListening(false);
            if (event.error !== 'no-speech') {
                onError?.('Voice recognition error: ' + event.error);
            }
        };
        recognition.onend = () => setIsListening(false);
        recognitionRef.current = recognition;
        recognition.start();
    }, [isListening, onTranscript, onError]);

    const stop = useCallback(() => {
        recognitionRef.current?.stop();
        setIsListening(false);
    }, []);

    useEffect(() => {
        return () => {
            recognitionRef.current?.stop();
        };
    }, []);

    return { isListening, toggle, stop };
}