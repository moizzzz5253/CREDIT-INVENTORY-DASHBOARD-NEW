import Button from "../ui/Button";

export default function ContainerHeader({
  onInit,
  onRegenerate,
  hasContainers,
}) {
  return (
    <div className="flex items-center justify-between mb-6">
      <h2 className="text-xl font-semibold">Containers</h2>

      <div className="flex gap-3">
        {!hasContainers && (
          <Button onClick={onInit} variant="primary">
            Initialize Containers
          </Button>
        )}

        <Button onClick={onRegenerate} variant="secondary">
          Regenerate QR Codes
        </Button>

        <Button
          variant="secondary"
          onClick={() => window.open("/containers/print", "_blank")}
        >
          Print QR Codes
        </Button>
      </div>
    </div>
  );
}
