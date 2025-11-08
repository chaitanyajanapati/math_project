import { useEffect, useRef } from 'react';

interface GeometryVisualizerProps {
  question: string;
  className?: string;
}

/**
 * SVG-based geometry visualizer that parses questions and draws shapes
 * Supports: circles, rectangles, squares, triangles, cubes (3D projection)
 */
export default function GeometryVisualizer({ question, className = '' }: GeometryVisualizerProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = svgRef.current;
    // Clear previous content
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }

    const q = question.toLowerCase();
    
    // Extract numbers from question
    const numbers = question.match(/\d+(\.\d+)?/g)?.map(Number) || [];
    
    // Determine shape type and draw
    if (q.includes('circle')) {
      drawCircle(svg, numbers[0] || 50);
    } else if (q.includes('square')) {
      drawSquare(svg, numbers[0] || 100);
    } else if (q.includes('rectangle')) {
      drawRectangle(svg, numbers[0] || 120, numbers[1] || 80);
    } else if (q.includes('triangle')) {
      if (q.includes('right')) {
        drawRightTriangle(svg, numbers[0] || 80, numbers[1] || 60);
      } else {
        drawTriangle(svg, numbers[0] || 100);
      }
    } else if (q.includes('cube')) {
      drawCube(svg, numbers[0] || 80);
    } else if (q.includes('sphere')) {
      drawSphere(svg, numbers[0] || 60);
    } else if (q.includes('cylinder')) {
      drawCylinder(svg, numbers[0] || 50, numbers[1] || 100);
    } else if (q.includes('cone')) {
      drawCone(svg, numbers[0] || 50, numbers[1] || 120);
    } else {
      // Default: show a generic shape
      drawPlaceholder(svg);
    }

  }, [question]);

  return (
    <div className={`bg-white rounded-lg border-2 border-gray-300 p-4 ${className}`}>
      <svg
        ref={svgRef}
        viewBox="0 0 400 300"
        className="w-full h-full"
        style={{ maxHeight: '300px' }}
      />
    </div>
  );
}

// Helper functions to draw shapes

function createSVGElement(tag: string, attributes: Record<string, string | number>): SVGElement {
  const elem = document.createElementNS('http://www.w3.org/2000/svg', tag);
  Object.entries(attributes).forEach(([key, value]) => {
    elem.setAttribute(key, String(value));
  });
  return elem;
}

function addLabel(svg: SVGSVGElement, text: string, x: number, y: number, fontSize = 14) {
  const label = createSVGElement('text', {
    x,
    y,
    'font-size': fontSize,
    'font-weight': 'bold',
    fill: '#1e40af',
    'text-anchor': 'middle',
  });
  label.textContent = text;
  svg.appendChild(label);
}

function drawCircle(svg: SVGSVGElement, radius: number) {
  const scale = Math.min(100 / radius, 2);
  const r = radius * scale;
  const cx = 200;
  const cy = 150;

  // Circle
  svg.appendChild(createSVGElement('circle', {
    cx, cy, r,
    fill: 'rgba(59, 130, 246, 0.1)',
    stroke: '#3b82f6',
    'stroke-width': 3,
  }));

  // Radius line
  svg.appendChild(createSVGElement('line', {
    x1: cx, y1: cy,
    x2: cx + r, y2: cy,
    stroke: '#ef4444',
    'stroke-width': 2,
    'stroke-dasharray': '5,5',
  }));

  // Labels
  addLabel(svg, `r = ${radius}`, cx + r / 2, cy - 10);
  addLabel(svg, `Circle`, cx, cy + r + 25);
}

function drawSquare(svg: SVGSVGElement, side: number) {
  const scale = Math.min(150 / side, 2);
  const s = side * scale;
  const x = (400 - s) / 2;
  const y = (300 - s) / 2;

  svg.appendChild(createSVGElement('rect', {
    x, y, width: s, height: s,
    fill: 'rgba(34, 197, 94, 0.1)',
    stroke: '#22c55e',
    'stroke-width': 3,
  }));

  addLabel(svg, `${side}`, x + s / 2, y - 10);
  addLabel(svg, `${side}`, x - 15, y + s / 2);
  addLabel(svg, `Square`, x + s / 2, y + s + 25);
}

function drawRectangle(svg: SVGSVGElement, length: number, width: number) {
  const scale = Math.min(250 / Math.max(length, width), 2);
  const l = length * scale;
  const w = width * scale;
  const x = (400 - l) / 2;
  const y = (300 - w) / 2;

  svg.appendChild(createSVGElement('rect', {
    x, y, width: l, height: w,
    fill: 'rgba(168, 85, 247, 0.1)',
    stroke: '#a855f7',
    'stroke-width': 3,
  }));

  addLabel(svg, `${length}`, x + l / 2, y - 10);
  addLabel(svg, `${width}`, x - 20, y + w / 2);
  addLabel(svg, `Rectangle`, x + l / 2, y + w + 25);
}

function drawTriangle(svg: SVGSVGElement, base: number) {
  const scale = Math.min(200 / base, 2);
  const b = base * scale;
  const h = (b * Math.sqrt(3)) / 2;
  
  const x1 = 200 - b / 2;
  const x2 = 200 + b / 2;
  const x3 = 200;
  const y1 = 200;
  const y2 = 200;
  const y3 = 200 - h;

  svg.appendChild(createSVGElement('polygon', {
    points: `${x1},${y1} ${x2},${y2} ${x3},${y3}`,
    fill: 'rgba(251, 146, 60, 0.1)',
    stroke: '#fb923c',
    'stroke-width': 3,
  }));

  addLabel(svg, `${base}`, 200, y1 + 20);
  addLabel(svg, `Triangle`, 200, y1 + 40);
}

function drawRightTriangle(svg: SVGSVGElement, leg1: number, leg2: number) {
  const scale = Math.min(180 / Math.max(leg1, leg2), 2);
  const a = leg1 * scale;
  const b = leg2 * scale;
  
  const x1 = 120;
  const y1 = 220;
  const x2 = x1 + a;
  const y2 = y1;
  const x3 = x1;
  const y3 = y1 - b;

  // Triangle
  svg.appendChild(createSVGElement('polygon', {
    points: `${x1},${y1} ${x2},${y2} ${x3},${y3}`,
    fill: 'rgba(239, 68, 68, 0.1)',
    stroke: '#ef4444',
    'stroke-width': 3,
  }));

  // Right angle indicator
  const cornerSize = 15;
  svg.appendChild(createSVGElement('rect', {
    x: x1, y: y3,
    width: cornerSize, height: cornerSize,
    fill: 'none',
    stroke: '#374151',
    'stroke-width': 2,
  }));

  // Hypotenuse
  const hyp = Math.sqrt(leg1 * leg1 + leg2 * leg2).toFixed(1);
  
  addLabel(svg, `${leg1}`, x1 + a / 2, y1 + 20);
  addLabel(svg, `${leg2}`, x1 - 25, y3 + b / 2);
  addLabel(svg, `c = ${hyp}`, x1 + a / 2 + 20, y3 + b / 2 - 10, 12);
  addLabel(svg, `Right Triangle`, 200, 270);
}

function drawCube(svg: SVGSVGElement, edge: number) {
  const scale = Math.min(120 / edge, 1.5);
  const e = edge * scale;
  const offset = e * 0.4;

  // Back face
  svg.appendChild(createSVGElement('rect', {
    x: 150 + offset, y: 100,
    width: e, height: e,
    fill: 'rgba(156, 163, 175, 0.3)',
    stroke: '#9ca3af',
    'stroke-width': 2,
  }));

  // Front face
  svg.appendChild(createSVGElement('rect', {
    x: 150, y: 100 + offset,
    width: e, height: e,
    fill: 'rgba(59, 130, 246, 0.2)',
    stroke: '#3b82f6',
    'stroke-width': 3,
  }));

  // Connecting lines
  [[150, 100 + offset, 150 + offset, 100],
   [150 + e, 100 + offset, 150 + offset + e, 100],
   [150, 100 + offset + e, 150 + offset, 100 + e],
   [150 + e, 100 + offset + e, 150 + offset + e, 100 + e]].forEach(([x1, y1, x2, y2]) => {
    svg.appendChild(createSVGElement('line', {
      x1, y1, x2, y2,
      stroke: '#6b7280',
      'stroke-width': 2,
    }));
  });

  addLabel(svg, `${edge}`, 150 + e / 2, 100 + offset + e + 25);
  addLabel(svg, `Cube`, 200, 250);
}

function drawSphere(svg: SVGSVGElement, radius: number) {
  const scale = Math.min(100 / radius, 2);
  const r = radius * scale;

  // Outer circle
  svg.appendChild(createSVGElement('circle', {
    cx: 200, cy: 150, r,
    fill: 'url(#sphereGradient)',
    stroke: '#3b82f6',
    'stroke-width': 3,
  }));

  // Gradient for 3D effect
  const defs = createSVGElement('defs', {});
  const gradient = createSVGElement('radialGradient', { id: 'sphereGradient' });
  gradient.innerHTML = `
    <stop offset="0%" style="stop-color:rgba(59, 130, 246, 0.4)" />
    <stop offset="100%" style="stop-color:rgba(59, 130, 246, 0.1)" />
  `;
  defs.appendChild(gradient);
  svg.insertBefore(defs, svg.firstChild);

  // Radius
  svg.appendChild(createSVGElement('line', {
    x1: 200, y1: 150,
    x2: 200 + r, y2: 150,
    stroke: '#ef4444',
    'stroke-width': 2,
    'stroke-dasharray': '5,5',
  }));

  addLabel(svg, `r = ${radius}`, 200 + r / 2, 145);
  addLabel(svg, `Sphere`, 200, 150 + r + 25);
}

function drawCylinder(svg: SVGSVGElement, radius: number, height: number) {
  const scaleR = Math.min(70 / radius, 1.5);
  const scaleH = Math.min(150 / height, 1.5);
  const r = radius * scaleR;
  const h = height * scaleH;
  const cx = 200;
  const topY = 80;

  // Top ellipse
  svg.appendChild(createSVGElement('ellipse', {
    cx, cy: topY, rx: r, ry: r * 0.3,
    fill: 'rgba(34, 197, 94, 0.2)',
    stroke: '#22c55e',
    'stroke-width': 2,
  }));

  // Sides
  svg.appendChild(createSVGElement('line', {
    x1: cx - r, y1: topY,
    x2: cx - r, y2: topY + h,
    stroke: '#22c55e',
    'stroke-width': 3,
  }));
  svg.appendChild(createSVGElement('line', {
    x1: cx + r, y1: topY,
    x2: cx + r, y2: topY + h,
    stroke: '#22c55e',
    'stroke-width': 3,
  }));

  // Bottom ellipse
  svg.appendChild(createSVGElement('ellipse', {
    cx, cy: topY + h, rx: r, ry: r * 0.3,
    fill: 'rgba(34, 197, 94, 0.3)',
    stroke: '#22c55e',
    'stroke-width': 3,
  }));

  addLabel(svg, `r = ${radius}`, cx, topY - 15);
  addLabel(svg, `h = ${height}`, cx + r + 30, topY + h / 2);
  addLabel(svg, `Cylinder`, cx, topY + h + 30);
}

function drawCone(svg: SVGSVGElement, radius: number, height: number) {
  const scaleR = Math.min(80 / radius, 1.5);
  const scaleH = Math.min(150 / height, 1.5);
  const r = radius * scaleR;
  const h = height * scaleH;
  const cx = 200;
  const tipY = 60;
  const baseY = tipY + h;

  // Cone sides
  svg.appendChild(createSVGElement('line', {
    x1: cx, y1: tipY,
    x2: cx - r, y2: baseY,
    stroke: '#f59e0b',
    'stroke-width': 3,
  }));
  svg.appendChild(createSVGElement('line', {
    x1: cx, y1: tipY,
    x2: cx + r, y2: baseY,
    stroke: '#f59e0b',
    'stroke-width': 3,
  }));

  // Base
  svg.appendChild(createSVGElement('ellipse', {
    cx, cy: baseY, rx: r, ry: r * 0.3,
    fill: 'rgba(245, 158, 11, 0.2)',
    stroke: '#f59e0b',
    'stroke-width': 3,
  }));

  // Height line
  svg.appendChild(createSVGElement('line', {
    x1: cx, y1: tipY,
    x2: cx, y2: baseY,
    stroke: '#ef4444',
    'stroke-width': 2,
    'stroke-dasharray': '5,5',
  }));

  addLabel(svg, `r = ${radius}`, cx, baseY + 20);
  addLabel(svg, `h = ${height}`, cx + 15, tipY + h / 2);
  addLabel(svg, `Cone`, cx, baseY + 40);
}

function drawPlaceholder(svg: SVGSVGElement) {
  addLabel(svg, 'Geometry Visualizer', 200, 140, 18);
  addLabel(svg, 'Shape will appear when question is generated', 200, 170, 12);
}
