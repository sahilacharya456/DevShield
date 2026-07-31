"use client";

import { useEffect, useRef } from "react";

export function CyberSnakeOverlay() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext("2d"); 
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

    // --- Majestic Universe Cyber Snake Settings ---
    const mouse = { x: width / 2, y: height / 2, active: false };
    let time = 0;
    
    // Create an array of points for the snake body
    const snakeLength = 90; // Much longer and more majestic
    const linkDistance = 7; 
    const snake: {x: number, y: number}[] = [];
    for(let i = 0; i < snakeLength; i++) {
        snake.push({x: width / 2, y: height / 2});
    }

    // Particles for stardust trail
    const particles: {x: number, y: number, life: number, maxLife: number, vx: number, vy: number, color: string}[] = [];

    let lastMouseTime = Date.now();
    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
      lastMouseTime = Date.now();
    };
    window.addEventListener("mousemove", handleMouseMove);

    let slitherPhase = 0;

    // Main animation loop
    let animId: number;
    const draw = () => {
      time += 0.015;
      
      // Auto-swim in an infinity loop if mouse is idle for 2 seconds
      if (Date.now() - lastMouseTime > 2000) {
        mouse.active = false;
      }

      let targetX = mouse.x;
      let targetY = mouse.y;

      if (!mouse.active) {
        // Infinity loop parametric equation (Lemniscate of Bernoulli)
        const scale = Math.min(width, height) * 0.35;
        targetX = width / 2 + (scale * Math.cos(time)) / (1 + Math.sin(time) * Math.sin(time));
        targetY = height / 2 + (scale * Math.sin(time) * Math.cos(time)) / (1 + Math.sin(time) * Math.sin(time));
      }

      ctx.clearRect(0, 0, width, height);

      // --- Update Snake Physics ---
      const headDx = targetX - snake[0].x;
      const headDy = targetY - snake[0].y;
      const distToTarget = Math.sqrt(headDx * headDx + headDy * headDy);
      
      const moveAngle = Math.atan2(headDy, headDx);
      const moveSpeed = mouse.active ? Math.min(distToTarget * 0.1, 15) : 8;
      
      slitherPhase += moveSpeed * 0.04;
      const slitherAmplitude = Math.min(distToTarget * 0.05, 12);
      const slitherOffset = Math.sin(slitherPhase) * slitherAmplitude;
      
      const actualTargetX = targetX + Math.cos(moveAngle + Math.PI / 2) * slitherOffset;
      const actualTargetY = targetY + Math.sin(moveAngle + Math.PI / 2) * slitherOffset;
      
      snake[0].x += (actualTargetX - snake[0].x) * (mouse.active ? 0.15 : 0.08);
      snake[0].y += (actualTargetY - snake[0].y) * (mouse.active ? 0.15 : 0.08);

      for (let i = 1; i < snakeLength; i++) {
        const dx = snake[i-1].x - snake[i].x;
        const dy = snake[i-1].y - snake[i].y;
        const angle = Math.atan2(dy, dx);
        
        snake[i].x = snake[i-1].x - Math.cos(angle) * linkDistance;
        snake[i].y = snake[i-1].y - Math.sin(angle) * linkDistance;
      }

      // --- Stardust Particles ---
      if (Math.random() > 0.3) {
        particles.push({
          x: snake[0].x,
          y: snake[0].y,
          vx: (Math.random() - 0.5) * 2,
          vy: (Math.random() - 0.5) * 2,
          life: 0,
          maxLife: 50 + Math.random() * 50,
          color: Math.random() > 0.5 ? "#3b82f6" : "#c084fc"
        });
      }

      ctx.globalCompositeOperation = "screen";
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.life++;
        p.x += p.vx;
        p.y += p.vy;
        
        const opacity = 1 - (p.life / p.maxLife);
        if (opacity <= 0) {
          particles.splice(i, 1);
          continue;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, Math.random() * 2 + 0.5, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = opacity;
        ctx.fill();
      }
      ctx.globalAlpha = 1.0;
      ctx.globalCompositeOperation = "source-over";

      // --- Draw "Universe Link" Snake Body ---
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      
      for (let i = snakeLength - 1; i > 0; i--) {
        const ratio = Math.sin((i / snakeLength) * Math.PI);
        const thickness = Math.max(2, ratio * 28);
        const opacity = Math.max(0.1, 1 - (i / snakeLength));

        const r = Math.floor(59 + (i / snakeLength) * 100);
        const g = Math.floor(130 - (i / snakeLength) * 50);
        const b = Math.floor(246 + (i / snakeLength) * 9);

        ctx.beginPath();
        ctx.arc(snake[i].x, snake[i].y, thickness / 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${opacity * 0.8})`;
        ctx.shadowBlur = i < 20 ? 15 : 0;
        ctx.shadowColor = `rgb(${r}, ${g}, ${b})`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(snake[i].x, snake[i].y, thickness / 3.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(10, 15, 30, ${opacity})`;
        ctx.shadowBlur = 0;
        ctx.fill();
      }

      // --- Draw Snake Head ---
      const headX = snake[0].x;
      const headY = snake[0].y;
      
      const hDx = snake[0].x - snake[1].x;
      const hDy = snake[0].y - snake[1].y;
      const hAngle = Math.atan2(hDy, hDx);

      ctx.save();
      ctx.translate(headX, headY);
      ctx.rotate(hAngle);

      ctx.beginPath();
      ctx.moveTo(18, 0);
      ctx.lineTo(0, 12);
      ctx.lineTo(-8, 10);
      ctx.lineTo(-8, -10);
      ctx.lineTo(0, -12);
      ctx.closePath();
      ctx.fillStyle = "#ffffff";
      ctx.shadowBlur = 25;
      ctx.shadowColor = "#ec4899";
      ctx.fill();
      
      ctx.fillStyle = "#000000";
      ctx.shadowBlur = 0;
      ctx.beginPath();
      ctx.arc(5, 6, 2.5, 0, Math.PI * 2); 
      ctx.arc(5, -6, 2.5, 0, Math.PI * 2); 
      ctx.fill();

      ctx.restore();

      animId = requestAnimationFrame(draw);
    };

    animId = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      window.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <canvas 
      ref={canvasRef} 
      className="fixed top-0 left-0 w-full h-full pointer-events-none z-[3]"
    />
  );
}
