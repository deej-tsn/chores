type DayTime = {
  Morning: string | undefined
  Evening: string | undefined
}

type TimeTableDict = {
  [day: string]: DayTime
}

export const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

export const DefaultTimeTable: TimeTableDict = {
  Monday: { Morning: undefined, Evening: undefined },
  Tuesday: { Morning: undefined, Evening: undefined },
  Wednesday: { Morning: undefined, Evening: undefined },
  Thursday: { Morning: undefined, Evening: undefined },
  Friday: { Morning: undefined, Evening: undefined },
  Saturday: { Morning: undefined, Evening: undefined },
  Sunday: { Morning: undefined, Evening: undefined },
}