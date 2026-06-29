function Card({ title, description, children, className = '', footer }) {
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}
    >
      {(title || description) && (
        <div className="border-b border-slate-100 px-6 py-4">
          {title && <h3 className="text-base font-semibold text-slate-900">{title}</h3>}
          {description && (
            <p className="mt-1 text-sm text-slate-500">{description}</p>
          )}
        </div>
      )}

      <div className="px-6 py-4">{children}</div>

      {footer && (
        <div className="border-t border-slate-100 px-6 py-4">{footer}</div>
      )}
    </div>
  );
}

export default Card;
