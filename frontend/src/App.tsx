import React from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/common/Layout';
import RouteController from './components/routing/RouteController';

function App() {
  return (
    <ThemeProvider>
      <Layout>
        <RouteController />
      </Layout>
    </ThemeProvider>
  );
}

export default App;
