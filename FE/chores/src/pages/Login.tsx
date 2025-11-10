export default function Login(){

    function submitLogin(event : React.FormEvent<HTMLFormElement>){
        event.preventDefault()
        const data = new FormData(event.target as HTMLFormElement)
        console.log(Object.fromEntries(data))
        fetch('http:127.0.0.1:8000/login', {
            method: 'POST',
            body: data
        }).then((res) => console.log(res))
    }

    return (
        <div className=' w-screen h-screen bg-amber-700 flex items-center justify-center p-1'>
            <form onSubmit={submitLogin}className="w-full h-96 md:w-1/2 lg:w-1/3 md:h-96 rounded-2xl drop-shadow-2xl bg-amber-600 p-5 flex items-center flex-col justify-evenly">
                <h1 className=" text-5xl">Login</h1>
                <input className="bg-amber-500 p-2 rounded-2xl w-1/2" id="email" name="email" type="email" required placeholder="Email"/>
                <input className="bg-amber-500 p-2 rounded-2xl w-1/2" id="password" name="password" required type="password" placeholder="Password"/>
                <button className="bg-amber-700 p-2 rounded-2xl w-1/2 cursor-pointer hover:bg-amber-800 transition-colors" type="submit">Login</button>
            </form>
        </div>
    )
}