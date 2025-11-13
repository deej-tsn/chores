import { useContext, useEffect, useState } from "react"
import { UserContext } from "../context/UserContext"
import { convertDataToTimeTableType, daysOfWeek, DefaultTimeTable, type TimeTableDict } from "../utils/timetable"
import DayCell from "../components/DayCell"
import luka from "../assets/image.png"
import EditPanel from "../components/EditPanel"

function Home() {
  const {user} = useContext(UserContext)
  const [width, setWidth] = useState<number>(window.innerWidth);
  const [timetable, setTimetable] = useState<TimeTableDict>(DefaultTimeTable)

  function handleWindowSizeChange() {
      setWidth(window.innerWidth);
  }
  
  useEffect(() => {
      window.addEventListener('resize', handleWindowSizeChange);
      return () => {
          window.removeEventListener('resize', handleWindowSizeChange);
      }
  }, []);

  useEffect(() => {
    async function getTimetable() {
      fetch('https://local.app.com:8000/timetable', {
      method : 'GET',
      credentials : 'include'
      }).then((res) => res.json()).then((data) => {
        const timetable = convertDataToTimeTableType(data);
        setTimetable(timetable)
    }).catch((error) => console.log(error))
    }

    getTimetable()
  }, [])

  const isMobile = width <= 768;

  if(!user) return

  let daysToAssign = 0
  for (let index = 0; index < daysOfWeek.length; index++) {
    if(timetable[daysOfWeek[index]].Morning.assignee == undefined) daysToAssign++
    if(timetable[daysOfWeek[index]].Evening.assignee == undefined) daysToAssign++
  }

  return (
    <>
    <img src={luka}/>
    <div className="w-11/12 h-fit bg-amber-500 p-5 rounded-4xl drop-shadow-2xl">
      <div className="w-full flex flex-row mb-2 font-bold text-2xl text-gray-50">
        <h1 className=" grow">Week: {(new Date()).toLocaleDateString()}</h1>
        {daysToAssign > 0 ?
          <h1>Days to Assign : {daysToAssign}</h1>
          :
          <h1>Fully Allocated</h1>
        
        }
        
      </div>
      <div className="w-full h-11/12 md:h-64 grid grid-cols-2 grid-rows-7 md:grid-cols-7 md:grid-rows-2 gap-4">
         {!isMobile ?           
          <>
            {daysOfWeek.map(
              (day) => <DayCell key={`${day} - Morning`} 
                day={day}
                time="Morning"
                assigned={timetable[day].Morning.assignee}
                id={timetable[day].Morning.id}
            />)}
            {daysOfWeek.map(
              (day) => <DayCell key={`${day} - Evening`}
                day={day}
                time="Evening"
                assigned={timetable[day].Evening.assignee}
                id={timetable[day].Evening.id}
            />)}
          </>
          :
          daysOfWeek.map(day => (
          <>
            <DayCell key={`${day} - Morning`} 
                day={day}
                time="Morning"
                assigned={timetable[day].Morning.assignee}
                id={timetable[day].Morning.id}
            />
           <DayCell key={`${day} - Evening`}
                day={day}
                time="Evening"
                assigned={timetable[day].Evening.assignee}
                id={timetable[day].Evening.id}
            />
          </> 
          ))
        }
      </div>
    </div>
    <EditPanel setTimetable={setTimetable}/>
    </>
  )
}

export default Home
