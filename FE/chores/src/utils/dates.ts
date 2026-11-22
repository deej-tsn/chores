/**
 * Calendar-safe date helpers.
 *
 * `new Date("YYYY-MM-DD")` parses as UTC and `toISOString()` converts back to
 * UTC, so both can slip a day either side of midnight. These helpers stay in
 * local time, and `addDays` uses calendar arithmetic on a copy so a DST
 * boundary cannot shift a date.
 */

export function parseISODate(value: string): Date {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

export function formatISODate(date: Date): string {
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}

export function addDays(date: Date, days: number): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days);
}
