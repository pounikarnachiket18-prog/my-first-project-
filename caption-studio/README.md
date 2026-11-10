# Caption Studio

Write hooks, captions and hashtags for Mindset Mode India Reels and YouTube Shorts.

## Open it
Double-click `index.html`. It opens in Chrome, Edge or Firefox. There's nothing to install, and it works offline (only the Hindi font comes from Google Fonts).

## How to use it
1. **Topic, pillar, language, platform.** Type what the video is about, or press **🎲 Idea** for a topic. Pick a pillar (Mindset, Discipline, Focus, Growth), the language (English, Hinglish or हिंदी), and Instagram Reel or YouTube Shorts.
2. **Pick a hook.** You get 8 opening lines for your topic. Each one shows its word count, and any hook over 12 words is marked "long". Press **Shuffle** for new ones, then **Use** to put one in the caption. You can also type your own.
3. **Build the caption.** Write your key points one per line, then choose a bullet style and a call to action: save, share, comment a keyword, or follow your @handle.
4. **Hashtags.** Use the slider to set how many. Tags are ordered from most to least relevant: a tag made from your topic, `#mindsetmodeindia`, the platform tag, then pillar tags. Click a tag to turn it off. You can also hide them below a few dots.
5. **Preview and copy.** The preview shows the finished caption with character and hashtag counts checked against each platform's limits. For Shorts you also get a title, with a warning past 70 characters.

Your work in progress is remembered, so closing the tab doesn't lose it.

## Idea bank
Press **Save to idea bank** to keep a caption. In the **Idea bank** tab you can:
- move each idea through **Idea → Scripted → Shot → Posted**
- filter by status or search
- copy a caption, or load it back into the editor to change it
- **Export CSV** to open your list in Excel or Google Sheets
- **Backup / Restore** a `.json` file

Ideas are stored in this browser only. Take a backup now and then, and use it to move ideas to another computer.

## Add your own hooks, hashtags or topics
Open `index.html` in a text editor and find the **Content library** near the top of the `<script>`:
- `HOOKS`: opening lines for each language. `{t}` becomes the topic, and `{T}` is the topic with a capital first letter. Lines under `any` are used for every pillar.
- `CTAS`: the call-to-action lines. `{k}` is the comment keyword and `{h}` is your handle.
- `TAGS`: the hashtag sets.
- `TOPIC_IDEAS`: the topics the 🎲 button picks from.
