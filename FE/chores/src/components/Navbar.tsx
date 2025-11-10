
interface User {
    first_name : string,
    second_name : string,
    colour : string
}

interface NavbarProps { 
    user : User
}

const displayUserName = (user: User) => user.first_name.charAt(0) + user.second_name.charAt(0)

export default function Navbar({user} : NavbarProps){
    return (
        <nav className=" w-full h-5 bg-amber-800">
            <div>
                
            </div>
            <div id="userProfile" className="w-3 h-3 rounded-full flex items-center justify-center">
                {displayUserName(user)}
            </div>
        </nav>
    )
}