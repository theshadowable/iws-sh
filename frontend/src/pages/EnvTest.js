import React from 'react';

export const EnvTest = () => {
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  
  return (
    <div style={{padding: '20px'}}>
      <h1>Environment Variable Test</h1>
      <p><strong>REACT_APP_BACKEND_URL:</strong> {backendUrl || 'undefined'}</p>
      <p><strong>Window Location Origin:</strong> {window.location.origin}</p>
      <p><strong>Using API:</strong> {backendUrl ? `${backendUrl}/api` : '/api'}</p>
    </div>
  );
};
