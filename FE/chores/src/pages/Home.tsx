import { useContext, useEffect, useState } from "react"
import { UserContext } from "../context/UserContext"
import { daysOfWeek, DefaultTimeTable } from "../utils/timetable"
import DayCell from "../components/DayCell"
import luka from "../assets/image.png"

function Home() {
  const {user} = useContext(UserContext)
  const [width, setWidth] = useState<number>(window.innerWidth);

  function handleWindowSizeChange() {
      setWidth(window.innerWidth);
  }
  
  useEffect(() => {
      window.addEventListener('resize', handleWindowSizeChange);
      return () => {
          window.removeEventListener('resize', handleWindowSizeChange);
      }
  }, []);

  const isMobile = width <= 768;

  if(!user) return

  let daysToAssign = 0
  for (let index = 0; index < daysOfWeek.length; index++) {
    if(DefaultTimeTable[daysOfWeek[index]].Morning == undefined) daysToAssign++
    if(DefaultTimeTable[daysOfWeek[index]].Evening == undefined) daysToAssign++
  }

  return (
    <>
    <img src={luka}/>
    <div className="w-11/12 h-fit bg-amber-500 p-5 rounded-4xl drop-shadow-2xl">
      <div className="w-full flex flex-row mb-2 font-bold text-2xl text-gray-50">
        <h1 className=" grow">{(new Date()).toLocaleDateString()}</h1>
        <h1>Days to Assign : {daysToAssign}</h1>
      </div>
      <div className="w-full h-11/12 md:h-64 grid grid-cols-2 grid-rows-7 md:grid-cols-7 md:grid-rows-2 gap-4">
         {!isMobile ?           
          <>
            {daysOfWeek.map((day) => <DayCell day={day} time="Morning" assigned={DefaultTimeTable[day].Morning} />)}
            {daysOfWeek.map((day) => <DayCell day={day} time="Evening" assigned={DefaultTimeTable[day].Morning} />)}
          </>
          :
          daysOfWeek.map(day => (
          <>
            <DayCell day={day} time="Morning" assigned={DefaultTimeTable[day].Morning} />
            <DayCell day={day} time="Evening" assigned={DefaultTimeTable[day].Evening} />
          </>
          ))
        }
      </div>
    </div>
    </>
  )
}

export default Home
