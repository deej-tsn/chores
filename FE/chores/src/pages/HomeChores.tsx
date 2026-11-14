import { useCallback, useContext, useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, Info } from "lucide-react";
import { UserContext } from "@/context/UserContext";
import { fetchURL } from "@/utils/fetch";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import HomeChoreCard from "@/components/HomeChoreCard";
import SummaryBox from "@/components/Summary";
import {
  addFortnights,
  convertPeriodResponse,
  countClaimants,
  formatISODate,
  getFortnightStart,
  periodLabel,
  type HomeChoreApi,
  type HomeChorePeriod,
  type HomeChorePeriodResponse,
} from "@/utils/homeChores";

function HomeChores() {
  const { user } = useContext(UserContext);
  const [period, setPeriod] = useState<HomeChorePeriod>({
    periodStart: getFortnightStart(),
    chores: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pendingId, setPendingId] = useState<number | null>(null);
  const [showSummary, setShowSummary] = useState(false);

  // Stable identity so the initial fetch runs exactly once on mount.
  const loadPeriod = useCallback(async (start?: Date) => {
    const requested = start ?? getFortnightStart();
    const url = fetchURL(`/chores/home?period=${formatISODate(requested)}`);

    setLoading(true);
    try {
      const res = await fetch(url, { method: "GET", credentials: "include" });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data: HomeChorePeriodResponse = await res.json();
      setPeriod(convertPeriodResponse(data));
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Could not load home chores");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadPeriod();
  }, [loadPeriod]);

  async function toggleClaim(chore: HomeChoreApi, claim: boolean) {
    setPendingId(chore.id);
    try {
      // PATCH returns the refreshed period, so no refetch is needed.
      const res = await fetch(fetchURL("/chores/home"), {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          assignmentID: chore.id,
          claimed: claim,
          period: formatISODate(period.periodStart),
        }),
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data: HomeChorePeriodResponse = await res.json();
      setPeriod(convertPeriodResponse(data));
    } catch (err) {
      console.error(err);
    } finally {
      setPendingId(null);
    }
  }

  if (!user) return null;

  const canClaim = ["admin", "user"].includes(user.role);
  const choresToClaim = period.chores.filter(
    (chore) => chore.claimed_by.length === 0,
  ).length;

  return (
    <div className="w-full flex flex-col items-center gap-6 animate-fade-up animate-duration-500 animate-ease-in-out">
      <div className="w-full max-w-4xl flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-bold text-[#3A2F2F]">
          Home chores
        </h1>
        <p className="text-[#6A5F5D] text-md md:text-lg">
          Every chore runs for a fortnight. Join the ones you're happy to take
          on.
        </p>
      </div>

      <Card className="w-full max-w-5xl bg-white rounded-3xl shadow-xl p-6 animate-fade-up animate-duration-500 animate-ease-in-out relative">
        <div className="flex flex-col md:flex-row justify-center mb-6 items-center gap-3 relative">
          <div className="flex flex-row items-center gap-3 bg-[#FFF8F2] px-4 py-2 rounded-full shadow-sm border border-[#E8D6C5]">
            <Button
              variant="ghost"
              className="rounded-full p-2 hover:bg-[#E8D6C5] transition"
              onClick={() =>
                loadPeriod(addFortnights(period.periodStart, -1))
              }
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>

            <h2 className="text-xl font-bold text-[#3A2F2F]">
              {periodLabel(period.periodStart)}
            </h2>

            <Button
              variant="ghost"
              className="rounded-full p-2 hover:bg-[#E8D6C5] transition"
              onClick={() => loadPeriod(addFortnights(period.periodStart, 1))}
            >
              <ArrowRight className="w-5 h-5" />
            </Button>
          </div>

          {!loading && !error && (
            <span
              className={`text-lg font-semibold ${choresToClaim > 0 ? "text-[#E59D50]" : "text-[#6A5F5D]"} md:absolute md:right-6`}
            >
              {choresToClaim > 0
                ? `Chores to claim: ${choresToClaim}`
                : "Fully claimed"}
            </span>
          )}

          <div
            className="relative cursor-pointer p-2 rounded-full hover:bg-[#39393912]"
            onClick={() => setShowSummary((prev) => !prev)}
          >
            <Info className="w-5 h-5" />
            {showSummary && (
              <SummaryBox counts={countClaimants(period.chores)} />
            )}
          </div>
        </div>

        {loading && (
          <div className="w-full flex justify-center font-bold">Loading…</div>
        )}
        {!loading && error && (
          <div className="w-full flex justify-center font-bold text-[#3A2F2F]">
            {error}
          </div>
        )}
        {!loading && !error && period.chores.length === 0 && (
          <div className="w-full flex justify-center font-bold">
            No home chores for this period
          </div>
        )}
        {!loading && !error && period.chores.length > 0 && (
          <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
            {period.chores.map((chore) => (
              <HomeChoreCard
                key={chore.id}
                chore={chore}
                canClaim={canClaim}
                pending={pendingId === chore.id}
                onToggleClaim={toggleClaim}
              />
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

export default HomeChores;
