# Voice Transcription Feature

## Overview
The EditorDashboard now includes voice-to-text transcription functionality for both question and answer sections, allowing users to dictate content instead of typing.

## Features

### 1. Voice Input for Questions
- **Location**: Question Content toolbar (top section)
- **Button**: Orange "Mic" button with microphone icon
- **States**:
  - **Inactive**: Orange button labeled "Mic"
  - **Active**: Red pulsing button labeled "Recording..."

### 2. Voice Input for Answers
- **Location**: Answer Content toolbar (bottom section)
- **Button**: Orange "Voice Input" button with microphone icon
- **States**:
  - **Inactive**: Orange button labeled "Voice Input"
  - **Active**: Red pulsing button labeled "Recording..."

## How to Use

### Starting Voice Recording
1. Click the microphone button in either the question or answer section
2. The button will turn red and pulse, indicating active recording
3. Grant microphone permissions when prompted by your browser
4. Start speaking - your words will be transcribed in real-time
5. The transcribed text will be appended to the existing content

### Stopping Voice Recording
1. Click the microphone button again (now red and pulsing)
2. Recording will stop immediately
3. The button will return to its orange inactive state
4. All transcribed text will be saved in the text area

## Technical Details

### Browser Compatibility
- **Supported Browsers**:
  - Google Chrome (recommended)
  - Microsoft Edge
  - Safari (iOS/macOS)
  
- **Unsupported Browsers**:
  - Firefox (limited support)
  - Internet Explorer
  - Opera (limited support)

### Language Support
- **Default Language**: English (US)
- **Customization**: The language can be changed by modifying the `recognition.lang` property in the code
- **Available Languages**: Any language supported by the Web Speech API (e.g., 'en-GB', 'es-ES', 'fr-FR', 'de-DE', etc.)

### How It Works
1. **Web Speech API**: Uses the browser's built-in SpeechRecognition API
2. **Continuous Mode**: Recording continues until manually stopped
3. **Interim Results**: Shows text as you speak for immediate feedback
4. **Final Transcription**: Only finalized text is added to the content area
5. **Append Mode**: New transcribed text is added to existing content (not replaced)

## Features

### Real-time Transcription
- Text appears as you speak
- Automatic punctuation (browser-dependent)
- Automatic capitalization

### Continuous Recording
- No time limits
- Can record long passages
- Manually controlled start/stop

### Error Handling
- Browser compatibility check on activation
- User-friendly error messages
- Automatic recovery from temporary errors
- "No speech" errors are silently handled

### Visual Feedback
- **Inactive**: Orange button
- **Active**: Red pulsing animation
- **Text labels**: "Mic"/"Recording..." or "Voice Input"/"Recording..."

## Use Cases

### Question Entry
- Dictate complex mathematical problems
- Read questions from paper documents
- Create multiple questions quickly
- Add verbal context to questions

### Answer Entry
- Dictate detailed explanations
- Provide step-by-step solutions
- Add commentary to existing answers
- Create marking schemes verbally

## Tips for Best Results

### 1. Microphone Setup
- Use a quality microphone for better accuracy
- Reduce background noise
- Speak clearly and at a moderate pace
- Position microphone 6-12 inches from your mouth

### 2. Speaking Technique
- Speak naturally but clearly
- Pause briefly between sentences
- Say punctuation if needed (e.g., "comma", "period")
- Spell out abbreviations or technical terms

### 3. Content Editing
- Review transcribed text for accuracy
- Edit any errors manually after recording
- Use voice for bulk content, then refine with keyboard
- Combine with other input methods (typing, images, drawing)

### 4. Browser Settings
- Grant microphone permissions when requested
- Check browser's speech recognition settings
- Use the latest browser version for best results
- Test with a simple phrase first

## Known Limitations

1. **Accuracy**: 
   - May struggle with technical terms
   - Accents can affect recognition
   - Background noise reduces accuracy

2. **Punctuation**:
   - Automatic punctuation varies by browser
   - May need manual punctuation editing

3. **Privacy**:
   - Audio is processed by browser's speech service
   - Some browsers may send audio to cloud services
   - No audio is stored by the application

4. **Internet Connection**:
   - Most browsers require internet for speech recognition
   - Offline mode not supported

## Troubleshooting

### "Voice recognition is not supported in your browser"
- **Solution**: Switch to Chrome, Edge, or Safari

### Microphone permission denied
- **Solution**: 
  1. Check browser's permission settings
  2. Allow microphone access for the website
  3. Reload the page and try again

### No text appears when speaking
- **Solution**:
  1. Check microphone is not muted
  2. Verify microphone is selected in OS settings
  3. Test microphone with another application
  4. Check browser console for errors

### Transcription stops unexpectedly
- **Solution**:
  1. Click the microphone button again to restart
  2. Check internet connection
  3. Try speaking more continuously
  4. Reduce background noise

### Poor transcription accuracy
- **Solution**:
  1. Speak more clearly and slowly
  2. Improve microphone quality
  3. Reduce background noise
  4. Use a headset microphone
  5. Spell out complex technical terms

## Future Enhancements

### Potential Features
- Language selection dropdown
- Custom vocabulary for technical terms
- Voice commands for formatting
- Audio playback of recorded content
- Save audio files alongside text
- Multi-language support toggle
- Offline speech recognition
- Speaker identification for multiple users

## Implementation Notes

### State Management
- `isQuestionListening`: Boolean tracking question recording state
- `isAnswerListening`: Boolean tracking answer recording state
- `questionRecognitionRef`: Reference to question speech recognition instance
- `answerRecognitionRef`: Reference to answer speech recognition instance

### Event Handlers
- `toggleQuestionVoiceRecording()`: Starts/stops question voice input
- `toggleAnswerVoiceRecording()`: Starts/stops answer voice input
- Automatic cleanup on component unmount

### Integration
- Works seamlessly with existing text input
- Compatible with image insertion
- Compatible with drawing tools
- Maintains all existing formatting

## Security & Privacy

### Data Handling
- No audio is stored on servers
- Text transcription only is saved
- Audio processing by browser/OS only
- No third-party audio storage

### Permissions
- Requires microphone permission
- Permission requested on first use
- Can be revoked in browser settings
- No automatic background recording

## Best Practices

### For Educators
1. Review all transcribed content before submitting
2. Use for quick content entry, then refine
3. Combine voice with other input methods
4. Test microphone setup before long sessions

### For Content Quality
1. Speak complete thoughts
2. Review and edit after transcription
3. Use keyboard for technical symbols
4. Verify mathematical expressions manually

### For Efficiency
1. Prepare content mentally before recording
2. Record in quiet environments
3. Use continuous recording for paragraphs
4. Stop and restart for new sections

## Support

For issues or questions about voice transcription:
1. Check browser compatibility first
2. Review troubleshooting section
3. Test microphone with other applications
4. Check browser console for error messages
5. Verify internet connection is stable
