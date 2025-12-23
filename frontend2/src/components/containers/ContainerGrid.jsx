import ContainerCard from "./ContainerCard";

export default function ContainerGrid({ containers }) {
  if (!containers.length) {
    return (
      <p className="text-zinc-400 text-center mt-10">
        No containers found
      </p>
    );
  }

  return (
    <div
      className="
        grid
        grid-cols-2
        sm:grid-cols-3
        md:grid-cols-4
        lg:grid-cols-5
        gap-6
      "
    >
      {containers.map((c) => (
        <ContainerCard key={c.id} container={c} />
      ))}
    </div>
  );
}
