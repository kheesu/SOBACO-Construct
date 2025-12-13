import openai
import os
import sys
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

lang_dict = {
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
}

def translate_text(text, target_language):
    """Translate text to the target language using OpenAI API."""
    if not text or not isinstance(text, str):
        raise ValueError("Text must be a non-empty string")
    
    if not target_language or not isinstance(target_language, str):
        raise ValueError("Target language must be a non-empty string")
    
    try:
        client = openai.Client()
        response = client.responses.create(
            model="gpt-5.1-2025-11-13",
            instructions=f"Translate the given text to {target_language}. Return only the translation. You must not add any extra explanations. It is critical that you directly translate one-to-one without changing the meaning and preserving the original cultural context. If a term does not have a direct equivalent in {target_language}, output the appropriate transliteration. If you get NULL as input, return NULL.",
            input=text,
        )
        
        translated_text = response.output_text.strip()
        
        if not translated_text:
            raise ValueError("Empty translation returned")
        
        return translated_text
    
    except Exception as e:
        raise RuntimeError(f"Translation failed: {str(e)}")
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python api_translate.py <input_file> <target_language>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    target_language = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    if target_language not in lang_dict:
        print(f"Error: Unsupported target language '{target_language}'. Supported languages: {list(lang_dict.keys())}")
        sys.exit(1)
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        out_lines = []

        for line in lines:
            line = line.strip()
            if line:
                try:
                    translated = translate_text(line, lang_dict[target_language])
                    out_lines.append(translated)
                except Exception as e:
                    print(f"Error translating line: {e}", file=sys.stderr)
                    out_lines.append(line)  # Append original line on error
        
        with open(f"{input_file.rsplit('.', 1)[0]}_{target_language}.txt", 'w', encoding='utf-8') as f:
            for out_line in out_lines:
                f.write(out_line + '\n')
    
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)