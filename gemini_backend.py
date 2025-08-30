import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")

# Don't raise error immediately, just store the API key status
def has_api_key():
    # Reload environment variables to check for newly saved API keys
    load_dotenv(override=True)
    current_api_key = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
    return bool(current_api_key)

# Only create client if API key is available
client = None
if api_key:
    client = genai.Client(api_key=api_key)

SUMMARY_PATH = "db/summary.txt"
MODEL_NAME = "gemini-2.5-flash"

def generate_summary_text(data):
    if not has_api_key():
        raise ValueError("API key is required for this operation")
    
    # Reload client if API key was added after startup
    global client
    if not client:
        current_api_key = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
        if current_api_key:
            client = genai.Client(api_key=current_api_key)
        else:
            raise ValueError("API key is required for this operation")
    
    prompt = (
        """You are an expert at concisely summarizing color associations based on their color categories.

Given a list of colors and their associated synesthetic descriptions, summarize the data by:
1. Grouping colors into primary, secondary, and tertiary color categories arranged in rainbow order.
2. Subcategorizing and summarizing each group by HUE (NO MORE THAN 4).  ("Light purples" ✅, "murky yellows" ✅, "earthy greens" ✅)

Whenever you mention a specific color, ALWAYS include the hex code afterward, like "dark maroon (#3c0008)".
Consider combinations of primary and secondary colors (like blue-greens, blue-purples, and purple-reds) separately from primary and secondary colors, and focus on how they combine aspects of the colors mixed. Place them between the colors that make them up, following rainbow order.

Format the output like this:
- Use indentation and dashes for subcategorization
- Categorize the HUES ONLY, not the associations connected to them (e.g. "bright", "dark", "earthy", "muted" shades) and examples
- Use hanging bullet point format with a bullet for each complete thought
- No more than 64 characters per line!
- Avoid markdown formatting.
- Keep it visually clear and intuitive, using the following format:

WARM COLORS
-----------------------------------------------------------------------
Pinks: [One-sentence summary]
   - Light Pinks: [Three-word summary]
       - Baby pink (#ffb7ce): [Three-word summary of association]
   - Bright Pinks: [Three-word summary]
       - Hot pink (#ff028d): [Three-word summary of association]
       - Barbie pink (#fe46a5): [Three-word summary of association]
   - Muted Pinks: [Three-word summary]
       - Greyish pink (#c88d94): [Three-word summary of association]

Reds: [One-sentence summary]
   - Bright Reds: [Three-word summary]
       - Lightish red (#fe2f4a): [Three-word summary of association]
       - Watermelon (#fd4659): [Three-word summary of association]
   - Muted Reds: [Three-word summary]
       - Pastel red (#db5856): [Three-word summary of association]
       - Raspberry (#b00149): [Three-word summary of association]
   - Dark Reds: [Three-word summary]
       - Dark maroon (#3c0008): [Three-word summary of association]
       - Dried blood (#4b0101): [Three-word summary of association]

Oranges: 
[...]

Yellow-Oranges:
[...]

Yellows:
[...]

Yellow-Greens:

\n\n\n   
COOL COLORS
-----------------------------------------------------------------------
...\n\n\n
NEUTRAL COLORS  
-----------------------------------------------------------------------
...
\n\n\n
=======================================================================
DARK VS LIGHT:
[Indented paragraph about dark colors in general. Do not use line breaks]
\n
[Indented paragraph about light colors in general. Do not use line breaks]
\n\n\n
=======================================================================
DULL VS VIBRANT:
[Indented paragraph about dull colors in general. Do not use line breaks]
\n
[Indented paragraph about vibrant colors in general. Do not use line breaks]
\n\n\n
=======================================================================
OVERALL SUMMARY:
[3-paragraph indented summary with newlines between each paragraph.]

Be concise but insightful. Focus on deeper patterns not explored or obvious from the rest of the analysis.
"""
        + "\n".join(
            f"{e['xkcd_name']} ({e['hex']}): {e['associations']}" for e in data
        )
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text

def update_summary_file(data):
    summary = generate_summary_text(data)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(summary)
    return summary

def generate_chat_response(prompt, data):
    if not has_api_key():
        raise ValueError("API key is required for this operation")
    
    # Reload client if API key was added after startup
    global client
    if not client:
        current_api_key = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
        if current_api_key:
            client = genai.Client(api_key=current_api_key)
        else:
            raise ValueError("API key is required for this operation")
    
    db_text = "\n".join(
        f"{e['xkcd_name']} ({e['hex']}): {e['associations']}" for e in data
    )
    full_prompt = (
        "You are a thoughtful assistant trained on the following database of "
        "synesthetic color associations:\n\n"
        f"{db_text}\n\n"
        "Your job is to respond to the user's prompt using clear and intuitive "
        "plaintext formatting that fits well in a window ~64 characters wide.\n\n"
        "FORMATTING GUIDELINES:\n"
        "- Use ALL-CAPS for major headers\n"
        "- Use hanging indents: when a line wraps, indent it with 6 spaces so it's aligned with "
        "the text after the bullet or number, NOT under the bullet/number itself\n"
        "- Use dashes ( - ) for lists and bullet points\n"
        "- Use paragraphs for explanations and grouped analysis\n"
        "- Avoid any markdown formatting (no asterisks, hashes, underscores, etc.)\n"
        "- Use hex codes when referencing colors\n"
        "- Keep line length around 70 characters for readability\n"
        "- Use consistent spacing and line breaks\n\n"
        f"Prompt: {prompt}"
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt
    )
    return response.text 