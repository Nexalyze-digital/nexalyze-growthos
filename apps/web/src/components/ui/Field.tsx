type FieldProps = {
  error?: string;
  id: string;
  label: string;
  onBlur?: () => void;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  type?: "email" | "password" | "text";
  value: string;
};

export function Field({
  error,
  id,
  label,
  onBlur,
  onChange,
  placeholder,
  required,
  type = "text",
  value,
}: FieldProps) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium text-slate-200" htmlFor={id}>
        {label}
      </label>
      <input
        aria-describedby={error ? `${id}-error` : undefined}
        aria-invalid={Boolean(error)}
        className="w-full rounded-lg border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-300/25"
        id={id}
        onBlur={onBlur}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        required={required}
        type={type}
        value={value}
      />
      {error ? (
        <p className="mt-2 text-sm text-red-300" id={`${id}-error`}>
          {error}
        </p>
      ) : null}
    </div>
  );
}
