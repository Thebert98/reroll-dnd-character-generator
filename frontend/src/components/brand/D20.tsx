/** The Re:Roll d20 mark — the icon/favicon as a reusable component.
 *  Crisp SVG at any size; pass a `number` to render a face value other than 20. */
export function D20({
  size = 40,
  value = 20,
  className = "",
  withBackground = false,
}: {
  size?: number;
  value?: number | string;
  className?: string;
  withBackground?: boolean;
}) {
  const id = `rr-die-${Math.random().toString(36).slice(2, 8)}`;
  return (
    <svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={className}
      role="img"
      aria-label="Re:Roll d20"
    >
      <defs>
        <radialGradient id={id} cx="50%" cy="38%" r="75%">
          <stop offset="0%" stopColor="#9E2A2F" />
          <stop offset="55%" stopColor="#7A1F23" />
          <stop offset="100%" stopColor="#3E1012" />
        </radialGradient>
      </defs>
      {withBackground && <rect width="100" height="100" rx="22" fill="#1E1A17" />}
      <g transform="translate(0,2)">
        <path
          d="M50 6 L88 28 L88 70 L50 92 L12 70 L12 28 Z"
          fill={`url(#${id})`}
          stroke="#D8BA1F"
          strokeWidth={3}
          strokeLinejoin="round"
        />
        <g
          fill="none"
          stroke="#E6C36B"
          strokeWidth={1.6}
          strokeOpacity={0.75}
          strokeLinejoin="round"
        >
          <path d="M30 40 L70 40 L50 80 Z" />
          <path d="M50 6 L30 40 M50 6 L70 40" />
          <path d="M12 28 L30 40 M88 28 L70 40" />
          <path d="M12 70 L50 80 M88 70 L50 80" />
        </g>
        <text
          x={50}
          y={52}
          textAnchor="middle"
          fontFamily='"IM Fell English SC", Georgia, serif'
          fontWeight={700}
          fontSize={24}
          fill="#FFF3D6"
        >
          {value}
        </text>
      </g>
    </svg>
  );
}
