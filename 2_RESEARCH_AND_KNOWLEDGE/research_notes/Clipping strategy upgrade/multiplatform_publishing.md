# Multi-platform publishing of vertical shorts (researched 2026-11-17)

Legend: [D] = official platform docs; [3P] = third-party guide (verify); [U] = common knowledge, not verified this session.

## Per-platform specs (export + copy)

### Takeaway
One master export works almost everywhere: **1080×1920, 9:16, H.264 High, AAC-LC 48 kHz stereo, 30 fps CFR, closed GOP 2–5 s, faststart MP4, ≤60 s, <100 MB**. The binding limits are IG API (≤90 s for Reels-tab, 100 MB), FB Reels API (3–90 s), X free (140 s / 512 MB) and Snapchat Spotlight (≤60 s per most guides).

### Spec table
| Platform | Aspect / res | Length | File / codec / fps | Cover | Copy limits | API publish |
|---|---|---|---|---|---|---|
| YouTube Shorts | 1:1 to 9:16; 1080×1920 | ≤3 min (uploads ≥15 Oct 2024) [3P] | MP4/MOV [3P] | Custom upload since 25 Jul 2026, YPP + desktop Studio only, no A/B [3P] | Title 100, desc 5000 [U] | Data API v3; private-lock if unaudited [D] |
| Instagram Reels | 9:16 required for Reels tab | 5–90 s via API for Reels tab; up to 15 min becomes plain video [3P] | ≤100 MB, H.264/HEVC, 23–60 fps, MP4/MOV, moov at front, AAC 48 kHz [3P] | `cover_url` 1080×1920 (grid crops center 1080×1080) or `thumb_offset` ms [3P] | **5 hashtags max** (Dec 2025) [3P]; caption 2200 [U] | Graph API, 100 posts/24 h [D] |
| Facebook Reels | 9:16; 1080×1920 rec, 540×960 min | **3–90 s** | MP4, H.264/H.265 (VP9/AV1 ok), 24–60 fps CFR, closed GOP 2–5 s, AAC-LC ≥128 kbps stereo 48 kHz [D] | – | – | `/{page-id}/video_reels`, 30 posts/24 h, Pages only, schedule 10 min–29 days ahead [D] |
| TikTok | 360–4096 px each side | API ≤10 min (some creators capped 3/5 min) [D] | ≤4 GB, MP4/WebM/MOV, H.264/H.265/VP8/VP9, 23–60 fps; chunks 5–64 MB [D] | – | Caption 2200 [3P] (one source; 4000 unconfirmed) | Content Posting API; private-only until audited [D] |
| X | 9:16 OK | Free 140 s / 512 MB; Premium 2–4 h (sources conflict) [3P] | API: 20 min/8 GB std, 125 min/16 GB Premium (changelog 1 Sep 2026, reported) [3P] | – | 280 chars free [U] | X API (paid tiers) [U] |
| Snapchat Spotlight | 1080×1920 [3P] | Conflicting: 5–60 s vs up to 3 min; sweet spot 10–30 s [3P] | – | – | 160 chars incl. hashtags, max 5 hashtags [3P, unconfirmed] | No public organic posting API found |

### Cited Findings
- YouTube Shorts: ≤3 min and square/vertical both required; #shorts tag does not decide classification — [Social Media Today](https://www.socialmediatoday.com/news/youtube-expands-3-minute-shorts-to-all-users/736967/), [OpenClip](https://openclip.app/guides/youtube-shorts-length)
- Shorts Audio Library tracks usable up to 90 s in a Short; some 60/30 s — [1of10](https://1of10.com/blog/how-long-can-youtube-shorts-be/)
- Custom Shorts thumbnails rolled out 25 Jul 2026 (announced by Neal Mohan 24 Jul), YPP creators, desktop, no Test & Compare — [Tubefilter](https://www.tubefilter.com/2026/07/24/youtube-shorts-custom-thumbnails-neal-mohan-feature-update/), [ppc.land](https://ppc.land/youtube-ends-2-year-wait-for-shorts-thumbnails-but-blocks-a-b-testing/); older vidIQ pages imply 2025 (conflict) — [vidIQ](https://vidiq.com/blog/post/youtube-shorts-custom-thumbnails/)
- Instagram caps hashtags at 5 per post/Reel (Mosseri, Dec 2025, gradual rollout) — [Business Today](https://www.businesstoday.in/technology/news/story/no-more-hashtag-stuffing-instagram-limits-hashtag-usage-to-just-5-per-reel-and-post-507444-2025-12-19), [Social Media Today](https://www.socialmediatoday.com/news/instagrams-implementing-new-limits-on-hashtag-use/808309/)
- IG API: `media_type=REELS`, 100 API posts per rolling 24 h, Trial Reels via `trial_params.graduation_strategy` = MANUAL or SS_PERFORMANCE, professional account required — [Meta docs](https://developers.facebook.com/docs/instagram-platform/content-publishing)
- IG Reels API specs, `cover_url`/`thumb_offset`, `share_to_feed`, no library music via API (dated 13 Mar 2026) — [PostProxy](https://postproxy.dev/blog/instagram-reels-api-publishing-guide/)
- FB Reels spec table, 30 posts/24 h, scheduling, Pages-only, Public only — [Meta Reels Publishing API](https://developers.facebook.com/docs/video-api/guides/reels-publishing)
- TikTok media rules (formats, 23–60 fps, 4 GB, 10 min) — [TikTok media transfer guide](https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide)
- X limits — [OpenTweet (checked Oct 2026)](https://opentweet.io/answers/x-api-video-upload-limit), [PostSyncer](https://postsyncer.com/blog/how-long-can-a-twitter-video-be)
- Snapchat Spotlight — [Kompozy length](https://kompozy.io/specs/snapchat-spotlight-video-length-limit), [Kompozy caption](https://kompozy.io/specs/snapchat-spotlight-caption-character-limit), [OpenClip](https://openclip.app/guides/snapchat-video-guide.md)

### Inferences
- Our current recipe (1080×1920, 30 fps, ≤60 s, −14 LUFS) already fits every platform; only add a size guard (<100 MB) and faststart flag.
- Our 9:16 cover JPG maps directly to IG `cover_url` and YouTube Shorts custom thumbnail (if channel is in YPP).
- A 5-hashtag cap fits our existing IG kit rule; reuse the same 5 tags for Snapchat.

### Gaps
- Official YouTube Shorts help page and official Snapchat Spotlight specs not reached; caption limits for YT/TikTok/X marked [U]/[3P].
- Whether YouTube `thumbnails.set` API applies to Shorts after the Jul 2026 change: unverified.
- LinkedIn/Pinterest not researched (out of budget). Posting-frequency guidance: no official source found.

## Cross-posting rules (watermarks, duplicates, hooks)

### Takeaway
Upload clean masters (no other-platform watermarks) natively to each platform. Instagram demotes accounts that mostly post unoriginal reposts; our own logo is fine.

### Cited Findings
- Instagram limits reach of Reels with visible TikTok marks (2021): shown to followers, kept out of Explore/recommendations — [Social Media Today](https://www.socialmediatoday.com/news/instagram-will-now-limit-the-reach-of-re-posts-from-tiktok-within-its-reels/594803), [XDA](https://www.xda-developers.com/psa-do-not-upload-tiktok-instagram-reels-without-removing-watermark/)
- Originality policy: accounts that mostly post unoriginal content stop being recommended; watermark/border/credit alone is not "meaningful creative input"; remixes with commentary/overlays favored — [Planoly](https://planoly.com/blog/instagram-updates-its-original-content-policy), [eMarketer](https://www.emarketer.com/content/instagram-s-algorithm-clamps-down-on-repurposed--unoriginal-photos-posts)
- Mosseri: your own brand logo on clips does not cause a penalty — [Social Media Today](https://www.socialmediatoday.com/news/instagram-clarifies-including-your-own-logo-on-a-reel-is-ok/730852/)

### Inferences
- Clips of third-party (e.g., MrBeast) footage are exactly what the originality rule targets; our edits (cold-open restructure, hooks, captions, SFX) are the "creative input". Keep them strong and avoid near-raw reuploads.
- Varying hook text per platform is optional; a different first caption line/title per platform is cheap and avoids identical metadata. No official source says identical files are penalized across platforms.

### Gaps
- No official YouTube/TikTok statement found on cross-platform duplicates in 2025–26.

## Automation (APIs, schedulers, native tools)

### Takeaway
For a solo creator, API self-builds hit audits: YouTube and TikTok lock posts to private until the app is audited. Meta (IG+FB) API is open with a professional account plus Page. Native schedulers (YouTube Studio, Meta Business Suite) cover 3 of the 6 platforms free.

### Cited Findings
- YouTube: `videos.insert` from unverified projects created after 28 Jul 2020 is locked private; requires an API compliance audit; locked videos can't be appealed, only re-uploaded — [Google videos docs](https://developers.google.com/youtube/v3/docs/videos), [Ayrshare](https://www.ayrshare.com/solutions/google-api-error-403-unverified-app-how-to-fix-the-audit-pipeline/)
- YouTube quota: upload cost reported cut from ~1,600 to ~100 units (revision 4 Dec 2025), and uploads moved to a separate 100-calls/day bucket (reported 1 Jun 2026); `uploadLimitExceeded` is a separate channel cap — [Blotato](https://www.blotato.com/blog/youtube-api-pricing), [bundle.social](https://bundle.social/blog/youtube-api-quota-exceeded-limits-fixes) (third-party; verify against [revision history](https://developers.google.com/youtube/v3/revision_history))
- TikTok: unaudited clients post private-only (SELF_ONLY), ≤5 users/24 h, accounts must be private; audit separate from app review — [TikTok Direct Post docs](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post), [bundle.social](https://bundle.social/blog/tiktok-api-approval)
- Meta: IG 100/24 h, FB Reels 30/24 h; FB supports `scheduled_publish_time` (10 min–29 days) — [Meta IG](https://developers.facebook.com/docs/instagram-platform/content-publishing), [Meta FB](https://developers.facebook.com/docs/video-api/guides/reels-publishing)
- Postiz: AGPL-3.0, self-hostable, ~29k GitHub stars, very active, also hosted cloud; Mixpost: MIT, Lite edition only FB Pages/Mastodon/X, Pro ($299 one-time) unlocks the rest — [OpenAlternative](https://openalternative.co/compare/mixpost/vs/postiz), [Postiz TikTok provider docs](https://docs.postiz.com/providers/tiktok)

### Inferences
- Self-hosted Postiz still needs your own developer apps per platform (YouTube/TikTok audits apply) unless you use Postiz Cloud, whose apps are already approved.
- Meta Business Suite natively schedules FB+IG Reels with custom cover; YouTube Studio schedules Shorts. Both free, no API work [U].

### Gaps
- Meta Business Suite scheduling limits and Postiz's current TikTok/YouTube audit status not verified from primary docs.
- X API pricing tiers in 2026 not checked.

## Recommended setup (solo creator, Windows)

### Takeaway
Automate the export and copy, publish manually or semi-manually; add an API scheduler later only if volume grows.

### Inferences
- **Automate (pipeline):** one master MP4 (spec above, faststart, <100 MB); per-platform copy files generated from `YOUTUBE_CAPTIONS.md`: YT (title ≤100, desc, 3–4 tags), IG (≤5 hashtags, alt text), FB (IG caption), TikTok (caption ≤2200 plus hashtags), X (≤280 chars), Snapchat (≤160 chars, ≤5 tags); a `schedule.csv` (date, platform, file, cover, caption).
- **Manual/native:** YouTube Studio scheduling plus custom Shorts cover if YPP; Meta Business Suite for IG+FB Reels (one upload, cover, Trial Reel option in IG app); TikTok app/web scheduler; X and Snapchat by hand.
- **Optional later:** Postiz Cloud (or self-hosted Postiz with own Meta app) for a single queue; avoid self-built YouTube/TikTok API until audits are passed, otherwise uploads stay private.
