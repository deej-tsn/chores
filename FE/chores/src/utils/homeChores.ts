import { addDays, parseISODate } from "@/utils/dates";

/** One chore instance as returned by `GET /chores/home`. */
export type HomeChoreApi = {
  id: number;
  chore: string;
  description: string;
  claimed_by: string[];
  claimed_by_me: boolean;
};

/** Payload of `GET /chores/home` and `PATCH /chores/home`. */
export type HomeChorePeriodResponse = {
  periodStart: string;
  chores: HomeChoreApi[];
};

export type HomeChorePeriod = {
  periodStart: Date;
  chores: HomeChoreApi[];
};

/** Must match `FORTNIGHT_ANCHOR` in the backend (`2025-12-08`, a Monday). */
export const FORTNIGHT_ANCHOR = "2025-12-08";
const FORTNIGHT_DAYS = 14;
const MS_PER_DAY = 24 * 60 * 60 * 1000;

export function addFortnights(date: Date, count: number): Date {
  return addDays(date, count * FORTNIGHT_DAYS);
}

/** Mirror of the backend's anchoring: the Monday that starts the date's fortnight. */
export function getFortnightStart(date: Date = new Date()): Date {
  const anchor = parseISODate(FORTNIGHT_ANCHOR);
  // Whole-day difference via UTC so a DST boundary cannot produce a fraction.
  const elapsedDays = Math.round(
    (Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) -
      Date.UTC(anchor.getFullYear(), anchor.getMonth(), anchor.getDate())) /
      MS_PER_DAY,
  );
  return addDays(anchor, Math.floor(elapsedDays / FORTNIGHT_DAYS) * FORTNIGHT_DAYS);
}

export function convertPeriodResponse(
  data: HomeChorePeriodResponse,
): HomeChorePeriod {
  return { periodStart: parseISODate(data.periodStart), chores: data.chores };
}

export function periodLabel(periodStart: Date): string {
  const periodEnd = addDays(periodStart, FORTNIGHT_DAYS - 1);
  const options: Intl.DateTimeFormatOptions = { day: "numeric", month: "short" };
  return `${periodStart.toLocaleDateString(undefined, options)} – ${periodEnd.toLocaleDateString(undefined, options)}`;
}

/** Per-person counts for the summary popover; chores with no owners count as unassigned. */
export function countClaimants(
  chores: HomeChoreApi[],
): Record<string, number> {
  return chores.reduce<Record<string, number>>((counts, chore) => {
    if (chore.claimed_by.length === 0) {
      counts.Unassigned = (counts.Unassigned ?? 0) + 1;
      return counts;
    }
    chore.claimed_by.forEach((name) => {
      counts[name] = (counts[name] ?? 0) + 1;
    });
    return counts;
  }, {});
}
