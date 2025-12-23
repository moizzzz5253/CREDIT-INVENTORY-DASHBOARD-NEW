import { useEffect, useState } from "react";

export default function Clock({ size = 260 }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const seconds = time.getSeconds();
  const minutes = time.getMinutes();
  const hours = time.getHours() % 12;

  const secondDeg = seconds * 6;
  const minuteDeg = minutes * 6 + seconds * 0.1;
  const hourDeg = hours * 30 + minutes * 0.5;

  const radius = size / 2;
  const numberRadius = radius * 0.8;

  return (
    <div className="flex flex-col items-center gap-3">
      {/* Clock face */}
      <div
        className="relative rounded-full border-4 border-zinc-500 bg-zinc-900"
        style={{ width: size, height: size }}
      >
        {/* Numbers */}
        {[...Array(12)].map((_, i) => {
          const angle = (i + 1) * 30 - 90;
          const x =
            radius + numberRadius * Math.cos((angle * Math.PI) / 180);
          const y =
            radius + numberRadius * Math.sin((angle * Math.PI) / 180);

          return (
            <div
              key={i}
              className="absolute text-white font-semibold"
              style={{
                left: x,
                top: y,
                transform: "translate(-50%, -50%)",
              }}
            >
              {i + 1}
            </div>
          );
        })}

        {/* Hour hand */}
        <div
          className="absolute bg-white rounded"
          style={{
            width: 6,
            height: radius * 0.45,
            left: "50%",
            bottom: "50%",
            transform: `translateX(-50%) rotate(${hourDeg}deg)`,
            transformOrigin: "50% 100%",
          }}
        />

        {/* Minute hand */}
        <div
          className="absolute bg-white rounded"
          style={{
            width: 4,
            height: radius * 0.65,
            left: "50%",
            bottom: "50%",
            transform: `translateX(-50%) rotate(${minuteDeg}deg)`,
            transformOrigin: "50% 100%",
          }}
        />

        {/* Second hand */}
        <div
          className="absolute bg-red-500 rounded"
          style={{
            width: 2,
            height: radius * 0.75,
            left: "50%",
            bottom: "50%",
            transform: `translateX(-50%) rotate(${secondDeg}deg)`,
            transformOrigin: "50% 100%",
          }}
        />

        {/* Center dot */}
        <div className="absolute w-3 h-3 bg-white rounded-full left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2" />
      </div>

      {/* Date */}
      <div className="text-lg text-zinc-400">
        {time.toLocaleDateString(undefined, {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
        })}
      </div>
    </div>
  );
}
