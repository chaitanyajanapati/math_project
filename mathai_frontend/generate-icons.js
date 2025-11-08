// Simple icon generator for PWA
// This creates basic colored placeholder icons
// For production, use a proper icon generator like https://www.pwabuilder.com/imageGenerator

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create a simple SVG icon
const createSvgIcon = (size) => `
<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="${size}" height="${size}" fill="url(#grad)" rx="${size * 0.15}"/>
  <text x="50%" y="50%" text-anchor="middle" dy=".35em" fill="white" font-size="${size * 0.5}" font-weight="bold" font-family="Arial, sans-serif">∑</text>
</svg>
`;

// Create icons directory
const publicDir = path.join(__dirname, 'public');
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
}

// Generate SVG icons (browsers can use these directly for now)
fs.writeFileSync(path.join(publicDir, 'icon.svg'), createSvgIcon(512));

console.log('✓ Generated icon.svg');
console.log('\nFor production PWA icons (PNG format), please:');
console.log('1. Visit https://www.pwabuilder.com/imageGenerator');
console.log('2. Upload a 512x512 PNG image (create one from icon.svg)');
console.log('3. Download the generated icons');
console.log('4. Place pwa-192x192.png and pwa-512x512.png in the public/ folder');
console.log('\nOr use ImageMagick to convert:');
console.log('  convert public/icon.svg -resize 192x192 public/pwa-192x192.png');
console.log('  convert public/icon.svg -resize 512x512 public/pwa-512x512.png');
