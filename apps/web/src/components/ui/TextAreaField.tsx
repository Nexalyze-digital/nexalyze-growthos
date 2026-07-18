type TextAreaFieldProps = {
  id: string;
  label: string;
  maxLength?: number;
  onChange: (value: string) => void;
  placeholder?: string;
  value: string;
};

export function TextAreaField({
  id,
  label,
  maxLength,
  onChange,
  placeholder,
  value,
}: TextAreaFieldProps) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3">
        <label className="block text-sm font-medium text-slate-200" htmlFor={id}>
          {label}
        </label>
        {maxLength ? (
          <span className="text-xs text-slate-500">
            {value.length}/{maxLength}
          </span>
        ) : null}
      </div>
      <textarea
        className="min-h-32 w-full resize-y rounded-lg border border-white/10 bg-slate-950 px-4 py-3 text-sm leading-6 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-300/25"
        id={id}
        maxLength={maxLength}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        value={value}
      />
    </div>
  );
}
