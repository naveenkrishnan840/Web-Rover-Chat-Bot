import { BrowserRouter, Routes, Route } from "react-router";
import RoverPage from "./components/rover/queryPage";
import Home from "./components/rover/mainPage";

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home/>}/>
          <Route path="rover" element={<RoverPage/>}/>
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
