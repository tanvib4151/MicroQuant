export default function ChannelSelector({
  channels,
  value,
  onChange,
}: {
  channels: string[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label>
      Intensity channel
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {channels.map((c) => (
          <option key={c} value={c}>
            {c === "gray" ? "Grayscale — single intensity plane" : c}
          </option>
        ))}
      </select>
    </label>
  );
}
