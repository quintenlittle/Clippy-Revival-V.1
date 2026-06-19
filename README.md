# 📎 Clippy Revival

### *"It looks like you're trying to bring back a beloved/cursed Windows mascot using artificial intelligence. Would you like help?"*

**[ Yes ]**　　**[ No, but thanks for asking like you actually mean it this time ]**

---

He showed up uninvited in Office 97. He outlived three of your relationships, two laptops, and one entire career pivot. Microsoft fired him in 2007 like a guy who peaked in middle management. He never even got severance.

This is his comeback tour. Except now he runs on a real LLM, lives in your system tray, and can actually read what's on your screen instead of just vibing near your Word document insisting you're writing a letter.

You're welcome, and we're sorry, in equal measure.

---

## What this actually is

A floating, draggable, fully transparent desktop Clippy that:

- **Reads** the text in whatever window you're currently in (Windows Accessibility APIs, not screenshots — he's not *watching* you, he's just nosy in a structured way)
- **Answers questions**, with your choice of brain transplant: a free local model via Ollama, a HuggingFace model running on your own GPU, or cloud Claude / GPT / Gemini if you want him smarter than your hardware
- **Talks back** in an actual hand-drawn speech bubble, typed out letter by letter like it's 1998 and the internet still made that modem noise
- **Plays his classic animations** — 23 of the originals, ripped straight from the source, gritty low-res charm fully intact
- Has zero persistent UI cluttering your desktop. Right-click him. That's the whole interface. Just like the actual Clippy required zero documentation to be deeply, personally annoying.

No telemetry, no cloud account required (unless you want one), no "Microsoft 365 Copilot" rebrand energy. Just a paperclip with eyes and an opinion, running entirely on your machine, answering to nobody but you.

---

## Before you start

You need:
- **Windows 10/11**
- **Python 3.13** — grab it from **[python.org/downloads](https://www.python.org/downloads/)**, NOT bundled in this repo (nobody needs a 25MB installer.exe sitting in their git history for the rest of time). On the install screen, check **"Add python.exe to PATH"** — this is the step everyone skips and then is sad about.
- Either **[Ollama](https://ollama.com)** (free, local, runs entirely offline, your secrets stay yours) or an API key for Claude/GPT/Gemini if you want to phone a friend with more VRAM than you.

---

## Setup (takes about as long as Windows 98 took to boot)

```powershell
# 1. Get a local model ready (skip this if you're going cloud-only)
irm https://ollama.com/install.ps1 | iex
ollama pull dolphin-mistral
```

```bat
:: 2. From inside this folder:
install.bat
```

```bat
:: 3. If you want a real .exe instead of running from source:
build_exe.bat
```

Find `Clippy.exe` waiting for you in `dist\`. Drag a shortcut to your **Desktop**, or into `shell:startup` (Win+R, type that, hit Enter) if you want him to greet you every single time you log in like it's never NOT 2003 in your house.

Got an API key for Claude, GPT, or Gemini instead of (or alongside) Ollama? Run `set_api_key.bat` — it asks for the key with hidden input and writes it straight to your local `config.json`. It never touches a network, a chat log, or anyone but you.

---

## How to use him

**Right-click Clippy.** That's it, that's the manual:

| Option | Does |
|---|---|
| **Ask** | Pops a tiny input box, cursor blinking and ready — ask him anything |
| **Animate** | Plays one of his 23 classic animations at random, then settles back down |
| **Terminate** | Mercy killing, round two. He'll understand. He's used to it. |

Drag him anywhere by clicking and holding. `Ctrl+Alt+C` brings him back if you've hidden him and forgotten where you put him, which, statistically, you will.

---

## Making him smarter (or dumber, your call)

Everything routes through `config.json`. Want a different local model?

```json
{ "active_backend": "ollama", "ollama": { "model": "llama3" } }
```

Want Claude/GPT/Gemini instead? Change `active_backend` and run `set_api_key.bat`. Full details on every backend, plus how to wire up your own, are documented inline in `src/backends/`.

---

## Customizing the look

`assets/avatar.png` is just a PNG. Replace it with literally anything — square, transparent background, any resolution. `assets/animations/` holds the 23 classic GIFs; drop your own transparent looping GIFs in there and they'll get picked up automatically by **Animate**.

Yes, the current avatar deliberately looks a little gritty and dithered instead of crisp and modern. That's not a bug. That's *fidelity*. He's supposed to look like he's been compressed through a 56k modem a few times. Respect the texture.

---

## A note on intellectual property, because we're adults here

Clippy — the name, the design, the soul of a thousand "It looks like you're writing a letter" jokes — belongs to Microsoft. This project bundles classic Clippy artwork and animations because nostalgia projects kind of require the actual nostalgia, but none of that art is original work and none of it is covered by this repo's license below. This is a fan-made, non-commercial love letter, not a Microsoft product, and not legal advice about what you're allowed to do with it. Use your judgment.

---

## License

The code in this repo (everything in `src/`, the build scripts, the general approach of "what if Clippy had Wi-Fi and a god complex") is MIT licensed — do whatever you want with it.

The Clippy artwork and animations in `assets/` are © Microsoft, included here for nostalgic, non-commercial, personal use only. See the note above.

---

*Built by someone who remembers when "the cloud" just meant Hotmail, for everyone else who does too.*
