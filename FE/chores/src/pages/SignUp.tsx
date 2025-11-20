import { useState, useContext, useEffect } from "react";
import { useForm } from "react-hook-form";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { PawPrint, Eye, EyeOff } from "lucide-react";
import { UserContext } from "@/context/UserContext";
import { Link, Navigate } from "react-router";
import { fetchURL } from "@/utils/fetch";

interface SignUpFormData {
  first_name: string;
  surename: string;
  email: string;
  password: string;
  confirm_password: string;
}

export default function SignUp() {
    const { token, setToken: setAccessToken, user } = useContext(UserContext);
    const [showPassword, setShowPassword] = useState(false);

    const {
        register,
        handleSubmit,
        watch,
        trigger,
        formState: { errors },
    } = useForm<SignUpFormData>();

    const password = watch("password", "");

    useEffect(() => {
        trigger("confirm_password");
    }, [password]);

    async function submitSignUp(data: SignUpFormData) {
        const formData = new FormData();
        formData.append("first_name", data.first_name);
        formData.append("surename", data.surename);
        formData.append("email", data.email);
        formData.append("password", data.password);

        const res = await fetch(fetchURL('/users'), {
            method: "POST",
            body: formData,
        });

        if (res.ok) {
            setAccessToken(!token);
            return;
        }

        switch (res.status) {
            case 500:
                alert("Server Error");
                break;
            case 400:
                alert("User Already Registered")
                break
            default:
                alert("Unknown Error");
        }
    }

    if (user) return <Navigate to="/home" replace />;

    return (
        <div className="w-screen h-screen bg-[#FFF8F2] flex items-center justify-center p-4 animate-in fade-in duration-500">
        <Card className="w-full max-w-md rounded-3xl shadow-xl border-none bg-white animate-in fade-in duration-500">
            <CardHeader className="text-center space-y-2">
            <div className="flex justify-center">
                <PawPrint className="w-12 h-12 text-[#E59D50]" />
            </div>
            <CardTitle className="text-3xl font-bold text-[#3A2F2F]">Create Account</CardTitle>
            <CardDescription className="text-[#6A5F5D]">
                Sign up to start managing your dog walks and happy pups.
            </CardDescription>
            </CardHeader>

            <CardContent className="space-y-5">
            <form onSubmit={handleSubmit(submitSignUp)} className="space-y-5">
                {/* First Name */}
                <div className="space-y-1">
                <Input
                    placeholder="First Name"
                    {...register("first_name", { required: "First name is required" })}
                    className="bg-[#FFF8F2] border-[#FFD7A8] focus:border-[#E59D50]"
                />
                {errors.first_name && <p className="text-red-600 text-sm">{errors.first_name.message}</p>}
                </div>

                {/* Surename */}
                <div className="space-y-1">
                <Input
                    placeholder="Surename"
                    {...register("surename", { required: "Surename is required" })}
                    className="bg-[#FFF8F2] border-[#FFD7A8] focus:border-[#E59D50]"
                />
                {errors.surename && <p className="text-red-600 text-sm">{errors.surename.message}</p>}
                </div>

                {/* Email */}
                <div className="space-y-1">
                <Input
                    placeholder="Email"
                    {...register("email", {
                    required: "Email is required",
                    pattern: { value: /^\S+@\S+$/i, message: "Invalid email address" },
                    })}
                    className="bg-[#FFF8F2] border-[#FFD7A8] focus:border-[#E59D50]"
                />
                {errors.email && <p className="text-red-600 text-sm">{errors.email.message}</p>}
                </div>

                {/* Password */}
                <div className="relative space-y-1">
                <Input
                    placeholder="Password"
                    type={showPassword ? "text" : "password"}
                    {...register("password", {
                    required: "Password is required",
                    minLength: { value: 6, message: "Minimum 6 characters" },
                    })}
                    className="bg-[#FFF8F2] border-[#FFD7A8] focus:border-[#E59D50] pr-11"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-800">
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
                {errors.password && <p className="text-red-600 text-sm">{errors.password.message}</p>}
                </div>

                {/* Confirm Password */}
                <div className="relative space-y-1">
                <Input
                    placeholder="Confirm Password"
                    type={showPassword ? "text" : "password"}
                    {...register("confirm_password", {
                    required: "Please confirm password",
                    validate: (value) => value === password || "Passwords do not match",
                    })}
                    className="bg-[#FFF8F2] border-[#FFD7A8] focus:border-[#E59D50] pr-11"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-800">
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
                {errors.confirm_password && <p className="text-red-600 text-sm">{errors.confirm_password.message}</p>}
                </div>

                {/* Submit */}
                <Button type="submit" className="w-full py-3 text-md font-semibold rounded-xl bg-[#FFB974] hover:bg-[#E59D50] text-[#3A2F2F] shadow-md">
                Sign Up
                </Button>
            </form>

            <p className="text-center text-sm text-[#6A5F5D]">
                Already have an account? <Link className="text-[#E59D50] font-medium" to={'/login'}>Login</Link>
            </p>
            </CardContent>
        </Card>
        </div>
    );
}