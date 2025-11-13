import NavLink from "./NavLink"

interface User {
    first_name : string,
    second_name : string,
    colour : string
}

interface NavbarProps { 
    user : User
}

const displayUserName = (user: User) => (user.first_name.charAt(0) + user.second_name.charAt(0)).toUpperCase()

export default function Navbar({user} : NavbarProps){
    return (
        <nav className=" w-11/12 p-2 max-w-full rounded-4xl drop-shadow-2xl box-content h-12 fixed top-5 bg-amber-500 flex">
            <div className="h-full flex items-center grow">
                <NavLink path="/home" label="Home"/>
                <NavLink path="/settings" label="Settings"/>
            </div>
            <div id="userProfile" className="h-full aspect-square rounded-full flex items-center justify-center bg-amber-600 cursor-pointer transition-colors hover:bg-amber-700 font-bold text-gray-100">
                {displayUserName(user)}
            </div>
        </nav>
    )
}