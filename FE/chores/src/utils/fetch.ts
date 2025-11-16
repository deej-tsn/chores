export async function fetchWithRedirect(url : string, opts? : any){
    const res = await fetch(url, opts)

    if(!res.ok){
        if (res.status == 500) {
            console.error("Server Error")
        }
    }
}