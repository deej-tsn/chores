interface DayCellProps {
    day : string
    time : "Morning"|"Evening"
    assigned : string | undefined
}


export default function DayCell({day, time, assigned} : DayCellProps){

    return (
        <div className="w-full h-full bg-amber-600 rounded-4xl p-2 flex items-center justify-center flex-col font-bold text-gray-100 transition-colors hover:bg-amber-700 cursor-pointer">
            <h1>{`${day} - ${time}`}</h1>

            <h2>{assigned ?? 'Unassigned'}</h2>
        </div>
    )
}