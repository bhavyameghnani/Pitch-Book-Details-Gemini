export default function Button({ children, onClick, type = "button", className = "", disabled }) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={
        "inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition " +
        "bg-sky-600 text-white hover:bg-sky-700 disabled:opacity-60 " +
        className
      }
    >
      {children}
    </button>
  );
}
