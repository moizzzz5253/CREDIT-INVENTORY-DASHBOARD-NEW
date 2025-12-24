export default function Modal({ open, title, children, onClose }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" aria-hidden={!open}>
      <div className="absolute inset-0 bg-black opacity-50" onClick={onClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="relative bg-zinc-900 border border-zinc-700 rounded-lg p-4 max-w-lg w-full z-10 shadow-lg"
      >
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <button type="button" aria-label="Close" className="text-zinc-400" onClick={onClose}>✕</button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
}