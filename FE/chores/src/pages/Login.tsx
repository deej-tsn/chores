import { useContext, useState } from "react"
import { UserContext } from "../context/UserContext"
import { Link, Navigate } from "react-router"
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Eye, EyeOff, PawPrint } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Login(){

    const {token, setToken: setAccessToken, user} = useContext(UserContext)
    const [showPassword, setShowPassword] = useState(false);
    const [resError, setError] = useState("")
    
    async function submitLogin(event : React.FormEvent<HTMLFormElement>){
        event.preventDefault()
        const data = new FormData(event.target as HTMLFormElement)
        const res  = await fetch('https://local.app.com:8000/token', {
            method: 'POST',
            body: data,
            credentials: 'include'
        })
        if(res.ok){
            setAccessToken(!token)
            return
        }

        switch(res.status){
            case 400:
                setError('Incorrect Email or Password')
                break
            case 500:
                setError('Server Error')
                break
            default:
                setError('Unknown')
            
        }
    }

    if (user){
        return <Navigate to="/home" replace/>
    }

    return (
        <div className="w-screen h-screen bg-[#FFF8F2] flex items-center justify-center p-4 ">
            <Card className="w-full max-w-md rounded-3xl shadow-xl border-none bg-white animate-fade-up animate-duration-500 animate-ease-in-out">
                <CardHeader className="text-center space-y-2 animate-in fade-in duration-500">
                <div className="flex justify-center">
                    <PawPrint className="w-12 h-12 text-[#E59D50]" />
                </div>
                <CardTitle className="text-3xl font-bold text-[#3A2F2F]">Welcome Back</CardTitle>
                <CardDescription className="text-[#6A5F5D]">
                    Log in to see your scheduled walks and happy pups.
                </CardDescription>
                </CardHeader>

                <CardContent className="space-y-5 animate-in fade-in duration-500">
                <form onSubmit={submitLogin} className="space-y-5">
                    {/* Email */}
                    <div className="space-y-1">
                    <Input
                        id="email"
                        name="username"
                        type="email"
                        placeholder="Enter your email"
                        required
                        className={`bg-[#FFF8F2] border-[#FFD7A8] focus:border-[#E59D50] ${resError && "border-red-500"}`}
                    />
                    </div>

                    {/* Password */}
                    <div className="relative space-y-1">
                    <Input
                        id="password"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        required
                        className={`bg-[#FFF8F2] border-[#FFD7A8] focus:border-[#E59D50] pr-11 ${resError && "border-red-500"}`}
                    />
                    <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-800">
                        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                    </div>

                    {/* Error */}
                    {resError && (
                    <p className="text-red-600 text-sm text-center mt-1">{resError}</p>
                    )}

                    {/* Submit */}
                    <Button type="submit" className="w-full py-3 text-md font-semibold rounded-xl bg-[#FFB974] hover:bg-[#E59D50] text-[#3A2F2F] shadow-md">
                    Login
                    </Button>
                </form>

                <p className="text-center text-sm text-[#6A5F5D]">
                    Don’t have an account? <Link className="text-[#E59D50] font-medium" to={'/sign-up'}>Sign up</Link>
                </p>
                </CardContent>
            </Card>
        </div>
        );
}