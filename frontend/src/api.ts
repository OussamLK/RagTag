export default class API{
    domain:string
    constructor(domain:string){
        this.domain = domain
    }

    private async post(url:string, payload:any){
        const resp = await fetch(this.domain+url, {
            method: 'POST',
            headers:{
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
            
        })
        return await resp.json()

    }

    async uploadFile(fileName:string, fileB64:string){
        return await this.post('/upload', {fileName, fileB64})
    }

    async query(query:string, backendFileId:string){
        return await this.post('query', {query, fileId:backendFileId})
    }
    
}