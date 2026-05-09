import { onBeforeUnmount, onMounted } from "vue";

const DEFAULT_POINTS_COUNT = 54;
const DEFAULT_LINE_DISTANCE = 145;

function createPoint(width, height) {
    return {
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 1.8 + 0.8,
        speedX: (Math.random() - 0.5) * 0.35,
        speedY: (Math.random() - 0.5) * 0.35,
        opacity: Math.random() * 0.35 + 0.15,
    };
}

function drawPoint(context, point, color) {
    context.beginPath();
    context.arc(point.x, point.y, point.radius, 0, Math.PI * 2);
    context.fillStyle = color(point.opacity);
    context.fill();
}

function drawLine(context, firstPoint, secondPoint, distance, maxDistance, color) {
    const opacity = 1 - distance / maxDistance;

    context.beginPath();
    context.moveTo(firstPoint.x, firstPoint.y);
    context.lineTo(secondPoint.x, secondPoint.y);
    context.strokeStyle = color(opacity * 0.16);
    context.lineWidth = 1;
    context.stroke();
}

function updatePoint(point, width, height) {
    point.x += point.speedX;
    point.y += point.speedY;

    if (point.x <= 0 || point.x >= width) {
        point.speedX *= -1;
    }

    if (point.y <= 0 || point.y >= height) {
        point.speedY *= -1;
    }
}

export function useFloatingCanvas(canvasRef, options = {}) {
    const pointsCount = options.pointsCount || DEFAULT_POINTS_COUNT;
    const lineDistance = options.lineDistance || DEFAULT_LINE_DISTANCE;

    const pointColor = options.pointColor || ((opacity) => `rgba(74, 111, 165, ${opacity})`);
    const lineColor = options.lineColor || ((opacity) => `rgba(74, 111, 165, ${opacity})`);

    let animationFrameId = null;
    let context = null;
    let points = [];
    let width = 0;
    let height = 0;
    let dpr = 1;

    function resizeCanvas() {
        const canvas = canvasRef.value;

        if (!canvas) {
            return;
        }

        const rect = canvas.getBoundingClientRect();

        width = rect.width;
        height = rect.height;
        dpr = window.devicePixelRatio || 1;

        canvas.width = width * dpr;
        canvas.height = height * dpr;

        context = canvas.getContext("2d");
        context.setTransform(dpr, 0, 0, dpr, 0, 0);

        points = Array.from(
            {
                length: pointsCount,
            },
            () => createPoint(width, height),
        );
    }

    function renderConnections() {
        for (let i = 0; i < points.length; i += 1) {
            for (let j = i + 1; j < points.length; j += 1) {
                const dx = points[i].x - points[j].x;
                const dy = points[i].y - points[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < lineDistance) {
                    drawLine(context, points[i], points[j], distance, lineDistance, lineColor);
                }
            }
        }
    }

    function renderFrame() {
        if (!context) {
            return;
        }

        context.clearRect(0, 0, width, height);

        renderConnections();

        points.forEach((point) => {
            updatePoint(point, width, height);
            drawPoint(context, point, pointColor);
        });

        animationFrameId = window.requestAnimationFrame(renderFrame);
    }

    function startAnimation() {
        resizeCanvas();
        renderFrame();
    }

    function stopAnimation() {
        if (animationFrameId) {
            window.cancelAnimationFrame(animationFrameId);
        }
    }

    onMounted(() => {
        startAnimation();
        window.addEventListener("resize", resizeCanvas);
    });

    onBeforeUnmount(() => {
        stopAnimation();
        window.removeEventListener("resize", resizeCanvas);
    });
}