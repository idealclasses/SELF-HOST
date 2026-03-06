#!/bin/bash

# Move DNS files
mv /workspaces/PI-HOLE-BLOCK/upstream_dns.txt /workspaces/PI-HOLE-BLOCK/dns/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/upstream_sources.txt /workspaces/PI-HOLE-BLOCK/dns/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/check_dns_updates.py /workspaces/PI-HOLE-BLOCK/dns/ 2>/dev/null

# Move IPTV files
mv /workspaces/PI-HOLE-BLOCK/BD_channels.m3u.bak /workspaces/PI-HOLE-BLOCK/iptv/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/check_iptv_links.py /workspaces/PI-HOLE-BLOCK/iptv/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/add_tvgid.py /workspaces/PI-HOLE-BLOCK/iptv/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/create_working_channels.py /workspaces/PI-HOLE-BLOCK/iptv/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/combine_bd.py /workspaces/PI-HOLE-BLOCK/iptv/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/extract_bd.py /workspaces/PI-HOLE-BLOCK/iptv/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/update_bd_channels.py /workspaces/PI-HOLE-BLOCK/iptv/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/update_bd_channels_enhanced.py /workspaces/PI-HOLE-BLOCK/iptv/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/update_youtube_urls.py /workspaces/PI-HOLE-BLOCK/iptv/ 2>/dev/null

# Move Blocklist files
mv /workspaces/PI-HOLE-BLOCK/blocker.txt /workspaces/PI-HOLE-BLOCK/blocklists/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/social-block.txt /workspaces/PI-HOLE-BLOCK/blocklists/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/youtube-blocklist-merged.txt /workspaces/PI-HOLE-BLOCK/blocklists/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/merge_blocklists.py /workspaces/PI-HOLE-BLOCK/blocklists/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/split_social_blocklist.py /workspaces/PI-HOLE-BLOCK/blocklists/ 2>/dev/null

# Move Documentation files
mv /workspaces/PI-HOLE-BLOCK/README.md /workspaces/PI-HOLE-BLOCK/docs/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/SOCIAL_SPLIT.md /workspaces/PI-HOLE-BLOCK/docs/ 2>/dev/null

# Move Image files
mv /workspaces/PI-HOLE-BLOCK/Copilot_20260127_010822.png /workspaces/PI-HOLE-BLOCK/images/ 2>/dev/null

# Move utility scripts
mv /workspaces/PI-HOLE-BLOCK/check_and_add_hutho.py /workspaces/PI-HOLE-BLOCK/scripts/ 2>/dev/null
mv /workspaces/PI-HOLE-BLOCK/check_and_add_saifujjaman.py /workspaces/PI-HOLE-BLOCK/scripts/ 2>/dev/null

echo "✓ Files organized successfully!"
echo ""
echo "Organization summary:"
echo "- dns/: DNS configuration files"
echo "- iptv/: IPTV/M3U playlist files and scripts"
echo "- blocklists/: DNS blocklists and related scripts"
echo "- docs/: Documentation files"
echo "- images/: Image files"
echo "- scripts/: Additional utility scripts"
