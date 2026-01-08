
import re

def simulate_gentle_response(original_text):
    # Simulate Gentle flattening the text and returning word objects
    # Gentle splits by whitespace and creates objects
    words_raw = original_text.split()
    gentle_words = []
    current_time = 0
    
    for w in words_raw:
        clean_word = re.sub(r'[^\w]', '', w.lower()) # Simulate Gentle normalization
        gentle_words.append({
            "word": w, # Gentle actually returns the transcript word
            "alignedWord": clean_word if clean_word else "<unk>",
            "start": current_time,
            "end": current_time + 100
        })
        current_time += 150
    return gentle_words

def process_words_preserving_format(original_text, gentle_words):
    # Logic to re-inject format
    # Strategy: 
    # 1. Tokenize original text preserving whitespace/newlines
    # 2. Match gentle words to original tokens
    
    # Simple strategy: iterate original text, find words, detect gaps.
    
    print(f"Original: {repr(original_text)}")
    
    # Split keeping delimiters to find \n
    # This is tricky because Gentle words might be slightly different if punctuation is handled differently.
    # But usually Gentle "word" field matches the input tokens.
    
    # Let's assume gentle_words[i]["word"] corresponds to the i-th non-whitespace token in original_text.
    
    processed_words = []
    
    # Regex to find words and intervening whitespace
    # We want to match the sequence of words.
    
    # Create a list of (word, trailing_whitespace) from original text
    tokens = re.split(r'(\s+)', original_text)
    # tokens will be ['Hello', ' ', 'world', '\n\n', 'Test']
    
    word_tokens = []
    for t in tokens:
        if not t.strip():
            if word_tokens:
                word_tokens[-1] = (word_tokens[-1][0], word_tokens[-1][1] + t)
        else:
            word_tokens.append((t, "")) # Word, trailing
            
    # Now map gentle words to these tokens
    # Gentle might split "word." into "word." or "word" + "."?
    # Gentle aligns strictly on whitespace-separated tokens usually.
    
    formatted_output = []
    
    gentle_idx = 0
    for original_word, trailing_space in word_tokens:
        if gentle_idx >= len(gentle_words):
            break
            
        g_word = gentle_words[gentle_idx]
        
        # Check if they match loosely (Gentle returns input word usually)
        # We prefer the original_word structure (casing, punctuation) + trailing space
        
        # Newlines in trailing space?
        newlines = trailing_space.count('\n')
        final_word_string = original_word
        
        if newlines > 0:
             # Inject newline into the word string?
             # App logic is: append(word) + " "
             # If we want newlines, we should append them to the word.
             # "Hello" + "\n" -> "Hello\n" + " " -> "Hello\n "
             final_word_string += "\n" * newlines
        
        # Use Gentle timestamp but Original Text
        formatted_output.append({
            "word": final_word_string,
            "start": g_word["start"],
            "end": g_word["end"],
            "confidence": 1.0
        })
        
        gentle_idx += 1
        
    return formatted_output

# Test Case
text = "The Metropolitan Train of Cochabamba\n\nthe metropolitan train of Cochabamba is in Bolivia."
gentle_data = simulate_gentle_response(text)

print("--- Gentle Raw ---")
for w in gentle_data:
    print(f"'{w['word']}'")

print("\n--- Processed ---")
result = process_words_preserving_format(text, gentle_data)
for w in result:
    print(f"'{w['word']}'")
