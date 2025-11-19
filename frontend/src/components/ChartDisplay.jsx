import React from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale,
    Filler
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale,
    Filler
);

const ChartDisplay = ({ data }) => {
    if (!data || data.length === 0) return null;

    // Determine trend for color
    const startValue = data[0].y;
    const endValue = data[data.length - 1].y;
    const isPositive = endValue >= startValue;

    const color = isPositive ? '#00ff9d' : '#ff4d4d';

    const chartData = {
        datasets: [
            {
                label: 'Cookies',
                data: data,
                borderColor: color,
                borderWidth: 2,
                backgroundColor: (context) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                    if (isPositive) {
                        gradient.addColorStop(0, 'rgba(0, 255, 157, 0.2)');
                        gradient.addColorStop(1, 'rgba(0, 255, 157, 0)');
                    } else {
                        gradient.addColorStop(0, 'rgba(255, 77, 77, 0.2)');
                        gradient.addColorStop(1, 'rgba(255, 77, 77, 0)');
                    }
                    return gradient;
                },
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: color,
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 2,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                enabled: false
            },
        },
        scales: {
            x: {
                type: 'time',
                display: false,
                grid: { display: false }
            },
            y: {
                display: false,
                grid: { display: false }
            },
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }
    };

    return (
        <div style={{ height: '250px', width: '100%', position: 'relative' }}>
            <Line data={chartData} options={options} />
            {/* Glowing effect behind the chart */}
            <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '80%',
                height: '80%',
                background: isPositive
                    ? 'radial-gradient(circle, rgba(0, 255, 157, 0.05) 0%, transparent 70%)'
                    : 'radial-gradient(circle, rgba(255, 77, 77, 0.05) 0%, transparent 70%)',
                pointerEvents: 'none',
                zIndex: -1
            }} />
        </div>
    );
};

export default ChartDisplay;
