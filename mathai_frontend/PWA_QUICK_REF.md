# 📱 Quick Reference: PWA Commands

## Development
```bash
npm run dev          # Start dev server with PWA (localhost:5173)
```

## Build & Deploy
```bash
npm run build        # Build production PWA
npm run preview      # Preview production build (localhost:4173)
npm run build:pwa    # Build + success message
npm run preview:pwa  # Build + preview in one command
```

## Test Installation

**Desktop Chrome:**
1. Open http://localhost:5173
2. Click install icon (➕) in address bar
3. App opens in standalone window

**Mobile (requires public URL):**
- Android: Menu → "Add to Home Screen"
- iOS: Share → "Add to Home Screen"

## Deploy (Free Options)

**Vercel:**
```bash
npm i -g vercel && vercel
```

**Netlify:**
```bash
npm run build
# Drag dist/ to netlify.com
```

**Manual:**
```bash
npm run build
# Upload dist/ folder to your server
```

## PWA Debug

**Check PWA Status:**
- Chrome DevTools → Application → Manifest
- Chrome DevTools → Application → Service Workers
- Chrome DevTools → Lighthouse → PWA Audit

**Clear Cache:**
- DevTools → Application → Storage → Clear site data
- Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)

## Files Modified
- ✅ `vite.config.ts` - PWA configuration
- ✅ `index.html` - Meta tags & icons
- ✅ `package.json` - PWA scripts

## New Files
- 📄 `public/icon.svg` - App icon
- 📄 `public/pwa-*.svg` - PWA icons
- 📄 `public/offline.html` - Offline page
- 📚 `PWA_SETUP.md` - Full documentation
- 📋 `PWA_COMPLETE.md` - Summary

## Current Status
✅ PWA fully configured and working
✅ Service worker active
✅ Installable on desktop
✅ Ready for mobile deployment

**Next:** Deploy to get public URL, then test on mobile!
