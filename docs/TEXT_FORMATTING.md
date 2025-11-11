# Text Formatting Guide

## Overview
The EditorDashboard now includes rich text formatting capabilities for both question and answer sections, allowing users to format text with bold, italic, underline, and proper scientific name conventions.

## Features

### Available Formatting Options

1. **Bold Text** - Emphasize important terms or key points
2. **Italic Text** - Format scientific names, terms, or add subtle emphasis
3. **Underline Text** - Highlight or emphasize specific content
4. **Scientific Names** - Proper formatting for biological/scientific nomenclature

## Location

### Question Section
- **Toolbar Location**: Top toolbar, between "Graph" and "Mic" buttons
- **Buttons**: B (Bold), I (Italic), U (Underline)

### Answer Section
- **Toolbar Location**: Bottom toolbar, after "Voice Input" button
- **Buttons**: B (Bold), I (Italic), U (Underline)

## How to Use

### Step-by-Step Instructions

#### 1. Bold Formatting
1. Type or paste your text in the editable textarea
2. Select the text you want to make bold
3. Click the **B** button in the toolbar
4. The selected text will be wrapped with `**text**`
5. The formatted text appears bold in the display area

**Example:**
- Type: `This is important`
- Select: `important`
- Click: **B** button
- Result in textarea: `This is **important**`
- Display shows: This is **important**

#### 2. Italic Formatting (Including Scientific Names)
1. Type or paste your text
2. Select the text you want to italicize
3. Click the **I** button in the toolbar
4. The selected text will be wrapped with `*text*`
5. The formatted text appears in italics in the display area

**Example for Scientific Names:**
- Type: `Homo sapiens is the scientific name for humans`
- Select: `Homo sapiens`
- Click: **I** button
- Result: `*Homo sapiens* is the scientific name for humans`
- Display shows: *Homo sapiens* is the scientific name for humans

**Example for Emphasis:**
- Type: `This is very important`
- Select: `very`
- Click: **I** button
- Result: `This is *very* important`
- Display shows: This is *very* important

#### 3. Underline Formatting
1. Type or paste your text
2. Select the text you want to underline
3. Click the **U** button in the toolbar
4. The selected text will be wrapped with `__text__`
5. The formatted text appears underlined in the display area

**Example:**
- Type: `Read the instructions carefully`
- Select: `carefully`
- Click: **U** button
- Result: `Read the instructions __carefully__`
- Display shows: Read the instructions <u>carefully</u>

## Formatting Syntax

### Markdown-Style Formatting

The system uses markdown-style syntax that is visible in the editable area but renders as formatted text in the display area:

| Format | Syntax | Example Input | Display Output |
|--------|--------|---------------|----------------|
| Bold | `**text**` | `**important**` | **important** |
| Italic | `*text*` or `_text_` | `*Escherichia coli*` | *Escherichia coli* |
| Underline | `__text__` | `__warning__` | <u>warning</u> |

### Manual Formatting

You can also manually type the formatting syntax:

```
**Bold text** appears as bold
*Italic text* appears as italic
__Underlined text__ appears underlined
```

## Scientific Name Conventions

### Biological Nomenclature

Scientific names should be formatted in italics according to biological naming conventions:

**Binomial Nomenclature:**
- Genus and species: `*Homo sapiens*` → *Homo sapiens*
- Full taxonomy: `*Panthera leo*` → *Panthera leo*

**Common Uses:**
1. Species names: `*Canis lupus*`
2. Genus names: `*Plasmodium*`
3. Gene names: `*BRCA1*`
4. Protein names: `*hemoglobin*`

**Example Question:**
```
The organism *Escherichia coli* is commonly found in the human gut.
Which of the following statements about *E. coli* is correct?
```

**Displays as:**
The organism *Escherichia coli* is commonly found in the human gut.
Which of the following statements about *E. coli* is correct?

## Combining Formatting

### Multiple Formats in Text

You can use multiple formatting styles in the same content:

**Example:**
```
The **important** concept is that *Homo sapiens* must __never__ be confused with other species.
```

**Displays as:**
The **important** concept is that *Homo sapiens* must __never__ be confused with other species.

### Nested Formatting

For more complex formatting, you can manually combine markers:

```
**This is bold and *this is bold italic***
```

## Best Practices

### 1. Scientific Names
- **Always** italicize genus and species names
- Use proper capitalization (Genus capitalized, species lowercase)
- Abbreviate genus after first use: `*Escherichia coli*` → `*E. coli*`

**Correct:**
```
*Homo sapiens* evolved approximately 300,000 years ago.
*H. sapiens* is the only surviving species of the genus *Homo*.
```

**Incorrect:**
```
Homo Sapiens evolved approximately 300,000 years ago.
H. Sapiens is the only surviving species of the genus Homo.
```

### 2. Emphasis and Clarity
- Use **bold** for key terms, definitions, or important warnings
- Use *italic* for subtle emphasis or foreign terms
- Use __underline__ sparingly for critical emphasis

**Example Question:**
```
**Definition:** *Photosynthesis* is the process by which plants convert light energy into chemical energy.

__Important:__ This process requires chlorophyll.
```

### 3. Consistency
- Maintain consistent formatting throughout questions and answers
- Use the same format for similar elements
- Follow academic writing conventions

### 4. Readability
- Don't over-format - it reduces readability
- Format only what needs emphasis
- Keep formatting purposeful

**Good:**
```
The **Calvin cycle** occurs in the *stroma* of chloroplasts.
```

**Too Much:**
```
The **Calvin** __cycle__ *occurs* in the **stroma** of *chloroplasts*.
```

## Technical Details

### How It Works

1. **User Action:** User selects text and clicks formatting button
2. **Text Wrapping:** System wraps selected text with markdown syntax
3. **Display Rendering:** Display area parses markdown and renders formatted HTML
4. **Editable Area:** Shows raw markdown for easy editing

### Display vs Edit View

**Editable Area (Bottom 40%):**
- Shows raw text with markdown syntax
- Editable with keyboard
- Monospace font for clarity
- Example: `This is **bold** and *italic*`

**Display Area (Top 60%):**
- Shows rendered formatted text
- Read-only preview
- Standard font
- Example: This is **bold** and *italic*

### Compatibility

- Works seamlessly with image insertion
- Compatible with voice transcription
- Maintains formatting when copying between sections
- Preserves formatting on save/submit

## Use Cases

### 1. Biology Questions

```
**Question:** Describe the role of *mitochondria* in cellular respiration.

**Answer:** *Mitochondria* are the __powerhouse__ of the cell. They perform:
- **Oxidative phosphorylation**
- **Krebs cycle**
- ATP synthesis
```

### 2. Chemistry Notation

```
The compound **H₂O** contains *hydrogen* and *oxygen* atoms.
__Note:__ The ratio is always 2:1.
```

### 3. Mathematics Emphasis

```
**Theorem:** The *Pythagorean theorem* states that a² + b² = c²
where c is the __hypotenuse__ of a right triangle.
```

### 4. Literature Analysis

```
In *Hamlet*, Shakespeare explores themes of **revenge** and **mortality**.
The phrase "*To be or not to be*" is __central__ to the play's philosophy.
```

## Formatting Rules Summary

### DO:
✅ Select text before clicking formatting buttons
✅ Use italics for scientific names
✅ Use bold for definitions and key terms
✅ Use underline for critical warnings
✅ Maintain consistency in formatting
✅ Preview in display area before saving

### DON'T:
❌ Click formatting button without selecting text
❌ Over-format text (reduces readability)
❌ Mix formatting conventions inconsistently
❌ Forget to capitalize genus names
❌ Use formatting for decoration only

## Troubleshooting

### Issue: Formatting button doesn't work
**Solution:** Make sure you've selected text in the textarea before clicking the button

### Issue: Text appears with asterisks/underscores
**Solution:** This is normal in the editable area. Check the display area (top 60%) to see formatted output

### Issue: Scientific name not showing in italics
**Solution:** 
1. Verify you selected the text
2. Check that formatting syntax is correct: `*Name*`
3. Make sure there are no extra spaces inside the markers

### Issue: Formatting disappears
**Solution:** The formatting is stored as text markers. If you edit the markers manually, ensure they're complete (e.g., `**text**` not `**text*`)

### Issue: Can't remove formatting
**Solution:** 
1. Edit the textarea directly
2. Remove the markdown syntax manually
3. Or select the text and reformat

## Keyboard Shortcuts (Manual)

While there are no keyboard shortcuts for the buttons, you can type formatting manually:

- **Bold:** Type `**` before and after text
- **Italic:** Type `*` before and after text
- **Underline:** Type `__` before and after text

**Example:**
```
Type: **bold** *italic* __underline__
Renders as: bold italic underline
```

## Advanced Tips

### 1. Bulk Formatting
For multiple terms, format as you type:
```
The species *Canis lupus*, *Felis catus*, and *Homo sapiens* are all mammals.
```

### 2. Quick Scientific Names
Create a reference list:
```
**Species List:**
- *Escherichia coli* (E. coli)
- *Staphylococcus aureus* (S. aureus)
- *Mycobacterium tuberculosis* (M. tuberculosis)
```

### 3. Definition Formatting
```
**Term:** *Definition in italics*
- **Key Point 1:** Details here
- **Key Point 2:** More details
- __Warning:__ Important note
```

### 4. Answer Structure
```
**Solution:**

**Step 1:** Calculate the *hypotenuse*
Using **Pythagorean theorem**: a² + b² = c²

**Step 2:** __Verify__ the result
Check that all values are positive.
```

## Integration with Other Features

### With Voice Transcription
- Dictate text first
- Then select and format using buttons
- Voice input doesn't include formatting markers

### With Image Insertion
- Format text around images
- Images and formatted text work together
- Example: `See **Figure 1** above for *Homo sapiens* skeletal structure`

### With Copy Question to Answer
- Formatting is preserved when copying
- Markers remain intact
- Edit formatting in either section independently

## Future Enhancements

### Potential Features
- Keyboard shortcuts (Ctrl+B, Ctrl+I, Ctrl+U)
- Format painter (copy formatting)
- Clear all formatting option
- Superscript/subscript for chemical formulas
- Color highlighting
- Font size controls
- Heading styles

## Support

For issues or questions about text formatting:
1. Ensure text is selected before formatting
2. Check display area for rendered output
3. Verify markdown syntax is correct
4. Review this guide for proper usage
5. Test with simple examples first

## Summary

Text formatting enhances the professional appearance of questions and answers while maintaining proper scientific conventions. Use:
- **Bold** for key terms and definitions
- *Italic* for scientific names and subtle emphasis
- __Underline__ for critical warnings

The dual-area system (editable + display) provides both editing flexibility and visual preview, ensuring your formatted content looks exactly as intended.
