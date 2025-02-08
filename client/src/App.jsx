import { Route, Routes } from 'react-router-dom';
import { Toaster } from 'sonner';
import { TooltipProvider } from "@/components/ui/tooltip";
import LandingPage from '@/pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import MainLayout from './layouts/MainLayout';
import Details from './pages/Details';

const App = () => {
  return (
    <TooltipProvider>
      <div className="bg-zinc-900 min-h-screen">
        <Toaster position="bottom-right" richColors />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/details" element={<Details />} />
          
          <Route element={<MainLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
          </Route>
        </Routes>
      </div>
    </TooltipProvider>
  );
};

export default App;