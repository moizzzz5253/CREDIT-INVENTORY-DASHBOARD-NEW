import ContainerCard from "./ContainerCard";

export default function ContainerGrid({ containers }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      {containers.map((container) => (
        <ContainerCard
          key={container.id}
          container={container}
        />
      ))}
    </div>
  );
}
