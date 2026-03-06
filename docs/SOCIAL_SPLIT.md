Split social blocklists
=======================

This repository contains a helper script `split_social_blocklist.py` that splits a blocklist into separate files for individual social platforms.

Quick usage
-----------

1. Ensure you have the input blocklist (e.g. `social-blocker.txt`) in the repo root or provide a full path.
2. Run the script with your desired platform patterns:

```
python split_social_blocklist.py -i social-blocker.txt -p youtube.com,tiktok.com,facebook.com -o social-blocks
```

Outputs:
- `social-blocks/youtube.txt`
- `social-blocks/tiktok.txt`
- `social-blocks/facebook.txt`
- `social-blocks/other.txt` (domains that didn't match any pattern)

Notes
-----
- Patterns can be any domain substring (e.g. `youtube.com`, `youtu.be`, `tiktok.com`).
- The script extracts domain-like tokens from the input file and matches them using substring/endswith rules.
- Use `--hosts-format` to generate `0.0.0.0 domain` style lines if needed.

Removing social domains from the main blocker file
-------------------------------------------------

You can also have the script write a filtered copy of the input file with social domains removed, or overwrite the input file in-place:

- Write filtered copy:

```
python split_social_blocklist.py -i blocker.txt -p youtube.com,tiktok.com,facebook.com -o social-blocks --main-out blocker_no_social.txt
```

- Overwrite input (use with caution):

```
python split_social_blocklist.py -i blocker.txt -p youtube.com,tiktok.com,facebook.com -o social-blocks --inplace
```

This will remove lines that contain matched social domains and write the filtered file to the requested path.

If you'd like, I can also add an example GitHub Action to run this on commits or integrate it into `combine_bd.py` so the per-platform files are regenerated automatically.