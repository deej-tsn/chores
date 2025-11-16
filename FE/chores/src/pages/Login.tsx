import { useContext, useState } from "react"
import { UserContext } from "../context/UserContext"
import { Navigate } from "react-router"
import { Button, FilledInput, FormControl, FormHelperText, IconButton, InputAdornment, InputLabel, OutlinedInput, TextField, Typography } from "@mui/material"
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';

export default function Login(){

    const {setToken: setAccessToken, user} = useContext(UserContext)
    const [showPassword, setShowPassword] = useState(false);
    const [resError, setError] = useState("")

    const handleClickShowPassword = () => setShowPassword((show) => !show);

    const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
    };

    const handleMouseUpPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
    };

    async function submitLogin(event : React.FormEvent<HTMLFormElement>){
        event.preventDefault()
        const data = new FormData(event.target as HTMLFormElement)
        const res  = await fetch('https://local.app.com:8000/token', {
            method: 'POST',
            body: data,
            credentials: 'include'
        })
        if(res.ok){
            setAccessToken(true)
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
        <div className=' w-screen h-screen bg-gray-100 flex items-center justify-center p-1'>
            <form onSubmit={submitLogin} className="w-full h-96 md:w-lg md:h-96 rounded-2xl drop-shadow-2xl bg-gray-50 p-5 flex items-center flex-col justify-evenly">
                <Typography variant='h2'>Login</Typography>
                <TextField className="w-1/2" variant="outlined" label="Email" id="email" name="username" type="email" error={!!resError} helperText={resError} required/>
                <FormControl className=" w-1/2" variant="outlined">
                    <InputLabel htmlFor="filled-adornment-password">Password</InputLabel>
                    <OutlinedInput
                        id="outlined-adornment-password"
                        type={showPassword ? 'text' : 'password'}
                        name="password"
                        error={!!resError}
                        required
                        endAdornment={
                        <InputAdornment position="end">
                            <IconButton
                            aria-label={
                                showPassword ? 'hide the password' : 'display the password'
                            }
                            onClick={handleClickShowPassword}
                            onMouseDown={handleMouseDownPassword}
                            onMouseUp={handleMouseUpPassword}
                            edge="end"
                            >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                        </InputAdornment>
                        }
                        label="Password"
                    />
                    {!!resError && <FormHelperText id="outlined-helper-text" variant='outlined' error>{resError}</FormHelperText>}
                </FormControl>
                <Button type="submit" className="w-1/2 p-2" variant='contained'>Login</Button>
            </form>
        </div>
    )
}