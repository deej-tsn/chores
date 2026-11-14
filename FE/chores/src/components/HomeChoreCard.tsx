import type { HomeChoreApi } from "@/utils/homeChores";

interface HomeChoreCardProps {
  chore: HomeChoreApi;
  canClaim: boolean;
  pending: boolean;
  onToggleClaim: (chore: HomeChoreApi, claim: boolean) => void;
}

export default function HomeChoreCard({
  chore,
  canClaim,
  pending,
  onToggleClaim,
}: HomeChoreCardProps) {
  const claimed = chore.claimed_by.length > 0;

  return (
    <div
      className="w-full rounded-2xl p-4 flex flex-col gap-3 shadow-md border"
      style={{
        backgroundColor: claimed ? "#FFE8C4" : "#FFF8F2",
        borderColor: "#e5ddd5",
        color: "#3A2F2F",
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h2 className="text-base font-bold">{chore.chore}</h2>
          {chore.description && (
            <p className="text-sm text-[#6A5F5D]">{chore.description}</p>
          )}
        </div>

        {canClaim && (
          <button
            type="button"
            disabled={pending}
            onClick={() => onToggleClaim(chore, !chore.claimed_by_me)}
            className={`shrink-0 px-3 py-1 rounded-2xl text-sm font-bold shadow-sm transition-colors disabled:opacity-50 ${
              chore.claimed_by_me
                ? "bg-[#FFF8F2] text-[#3A2F2F] border border-[#E8D6C5] hover:bg-[#E8D6C5]"
                : "bg-[#FFB974] text-[#3A2F2F] hover:bg-[#E59D50] hover:text-[#FFF8F2]"
            }`}
          >
            {pending ? "…" : chore.claimed_by_me ? "Leave" : "Join"}
          </button>
        )}
      </div>

      <div className="flex flex-wrap gap-1">
        {chore.claimed_by.length === 0 ? (
          <span className="text-sm text-[#6A5F5D]">Unassigned</span>
        ) : (
          chore.claimed_by.map((name) => (
            <span
              key={name}
              className="text-xs font-semibold bg-[#FFD7A8] text-[#3A2F2F] rounded-full px-2 py-1"
            >
              {name}
            </span>
          ))
        )}
      </div>
    </div>
  );
}
