export default function Card({ title, children }) {
  return (
    <div className="bg-white shadow-sm rounded-lg p-4 border border-slate-100">
      {title && <h3 className="text-lg font-semibold mb-2">{title}</h3>}
      <div>{children}</div>
    </div>
  );
}
