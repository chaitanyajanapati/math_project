import { useEffect, useRef, memo } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

interface MathRendererProps {
  content: string;
  displayMode?: boolean;
  className?: string;
}

/**
 * MathRenderer component that converts LaTeX expressions to rendered math
 * Detects inline ($...$) and display ($$...$$) math expressions
 * 
 * Memoized to prevent unnecessary re-renders when props haven't changed
 */
const MathRenderer = memo(function MathRenderer({ content, displayMode = false, className = '' }: MathRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    try {
      // Convert common math patterns to LaTeX if not already in LaTeX format
      let processedContent = content;

      // Pattern replacements for common math notation
      const patterns = [
        // Fractions: a/b -> \frac{a}{b} (only for simple fractions)
        { regex: /(\d+)\/(\d+)/g, replace: '\\frac{$1}{$2}' },
        // Exponents: x^2 -> x^{2}
        { regex: /\^(\d+)/g, replace: '^{$1}' },
        // Square root: sqrt(x) -> \sqrt{x}
        { regex: /sqrt\(([^)]+)\)/g, replace: '\\sqrt{$1}' },
        // Pi symbol: π or pi -> \pi
        { regex: /π|pi\b/g, replace: '\\pi' },
        // Multiplication: × -> \times
        { regex: /×/g, replace: '\\times' },
        // Division: ÷ -> \div
        { regex: /÷/g, replace: '\\div' },
        // Less than or equal: <= -> \leq
        { regex: /<=/g, replace: '\\leq' },
        // Greater than or equal: >= -> \geq
        { regex: />=/g, replace: '\\geq' },
        // Not equal: != -> \neq
        { regex: /!=/g, replace: '\\neq' },
      ];

      // Apply pattern replacements
      for (const pattern of patterns) {
        processedContent = processedContent.replace(pattern.regex, pattern.replace);
      }

      // Check if content has LaTeX delimiters
      const hasDisplayMath = /\$\$(.+?)\$\$/g.test(processedContent);
      const hasInlineMath = /(?<!\$)\$(?!\$)(.+?)\$(?!\$)/g.test(processedContent);

      if (hasDisplayMath || hasInlineMath || displayMode) {
        // Split content by math delimiters
        const parts: Array<{ type: 'text' | 'math', content: string, display: boolean }> = [];
        let lastIndex = 0;
        
        // Find all math expressions
        const displayMathRegex = /\$\$(.+?)\$\$/g;
        const inlineMathRegex = /(?<!\$)\$(?!\$)(.+?)\$(?!\$)/g;
        
        let match: RegExpExecArray | null;
        const allMatches: Array<{ index: number, length: number, content: string, display: boolean }> = [];
        
        // Collect display math matches
        while ((match = displayMathRegex.exec(processedContent)) !== null) {
          allMatches.push({
            index: match.index,
            length: match[0].length,
            content: match[1],
            display: true
          });
        }
        
        // Collect inline math matches
        while ((match = inlineMathRegex.exec(processedContent)) !== null) {
          // Skip if this position is already part of display math
          if (!allMatches.some(m => match!.index >= m.index && match!.index < m.index + m.length)) {
            allMatches.push({
              index: match.index,
              length: match[0].length,
              content: match[1],
              display: false
            });
          }
        }
        
        // Sort matches by index
        allMatches.sort((a, b) => a.index - b.index);
        
        // Build parts array
        allMatches.forEach(m => {
          if (m.index > lastIndex) {
            parts.push({
              type: 'text',
              content: processedContent.slice(lastIndex, m.index),
              display: false
            });
          }
          parts.push({
            type: 'math',
            content: m.content,
            display: m.display
          });
          lastIndex = m.index + m.length;
        });
        
        // Add remaining text
        if (lastIndex < processedContent.length) {
          parts.push({
            type: 'text',
            content: processedContent.slice(lastIndex),
            display: false
          });
        }

        // Render parts
        containerRef.current.innerHTML = '';
        parts.forEach(part => {
          if (part.type === 'text') {
            const textNode = document.createTextNode(part.content);
            containerRef.current?.appendChild(textNode);
          } else {
            const span = document.createElement('span');
            try {
              katex.render(part.content, span, {
                displayMode: part.display,
                throwOnError: false,
                strict: false,
              });
            } catch {
              // If KaTeX fails, show original content
              span.textContent = part.display ? `$$${part.content}$$` : `$${part.content}$`;
            }
            containerRef.current?.appendChild(span);
          }
        });
      } else {
        // No math delimiters found - render as plain text or single math expression
        if (displayMode) {
          // Treat entire content as math
          try {
            katex.render(processedContent, containerRef.current, {
              displayMode: true,
              throwOnError: false,
              strict: false,
            });
          } catch {
            containerRef.current.textContent = content;
          }
        } else {
          // Plain text
          containerRef.current.textContent = content;
        }
      }
    } catch {
      // Fallback to plain text on any error
      if (containerRef.current) {
        containerRef.current.textContent = content;
      }
    }
  }, [content, displayMode]);

  return <div ref={containerRef} className={className} />;
});

export default MathRenderer;
