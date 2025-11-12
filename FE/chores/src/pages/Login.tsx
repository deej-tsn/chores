import { useContext } from "react"
import { UserContext } from "../context/UserContext"
import type { Token } from "../types/user"
import { Navigate } from "react-router"

export default function Login(){

    const {setToken: setAccessToken, user} = useContext(UserContext)

    function submitLogin(event : React.FormEvent<HTMLFormElement>){
        event.preventDefault()
        const data = new FormData(event.target as HTMLFormElement)
        fetch('http://127.0.0.1:8000/token', {
            method: 'POST',
            body: data
        }).then(
            (res) => res.json()).then(
            (data : Token ) => setAccessToken(data)).catch(
            (error) => console.error(error)
        )
    }

    if (user){
        return <Navigate to="/home" replace/>
    }

    return (
        <div className=' w-screen h-screen bg-amber-50 flex items-center justify-center p-1'>
            <form onSubmit={submitLogin} className="w-full h-96 md:w-1/2 lg:w-1/3 md:h-96 rounded-2xl drop-shadow-2xl bg-amber-500 p-5 flex items-center flex-col justify-evenly">
                <h1 className=" text-5xl font-bold text-amber-50">Login</h1>
                <input className="bg-amber-50 p-2 rounded-2xl w-1/2 transition-colors hover:bg-gray-200" id="email" name="username" type="email" required placeholder="Email"/>
                <input className="bg-amber-50 p-2 rounded-2xl w-1/2 transition-colors hover:bg-gray-200" id="password" name="password" required type="password" placeholder="Password"/>
                <button className="bg-amber-700 p-2 rounded-2xl w-1/2 cursor-pointer hover:bg-amber-800 transition-colors  text-2xl text-amber-50 font-bold" type="submit">Login</button>
            </form>
        </div>
    )
}