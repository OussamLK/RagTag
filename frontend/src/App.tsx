import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigation, useLocation, useNavigate } from 'react-router-dom';
import './App.css'
import API from './api'

const api = new API('/api');

const URLS = {results:'/resultats', search:'/recherche', upload:'/'}
function App(){

  return (
    <Router>
      <Container />
    </Router>
  )
}

function Container(){
  const [backendFileId, setBackendFileId] = useState<string | undefined>(undefined)
  const navigate = useNavigate()
  async function onFileUpload(fileName:string, fileB64:string){
    console.debug("sending...", fileB64)
    const {fileId} = await api.uploadFile(fileName, fileB64)
    setBackendFileId(fileId)
    navigate(URLS.search)
  }

  return (
    <div className="container">
      <div className="app">
        <h1 className='title'>DocRag</h1>
          <Routes>
            <Route path={URLS.upload} element={<Upload onFileUpload={onFileUpload} />} />
            <Route path={URLS.search} element={<Rag backendFileId={backendFileId} />} />
            <Route path={URLS.results} element={<Results />} />
          </Routes>
      </div>
    </div>
  )

}

function Upload({onFileUpload}:{onFileUpload:(fileName:string, fileB64:string)=>void}){
  function handleUpload(event:React.ChangeEvent<HTMLInputElement>){
    const file = event.target.files && event.target.files[0]
    if (file){
      const reader = new FileReader();
      reader.onload = function (e){
        if (!e.target) {
          console.debug("e.target null inside file reader")
          return
        }
        const b64Data = e.target.result;
        if (typeof b64Data !== 'string'){
          console.debug("b64Datan is not a string but is: ", b64Data)
          return
        }
        const fileName = file.name
        onFileUpload(fileName, b64Data.split(",")[1])
      }
      reader.readAsDataURL(file)
    }
  }
  return (
    <>
        <div className="upload">
          <label>Ajoutez un document &nbsp;
            <br />
            <input onChange={handleUpload} type='file'/>
          </label>
        </div>
    </>
  )

}


function Processing(){
  return <div>
      <p>File is being processed...</p>
    </div>
}

function Rag({backendFileId}:{backendFileId:string | undefined}){
  if (backendFileId === undefined)
    return <p>backendFileId is undefined</p>
  const navigate = useNavigate()
  const [query, setQuery] = useState("")

  async function sendQuery(){
    if (!backendFileId) throw("BackendFieldId is undefined")
      await api.query(query, backendFileId)
      navigate(URLS.results)
  }

  return <>
    <label>
      Que veux-tu savoir?
      <br/>
      <textarea value={query} onChange={e=>setQuery(e.currentTarget.value)} className='query-input' cols={55}/>
    </label>
    <br />
    <button onClick={sendQuery}>Chercher</button>
  
  </>

}

function Results(){
  const imagePath1 = '/src/assets/doc_page.png'
  const imagePath2 = '/src/assets/doc_page2.png'
  const imagePath3 = '/src/assets/doc_page3.png'
  const images = [[imagePath1, imagePath2], [imagePath3]]
  const [currentImages, setCurrentImages] = useState(0)
  function nextResult(){
    setCurrentImages(prev=>prev === 0 ? 1 : 0)
  }
  return <>
    <span className='result-nav-bar'>Résultats &nbsp; | &nbsp; <a onClick={nextResult} className='result-nav-button'>Suivant</a> &nbsp; | &nbsp; <a className='result-nav-button'>Précédent</a></span>
    {images[currentImages].map(path=><img key={path} className='result-page' src={path} />)}
  </>
}

export default App
