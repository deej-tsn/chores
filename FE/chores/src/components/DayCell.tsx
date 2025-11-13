import { useContext } from "react"
import { editPanelContext } from "../context/EditContext"
import { UserContext } from "../context/UserContext"

interface DayCellProps {
    day : string
    time : "Morning"|"Evening"
    assigned : string | undefined
    id : number
}


export default function DayCell({day, time, assigned, id} : DayCellProps){
    const assigned_class = "bg-amber-800"
    const unassigned_class = "bg-amber-600 transition-colors hover:bg-amber-700"

    const {setEditPanelState} = useContext(editPanelContext)
    const {user} = useContext(UserContext)

    function editDay(){
        if(!assigned || user?.first_name === assigned) setEditPanelState(id)
    }
    
    return (
        <div onClick={() => editDay()} className={`w-full h-full rounded-4xl p-2 flex items-center justify-center flex-col font-bold text-gray-100 cursor-pointer ${assigned? assigned_class : unassigned_class}`}>
            <h1>{`${day} - ${time}`}</h1>

            <h2>{assigned ?? 'Unassigned'}</h2>
        </div>
    )
}