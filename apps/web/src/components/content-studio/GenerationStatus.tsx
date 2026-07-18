type GenerationStatusProps = {
  error: string;
  isLoading: boolean;
};

export function GenerationStatus({ error, isLoading }: GenerationStatusProps) {
  if (isLoading) {
    return (
      <div className="rounded-lg border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-100">
        Creating structured content with the local GrowthOS API...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-400/25 bg-red-500/10 px-4 py-3 text-sm text-red-100">
        {error}
      </div>
    );
  }

  return null;
}
