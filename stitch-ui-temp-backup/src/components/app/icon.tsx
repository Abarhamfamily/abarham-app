// Material Symbols Rounded icon wrapper.
// Renders an RTL-safe ligature icon using the font loaded in __root.tsx.
type IconProps = {
  name: string;
  className?: string;
  filled?: boolean;
  size?: number;
};

export function Icon({ name, className = "", filled = false, size = 24 }: IconProps) {
  return (
    <span
      className={`material-symbols-rounded select-none ${className}`}
      style={{
        fontSize: `${size}px`,
        fontVariationSettings: `'FILL' ${filled ? 1 : 0}, 'wght' 400, 'GRAD' 0, 'opsz' ${size}`,
      }}
      aria-hidden="true"
    >
      {name}
    </span>
  );
}
