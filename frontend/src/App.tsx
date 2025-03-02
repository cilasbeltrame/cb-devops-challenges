import { Toaster } from "react-hot-toast";
import { Route, Routes, useLocation } from "react-router-dom";
import Hello from "./components/HelloComponent/Hello";

export function App() {
  const location = useLocation();

  return (
    <>
        <Routes location={location}>
          <Route path='/' element={<Hello />} />
        </Routes>
         
        <Toaster position="top-center" />
    </>
  )
}
