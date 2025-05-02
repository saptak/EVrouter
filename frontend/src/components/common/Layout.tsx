import React, { ReactNode } from 'react';
import { useTheme } from '../../contexts/ThemeContext';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <div className={`min-h-screen bg-gray-50 ${theme === 'dark' ? 'dark' : ''}`}>
      <header className="bg-primary shadow-md p-4 text-white">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">EVrouter</h1>
          <button 
            onClick={toggleTheme}
            className="p-2 rounded-md bg-gray-700 hover:bg-gray-600 transition-colors"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </header>
      
      <main className="container mx-auto p-4">
        {children}
      </main>
      
      <footer className="bg-gray-800 p-4 mt-8 text-white">
        <div className="container mx-auto text-center text-sm">
          &copy; {new Date().getFullYear()} EVrouter - Electric Vehicle Route Planner
        </div>
      </footer>
    </div>
  );
};

export default Layout;
