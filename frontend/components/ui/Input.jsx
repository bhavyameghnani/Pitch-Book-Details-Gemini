export default function Input({ value, onChange, placeholder, type = "text", className = "" }) {
  return (
    <input
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      type={type}
      className={
        "w-full px-3 py-2 rounded-md border border-slate-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-300 " +
        className
      }
    />
  );
}
