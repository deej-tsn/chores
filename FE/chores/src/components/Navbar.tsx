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
        <nav className="w-11/12 h-16 p-2 max-w-full rounded-3xl shadow-lg fixed top-5 bg-[#E59D50] flex z-20">
            <div className="h-full flex items-center grow gap-4">
                <NavLink path="/home" label="Home" />
                <NavLink path="/settings" label="Settings" />
            </div>
            <div
                id="userProfile"
                className="h-full aspect-square rounded-full flex items-center justify-center bg-[#FFB974] cursor-pointer transition-colors hover:bg-[#E59D50] font-bold text-[#FFF8F2]"
            >
                {displayUserName(user)}
            </div>
        </nav>
    )
}