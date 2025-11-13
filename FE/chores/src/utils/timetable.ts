
type Day = {
  assignee : string | undefined
  id : number
}

type DayTime = {
  Morning: Day
  Evening: Day
}

export type TimeTableDict = {
  [day: string]: DayTime
}

export type TimetableDate = {
  weekStart : Date
  timetable : TimeTableDict
}

export const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

export const DefaultTimeTable: TimeTableDict = {
  Monday: { Morning: {assignee:undefined, id:-1}, Evening: {assignee:undefined, id:-1} },
  Tuesday: { Morning:{assignee:undefined, id:-1}, Evening: {assignee:undefined, id:-1} },
  Wednesday: { Morning: {assignee:undefined, id:-1}, Evening: {assignee:undefined, id:-1} },
  Thursday: { Morning: {assignee:undefined, id:-1}, Evening: {assignee:undefined, id:-1} },
  Friday: { Morning: {assignee:undefined, id:-1}, Evening: {assignee:undefined, id:-1}},
  Saturday: { Morning: {assignee:undefined, id:-1}, Evening: {assignee:undefined, id:-1} },
  Sunday: { Morning: {assignee:undefined, id:-1}, Evening: {assignee:undefined, id:-1} },
}

type DataTimeTable = {
  id: number
  time : "Morning" | "Evening"
  day : Date
  assigned : string | null
}

export function convertDataToTimeTableType(data : DataTimeTable[]){
  const timetable : TimeTableDict = {}

  dayNames.forEach(weekDay => {
    timetable[weekDay] = {Morning : {assignee:undefined, id:-1}, Evening : {assignee:undefined, id:-1}}
  })

  data.forEach((date) => {
    const weekday = dayNames[new Date(date.day).getDay()]
    timetable[weekday][date.time] = {assignee : date.assigned?? undefined, id:date.id}
  })
  return timetable
}