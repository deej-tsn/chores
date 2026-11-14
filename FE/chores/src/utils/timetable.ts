export type Day = {
  assignee: string | undefined;
  id: number;
};

export type DayTime = {
  Morning: Day;
  Evening: Day;
};

const DAYS_IN_MS = 1000 * 60 * 60 * 24

export type TimeTableDict = {
  [day: string]: DayTime;
};

export type TimetableData = {
  weekStart: Date;
  timetable: TimeTableDict;
};

export const daysOfWeek = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];
const dayNames = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];

export const DefaultTimeTable: TimeTableDict = {
  Monday: {
    Morning: { assignee: undefined, id: -1 },
    Evening: { assignee: undefined, id: -1 },
  },
  Tuesday: {
    Morning: { assignee: undefined, id: -1 },
    Evening: { assignee: undefined, id: -1 },
  },
  Wednesday: {
    Morning: { assignee: undefined, id: -1 },
    Evening: { assignee: undefined, id: -1 },
  },
  Thursday: {
    Morning: { assignee: undefined, id: -1 },
    Evening: { assignee: undefined, id: -1 },
  },
  Friday: {
    Morning: { assignee: undefined, id: -1 },
    Evening: { assignee: undefined, id: -1 },
  },
  Saturday: {
    Morning: { assignee: undefined, id: -1 },
    Evening: { assignee: undefined, id: -1 },
  },
  Sunday: {
    Morning: { assignee: undefined, id: -1 },
    Evening: { assignee: undefined, id: -1 },
  },
};

/** One row as returned by `GET /timetable` (date fields are ISO strings). */
export type TimetableApiDay = {
  id: number;
  time: "Morning" | "Evening";
  day: string;
  assigned: string | null;
};

/** Payload of `GET /timetable` and `PATCH /timetable`. */
export type TimetableResponse = {
  weekStart: string;
  timetable: TimetableApiDay[];
};

export function convertDataToTimeTableType(
  data: TimetableResponse,
): TimetableData {
  const timetable: TimeTableDict = {};

  dayNames.forEach((weekDay) => {
    timetable[weekDay] = {
      Morning: { assignee: undefined, id: -1 },
      Evening: { assignee: undefined, id: -1 },
    };
  });

  data.timetable.forEach((date) => {
    const weekday = dayNames[new Date(date.day).getDay()];
    timetable[weekday][date.time] = {
      assignee: date.assigned ?? undefined,
      id: date.id,
    };
  });

  const weekStart = new Date(data.weekStart);
  return { weekStart: weekStart, timetable: timetable };
}

/** Per-person slot counts for the summary popover; empty slots count as unassigned. */
export function countAssignees(
  timetable: TimeTableDict,
): Record<string, number> {
  return Object.values(timetable).reduce<Record<string, number>>(
    (counts, day) => {
      [day.Morning, day.Evening].forEach((shift) => {
        const name = shift.assignee ?? "Unassigned";
        counts[name] = (counts[name] ?? 0) + 1;
      });
      return counts;
    },
    {},
  );
}

export function getMonday() {
  const d = new Date();
  const day = d.getDay(),
    diff = d.getDate() - day + (day == 0 ? -6 : 1);
  return new Date(d.setDate(diff));
}

export function formatDate(date : Date) : string{
  return date.toISOString().split("T")[0]
}

export function diffInDates(a : Date, b : Date) : number {
  const diff = a.getTime() - b.getTime()
  return diff / DAYS_IN_MS
}