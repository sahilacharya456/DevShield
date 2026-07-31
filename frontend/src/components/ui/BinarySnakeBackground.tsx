"use client";

import { useEffect, useRef } from "react";

export function BinarySnakeBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext("2d", { alpha: false }); // Optimize for performance
    if (!ctx) return;

    let width = window.innerWidth;
    let height = window.innerHeight;

    const resizeCanvas = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Matrix background data
    const fontSize = 16;
    const columns = Math.floor(width / fontSize);
    const drops: number[] = [];
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -100; // Start offscreen randomly
    }

    // Main animation loop
    let animId: number;
    const draw = () => {
      // 1. Draw the absolute deep black background with a slight fade for motion blur
      ctx.fillStyle = "rgba(0, 0, 0, 0.2)";
      ctx.fillRect(0, 0, width, height);

      // 2. Draw falling hacker Matrix code (dense and fast)
      ctx.fillStyle = "rgba(0, 255, 128, 0.1)"; // Darker green so it doesn't distract from the snake
      ctx.font = `bold ${fontSize}px monospace`;
      ctx.textAlign = "center";
      
      for (let i = 0; i < columns; i++) {
        // Only draw if on screen
        if (drops[i] > 0) {
            const char = Math.random() > 0.5 ? "1" : "0";
            ctx.fillText(char, i * fontSize, drops[i] * fontSize);
        }
        
        // Reset randomly when it goes off screen
        if (drops[i] * fontSize > height && Math.random() > 0.95) {
          drops[i] = 0;
        }
        drops[i] += 0.5; // Speed of falling
      }

      // 3. (Snake removed from here, now in CyberSnakeOverlay)

      animId = requestAnimationFrame(draw);
    };

    animId = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <canvas 
      ref={canvasRef} 
      className="fixed top-0 left-0 w-full h-full pointer-events-none z-0"
    />
  );
}
