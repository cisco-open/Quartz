// # MIT License

// # Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

// # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

// # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

// # THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import React from 'react';
import { BrowserRouter, Route, Switch } from "react-router-dom";
import Dashboard from "./components/Dashboard/Dashboard";
import NAvBar from './components/NavBar';
import './App';
import ErrorBoundary from './components/ErrorBoundary';
import AlgoDashboard from './components/Dashboard/AlgoDashboard';
import DataAtRestDashboard from './components/Dashboard/DataAtRestDashboard';
import ServerDashboard from './components/Dashboard/ServerDashboard';
import ApiDashboard from './components/Dashboard/ApiDashboard';
import RepoDashboard from './components/Dashboard/RepoDashboard';
import DatabaseDashboard from './components/Dashboard/DatabaseDashboard';
import CloudDashboard from './components/Dashboard/CloudDashboard';
import FileSystemDashboard from './components/Dashboard/FileSystemDashboard';
import TerraformDashboard from './components/Dashboard/TerraformDashboard';
import CloudApplicationDashboard from './components/Dashboard/CloudApplicationDashboard';
import ConfigFileDashboard from './components/Dashboard/ConfigFileDashboard';

function App() {

  return (
    <div >
      
        <BrowserRouter >
          <NAvBar />
          <Switch>
            <Route exact path="/">
              <div className="App-header">
              Quartz: Post-Quantum Threat Analysis and Remediation
              </div>
            </Route>
            <Route exact path="/dashboard" >
              <ErrorBoundary>
                  <Dashboard />
              </ErrorBoundary>
            </Route>
            <Route exact path="/algo-dashboard" >
              <ErrorBoundary>
                  <AlgoDashboard />
              </ErrorBoundary>
            </Route>
            {/* <Route exact path="/data-at-rest-dashboard" >
              <ErrorBoundary>
                  <DataAtRestDashboard />
              </ErrorBoundary>
            </Route> */}
            <Route exact path="/server" >
              <ErrorBoundary>
                  <ServerDashboard />
              </ErrorBoundary>
            </Route>
            <Route exact path="/api" >
              <ErrorBoundary>
                  <ApiDashboard />
              </ErrorBoundary>
            </Route>
            <Route exact path="/repository" >
              <ErrorBoundary>
                  <RepoDashboard />
              </ErrorBoundary>
            </Route>
            <Route exact path="/database" >
              <ErrorBoundary>
                  <DatabaseDashboard />
              </ErrorBoundary>
            </Route>
            <Route exact path="/cloud" >
              <ErrorBoundary>
                  <CloudDashboard />
              </ErrorBoundary>
            </Route>
            <Route exact path="/file-system" >
              <ErrorBoundary>
                  <FileSystemDashboard />
              </ErrorBoundary>
            </Route>
            <Route exact path="/terraform" >
              <ErrorBoundary>
                  <TerraformDashboard />
              </ErrorBoundary>
            </Route>
            <Route exact path="/cloudApplication" >
              <ErrorBoundary>
                  <CloudApplicationDashboard />
              </ErrorBoundary>
            </Route>
            {/* <Route exact path="/configFile" >
              <ErrorBoundary>
                  <ConfigFileDashboard />
              </ErrorBoundary>
            </Route> */}
          </Switch>
        </BrowserRouter>
      
    </div>
  );
}

export default App;
