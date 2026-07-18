type SelectFieldProps<T extends string> = {
  id: string;
  label: string;
  onChange: (value: T) => void;
  options: readonly T[];
  value: T;
};

export function SelectField<T extends string>({
  id,
  label,
  onChange,
  options,
  value,
}: SelectFieldProps<T>) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium text-slate-200" htmlFor={id}>
        {label}
      </label>
      <select
        className="w-full rounded-lg border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300 focus:ring-2 focus:ring-cyan-300/25"
        id={id}
        onChange={(event) => onChange(event.target.value as T)}
        value={value}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}
