import ComponentCard from "./ComponentCard";

export default function ComponentGrid({ components }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      {components.map((c) => (
        <ComponentCard key={c.id} component={c} />
      ))}
    </div>
  );
}
