// # MIT License

// # Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

// # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

// # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

// # THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import React, { useMemo, useState, useRef, useEffect } from 'react';
import '../../App.css';
import axios from 'axios';
import { Graph } from "react-d3-graph";
import { PieChart } from 'react-minimal-pie-chart';
import { Input, Button, Icon, Dimmer, Header, Table  } from 'semantic-ui-react'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import  {myClientConfig, myScanConfig} from '../GraphConfig';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import DashboardServerDetector from './DashboardServerDetector';

// Rendering the Dashboard component 
const ApiDashboard = () => {
  
    // Local variables to store scan response and conditional values
    const scanResultReference = useRef(null);
    const [scanGraphVals, setScanGraph] = useState({'nodes':[], 'edges':[]});
    const [clientScanFailed, setClientScanFailed] = useState(false);
    const [clientGraphVals, setClientGraph] = useState({'nodes':[], 'edges':[]});
    const [clientPieData, setClientPieData] = useState([{ "title": 'safe', "value": 0, "color": '#90EE90' }, { "title": 'unsafe', "value": 0, "color": '#F75D59' }]);
    const [isClientGraphDataLoaded, setClientGraphDataLoaded] = useState(false);
    const [clientRiskFactor, setClientRiskFactor] = useState('');
    const [scanRiskFactor, setScanRiskFactor] = useState('');
    const [scanPieData, setScanPieData] = useState([{ "title": 'safe', "value": 0, "color": '#90EE90' }, { "title": 'unsafe', "value": 0, "color": '#F75D59' }]);
    const [isScanGraphDataLoaded, setScanGraphDataLoaded] = useState(false);
    const [targetScanStatus, setTargetScanStatus] = useState('No scan initiated yet..!');
    const [clientScanStatus, setClientScanStatus] = useState('No scan initiated yet..!');
    const [clientSafe, setClientSafe] = useState('');
    const [clientUnsafe, setClientUnsafe] = useState('');
    const [scanSafe, setScanSafe] = useState('');
    const [scanUnsafe, setScanUnsafe] = useState('');
    const [scanTarget, setScanTarget] = useState('');
    const [scanTargetPort, setScanTargetPort] = useState('');
    const [scanTargetProtocol, setScanTargetProtocol] = useState('');
    const [msg, setMsg] = useState('');
    const [isError, setError] = useState(false);
    const [btnState, setButState] = useState(true);
    const [active, setActive] = useState(false);
    const [isServerDataLoaded, setServerDataLoad] = useState(false);
    const [repoName, setReponame] = useState('');
    //Model consts
    const [cryproDetector, setCryproDetectorRow] = useState([]);
    
    // Hide the dimmer screen
    const handleHide = (e) => {
      setActive(false);
    }

    // Send request to perform scan
    const SubmitUrl = async (e) => {
      
      // Client side validations
      if(scanTarget === ''){
        setError('true');
        setMsg('Scan target not provided ..!');
        handleHide();
        return;
      }
      else if(parseInt(scanTargetPort) < 1 || parseInt(scanTargetPort) > 65535){
        setError('true');
        setMsg('Scan target port value is invalid..!');
        handleHide();
        return;
      }
      toast.warning("Fetching details..!");
      setActive(true);
      e.preventDefault();

      // Render the client scan details
      renderClientPiePlot(scanTarget);
      if(clientScanFailed){
        return;
      }
      setError(false);
      setMsg('');
      
      if(true){
        if(isScanGraphDataLoaded || isServerDataLoaded){
          toast.info("Removing previous scan..!");
          setScanGraphDataLoaded(false);
          setServerDataLoad(false);
        }
        
        try{
            
          /* const response = await axios.post("http://"+`${host}`+":"+`${port}`+'/getServerSecurity', {
              server: validateUrl(gitrepo),
              ratelimits: ratelimits,
              graphQlParam: graphQlParam,
              pullRequests: pullRequests,
              commitsMessages: commitsMessages,
              dependencies: dependencies
          }); */

          const response = await axios.post('http://localhost:5000/scanApi', {
            scan_type: "api",
            target: scanTarget,
            scan_target_port : scanTargetPort
          }, {timeout: 60000});

          if(typeof response.data === "string"){
            setClientPieData([{ "title": 'safe', "value": 0, "color": '#90EE90' }, { "title": 'unsafe', "value": 0, "color": '#F75D59' }]);
            setClientGraph({'nodes':[], 'edges':[]});
            setClientSafe('N/A');
            setClientUnsafe('N/A');
            setClientScanStatus('Scan Failed..!');
            setClientRiskFactor('N/A');
            if(response.data === 'None'){
              setError(true);
              setMsg("Invalid GitHub URL");
              setButState(true);
            }
            else{
              setError(true);
              setMsg(response.data);
              handleHide();
            }
          }
          else{
            setActive(false);
            setServerDataLoad(true);
            setCryproDetectorRow(response.data.scan_result);
            setScanGraph(response.data.graph);
            setScanPieData(response.data.scan_result[1]);
            setScanSafe(response.data.scan_result[1][0].value);
            setScanUnsafe(response.data.scan_result[1][1].value);
            setTargetScanStatus(response.data.scan_details[0].values);
            setScanGraphDataLoaded(true);
            setScanRiskFactor(response.data.scan_details[1].values);
            setReponame(response.data.scan_details[0].scan_target);
          }

        }catch (error) {
          console.log(error);
          setMsg('Failed to scan target..!');
          setError(true);
          handleHide();
        }
      }
    }

    // Handle form field changes and set local variable value
    const handleChange = (e) => {
      if(e.target.value !== undefined){
          setScanTarget(e.target.value);
          setButState(false);
          setMsg("");
          setError(false);
          setClientScanFailed(false);
        }
        else{
          setError(false);
          setServerDataLoad(false);
          setButState(true);
          setMsg("");
        }
    }

    const handlePortChange = (e) => {
      if(e.target.value !== undefined){
          setScanTargetPort(e.target.value);
        }
        else{
          setError(false);
          setServerDataLoad(false);
          setButState(true);
          setMsg("");
        }
    }

    const handleProtocolChange = (e) => {
        if(e.target.value !== undefined){
            setScanTargetProtocol(e.target.value);
          }
          else{
            setError(false);
            setServerDataLoad(false);
            setButState(true);
            setMsg("");
          }
      }
      
    // Render client scan details
    const renderClientPiePlot = async (target) => {
      var port = '443';
      if(scanTargetPort){
        port = scanTargetPort;
      }
      if(scanTarget === ''){
        setError('true');
        setMsg('Scan target not provided ..!');
        handleHide();
        return;
      }
      else if(parseInt(scanTargetPort) < 1 || parseInt(scanTargetPort) > 65535){
        setError('true');
        setMsg('Scan target port value is invalid..!');
        handleHide();
        return;
      }
      try{
        const response = await axios.post('http://localhost:5000/scanClient', {
          scan_type: 'host',
          target: target,
          scan_target_port: port,
        }, 3000);
  
        if(typeof response.data === "string"){
          setError(true);
          setMsg(response.data);
          handleHide();
          setClientScanFailed(true);
        }
        else{
          setClientPieData(response.data.scan_result[1]);
          setClientGraph(response.data.graph);
          setClientSafe(response.data.scan_result[1][0].value);
          setClientUnsafe(response.data.scan_result[1][1].value);
          setClientScanStatus(response.data.scan_details[0].values);
          setClientRiskFactor(response.data.scan_details[1].values);
        }
      }
      catch(error){
        handleHide();
        console.log(error);
        setMsg(error.message+' Failed to connect with target from client host..!');
        setError(true);
        setClientScanFailed(true);
      }
    }

    // if(!isClientGraphDataLoaded){
    //   renderClientPiePlot('cisco.com');
    //   setClientGraphDataLoaded(!isClientGraphDataLoaded);
    // }
  
    /* Dependency Graph - Cipher suites supported on Client and Scan Target */
    const clientGraphData = {
      nodes: clientGraphVals.nodes,
      links: clientGraphVals.edges,
    };

  const scanGraphData = {
    nodes: scanGraphVals.nodes,
    links: scanGraphVals.edges,
  }

  const clientGraphConfig = myClientConfig;
  const scanGraphConfig = myScanConfig;

    // Accessing the reponame to display in Tabs 
    const repo = repoName;

  const renderCryptos = useMemo(() => { 
    let params = {'rowData': cryproDetector, 'repo': repo, }
    if(isServerDataLoaded){
      return (<DashboardServerDetector params={params}/>);}
},[cryproDetector]);

  /* const panes2 = [
    { menuItem: 'Scan Plots', render: () => <Tab.Pane > { renderGraphData } </Tab.Pane> }
  ] */
  useEffect(() => {
    scanResultReference.current.focus();
  }, [])
  

  return (
    <div>
      
        <header className='App'>
            <h1>Quartz: Post Quantum Security (Threat Analysis Dashboard)</h1>
        </header>

    {/* Input form for GitHub url and toast message */}
      <div className='App'>
        <p  id="msg" style={{padding:'2%'}} className={isError ? 'error' : 'success'}>{msg}</p>
      </div>

      {/* Rendering the two Ag-Grids */}
      <div className='left-rigt-ag-grid'>
            <div className="ag-theme-alpine" style={{display: 'flex', justifyContent: 'center', width: '50%', height: '350px'}}>
        <form onSubmit={SubmitUrl} method="POST">  
        <Table celled striped fixed size='large'>
          <Table.Header>
            <Table.Row textAlign='center'>
              <Table.HeaderCell colSpan={2}>Launch Scan</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Header>
            <Table.Row textAlign='center'>
              <Table.HeaderCell>Label</Table.HeaderCell>
              <Table.HeaderCell>Input</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
              <Table.Row >
                <Table.Cell><b>Scan Target </b><b style={{color:"red"}}>*</b></Table.Cell>
                <Table.Cell><Input focus type="text"
                                placeholder="Scan Target (URL | IP)" 
                                value={scanTarget} 
                                name={scanTarget}
                                onChange={handleChange}
                                style = {{width: "100%"}}
                                required
                              />
                </Table.Cell>
            </Table.Row>
            <Table.Row >
                <Table.Cell><b>Scan Target Port </b> </Table.Cell>
                <Table.Cell><Input focus type="number"
                                step="1"
                                min="1"
                                max="65535"
                                placeholder="target port (default 443)" 
                                value={scanTargetPort} 
                                name={scanTargetPort}
                                onChange={handlePortChange}
                                style = {{width: "100%"}}
                              />
                </Table.Cell>
            </Table.Row>
            <Table.Row >
                <Table.Cell><b>Scan Target Protocol </b>(Only for API scans) </Table.Cell>
                <Table.Cell><select
                              placeholder="target protocol, e.g. mysql, ftp (for API scans)"  
                              name={scanTargetProtocol}
                              onChange={handleProtocolChange}
                              style = {{width: "100%"}}
                            >
                              <option value="" default>Select Protocol</option>
                              <option value="mysql">MySQL</option>
                              <option value="postgres">PostgreSQL</option>
                              <option value="smtp">SMTP (included as test for invalid input)</option>
                            </select>
                </Table.Cell>
            </Table.Row>
            <Table.Row >
                <Table.Cell></Table.Cell>
                <Table.Cell><div style={{textAlign:'center'}}><Button primary size='large' type='submit' disabled={btnState} onClick={SubmitUrl}> Scan </Button></div></Table.Cell>
            </Table.Row>
          </Table.Body>
      </Table> 
        </form>
            </div>
            {/* <div style={{display: 'flex', justifyContent: 'center', width: '50%', height: '350px', marginLeft: '1%'}}>
              <Table celled striped fixed size='small'>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell textAlign='center'>Client Scan Status</Table.HeaderCell>
                    <Table.HeaderCell>{clientScanStatus}</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Header>
                  <Table.Row  textAlign='center'>
                    <Table.HeaderCell>Cipher Suite Dependency Graph</Table.HeaderCell>
                    <Table.HeaderCell>Quantum Safe/Unsafe Risk</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                  <Table.Body  textAlign='center'>
                      <Table.Row>
                          <Table.Cell> <Graph 
                                        id="client-graph-id" // id is mandatory
                                        data={clientGraphData}
                                        config={clientGraphConfig}
                                        layout={ {title: 'Cipher Suite Dependency Graph'} }
                                      />
                          </Table.Cell>
                          <Table.Cell><div style={{height:'150px', width:'50%', marginLeft:'20%'}}><PieChart
                                        data={clientPieData}
                                      /></div>
                                      <div style={{fontSize: '14px', margin: '5%'}}>
                                      <Table celled>
                                          <Table.Body>
                                              <Table.Row >
                                                  <Table.Cell positive><b>Safe: </b>{clientSafe} </Table.Cell>
                                                  <Table.Cell negative><b>Unsafe: </b>{clientUnsafe}</Table.Cell>
                                                  <Table.Cell><b>Global Quantum Risk Factor: </b>{clientRiskFactor}</Table.Cell>
                                              </Table.Row>
                                          </Table.Body>
                                      </Table></div>
                            </Table.Cell>
                      </Table.Row>
                  </Table.Body>
              </Table>
            </div> */}
            
                  
      </div>

      {isScanGraphDataLoaded ?(
        <header> <h2 className='App' style={{paddingTop: '2%'}}>Scan Report</h2></header>) : null}
      <div tabIndex="0" ref={scanResultReference} className='left-rigt-ag-grid'>
      
        {isScanGraphDataLoaded ?(
      <div className='ag-theme-alpine' style={{display: 'flex', justifyContent: 'center', width: '50%', height: '450px', paddingTop: '1%'}} id="scanResult">
          <div className="ag-theme-alpine" style={{width: '100%', height: '100%'}}>
          <h3 style={{width:'100%'}}>Status and Data Plots</h3>
          <Table celled striped fixed size='small' focus>
            <Table.Header>
              <Table.Row>
                <Table.HeaderCell textAlign='center'>Target Scan Status</Table.HeaderCell>
                <Table.HeaderCell>{targetScanStatus}</Table.HeaderCell>
              </Table.Row>
            </Table.Header>
            <Table.Header>
              <Table.Row  textAlign='center'>
                <Table.HeaderCell>Cipher Suite Dependency Graph</Table.HeaderCell>
                <Table.HeaderCell>Quantum Safe/Unsafe Risk</Table.HeaderCell>
              </Table.Row>
            </Table.Header>
              <Table.Body  textAlign='center'>
                  <Table.Row>
                      <Table.Cell> <Graph 
                                    id="scan-graph-id" // id is mandatory
                                    data={scanGraphData}
                                    config={scanGraphConfig}
                                    layout={ {title: isScanGraphDataLoaded ? 'Cipher Suite Dependency Graph' : ''} }
                                    height="350px"
                                  />
                      </Table.Cell>
                      <Table.Cell textAlign='center'><div style={{height:'250px', margin:'5%'}}><PieChart
                                    data={scanPieData}
                                  /></div>
                                  <div style={{fontSize: '14px', margin: '10%'}}>
                                  <Table celled>
                                      <Table.Body>
                                          <Table.Row >
                                              <Table.Cell positive><b>Safe: </b>{scanSafe} </Table.Cell>
                                              <Table.Cell negative><b>Unsafe: </b>{scanUnsafe}</Table.Cell>
                                              <Table.Cell wrapText><b>Global Quantum Risk Factor: </b>{scanRiskFactor}</Table.Cell>
                                          </Table.Row>
                                      </Table.Body>
                                  </Table></div>
                        </Table.Cell>
                  </Table.Row>
              </Table.Body>
          </Table>
          </div>
        </div>) : null}
        {(isScanGraphDataLoaded) ?(<div className="ag-theme-alpine" style={{display: 'flex', justifyContent: 'center', width: '50%', height: '525px', paddingTop: '1%', marginLeft: '1%'}}>

               {renderCryptos} </div>): null}
              
      <ToastContainer
            autoClose={2000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
            style={{width: '500px'}}
      />
      </div>
      <Dimmer active={active} onClickOutside={handleHide} page>
            <Header as='h2' icon inverted>
              <Icon name='wait' />
              Waiting for results..!
            </Header>
          </Dimmer>
    </div>
  );
}

export default ApiDashboard;
