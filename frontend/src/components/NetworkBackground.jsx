import { useEffect, useRef } from "react";

const NetworkBackground = ({ isDarkMode }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let particles = [];

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    const particleCount = 60;
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.8,
            vy: (Math.random() - 0.5) * 0.8,
            radius: Math.random() * 1.5 + 1
        });
    }

    const drawLine = (p1, p2, distance) => {
        const opacity = 1 - (distance / 120);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = isDarkMode 
            ? `rgba(20, 210, 150, ${opacity * 0.12})`
            : `rgba(15, 110, 86, ${opacity * 0.08})`;
        ctx.lineWidth = 1;
        ctx.stroke();
    };

    const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = isDarkMode ? 'rgba(20, 210, 150, 0.45)' : 'rgba(15, 110, 86, 0.35)';

        for (let i = 0; i < particles.length; i++) {
            let p = particles[i];
            
            if (!prefersReducedMotion) {
                p.x += p.vx * 0.5;
                p.y += p.vy * 0.5;

                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;
            }

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();

            for (let j = i + 1; j < particles.length; j++) {
                let p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 120) {
                    drawLine(p, p2, distance);
                }
            }
        }

        if (!prefersReducedMotion) {
            animationFrameId = requestAnimationFrame(animate);
        }
    };

    animate();

    return () => {
        window.removeEventListener('resize', resize);
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [isDarkMode]);

  return (
    <canvas 
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full pointer-events-none z-0"
    />
  );
};

export default NetworkBackground;
