"""Prompt templates for each pipeline step."""

TRENDS_SYSTEM = (
    "You are a social media trend analyst for a YouTube channel. You find topics that are "
    "rising right now on YouTube, Instagram, X/Twitter, TikTok and Reddit."
)

TRENDS_PROMPT = """List the {count} most promising trending topics for a new YouTube video\
{niche_clause}.
{signals}
Return one topic per line in the form:
<title> | <platform> | <why it is trending> | <reference link if known>
"""

SCRIPT_SYSTEM = (
    "You are a YouTube scriptwriter. You write original scripts inspired by a topic. You never "
    "copy wording, structure or distinctive ideas from source videos, and you avoid copyrighted "
    "lyrics, quotes longer than a sentence, and trademarks used as claims."
)

SCRIPT_PROMPT = """Write a {minutes}-minute YouTube script about this topic:
{topic}

Include a hook in the first 10 seconds, clear sections, and a call to action.
Mark narration lines with NARRATOR: and visual cues in [brackets]."""

SCRIPT_CRITERIA = """- Original: no copied phrasing or structure from any existing video
- No copyright or trademark risk
- Strong hook in the first 10 seconds
- Clear pacing, fits the target length
- Ends with a call to action"""

VOICE_SYSTEM = "You are a casting director choosing a narrator voice for a YouTube video."

VOICE_PROMPT = """Score each candidate voice from 1-10 for narrating the script below.
Reply with one line per voice in the form: <voice_id>: <score> - <reason>

Script excerpt:
{excerpt}

Candidates:
{candidates}"""

VIDEO_SYSTEM = (
    "You write prompts for AI text-to-video models. Prompts are concrete: subject, action, "
    "setting, camera, lighting, style and duration for each shot."
)

VIDEO_PROMPT = """Turn this script into a shot-by-shot video generation prompt.

Script:
{script}"""

VIDEO_CRITERIA = """- Every scene in the script has a matching shot
- Each shot names subject, action, setting, camera move, lighting and style
- Consistent characters and style across shots
- No real people, logos or copyrighted characters"""

THUMBNAIL_SYSTEM = (
    "You design YouTube thumbnails and write prompts for AI image models to produce them."
)

THUMBNAIL_PROMPT = """Write an image generation prompt for a 1280x720 YouTube thumbnail \
for this video.
Include the headline text (max 5 words), composition, colours and focal point.

Title: {title}
Script summary:
{summary}"""

THUMBNAIL_CRITERIA = """- Readable at small size, headline of 5 words or fewer
- One clear focal point and high contrast
- Matches the video's content, not clickbait
- Visually distinct from the source/competitor thumbnails
- No real people, logos or copyrighted characters"""
