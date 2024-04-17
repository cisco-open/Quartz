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
import DashboardCryptoDetector from './DashboardCryptoDetector';

// Rendering the Dashboard component 
const RepoDashboard = () => {
  
    const scanResultReference = useRef(null);
    const [clientScanFailed, setClientScanFailed] = useState(false);
    const [clientGraphVals, setClientGraph] = useState({'nodes':[], 'edges':[]});
    const [clientPieData, setClientPieData] = useState([{ "title": 'safe', "value": 0, "color": '#90EE90' }, { "title": 'unsafe', "value": 0, "color": '#F75D59' }]);
    const [isClientGraphDataLoaded, setClientGraphDataLoaded] = useState(false);
    const [clientRiskFactor, setClientRiskFactor] = useState('');
    const [isScanGraphDataLoaded, setScanGraphDataLoaded] = useState(false);
    const [clientScanStatus, setClientScanStatus] = useState('No scan initiated yet..!');
    const [clientSafe, setClientSafe] = useState('');
    const [clientUnsafe, setClientUnsafe] = useState('');
    const [scanTarget, setScanTarget] = useState('');
    const [msg, setMsg] = useState('');
    const [isError, setError] = useState(false);
    const [btnState, setButState] = useState(true);
    const [active, setActive] = useState(false);
    const [isServerDataLoaded, setServerDataLoad] = useState(false);
    const [isRepoDataLoaded, setRepoDataLoad] = useState(false);
    const [repoName, setReponame] = useState('');
    //Model consts
    const [cryproDetector, setCryproDetectorRow] = useState([]);
    
    const handleHide = (e) => {
      setActive(false);
    }

    const SubmitUrl = async (e) => { 
      if(scanTarget === ''){
        setError('true');
        setMsg('Scan target not provided ..!');
        handleHide();
        return;
      }
      toast.warning("Fetching details..!");
      setActive(true);
      e.preventDefault();
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

          const response = await axios.post('http://localhost:5000/scanRepo', {
            scan_type: "repo",
            target: scanTarget,
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
            setRepoDataLoad(true);
            setCryproDetectorRow(response.data.scan_result);
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
  
    const renderClientPiePlot = async (target) => {
      var port = '443';
      if(scanTarget === ''){
        setError('true');
        setMsg('Scan target not provided ..!');
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


  const clientGraphConfig = myClientConfig;

    // Accessing the reponame to display in Tabs 
    const repo = repoName;

  const renderCryptos = useMemo(() => { 
    let params = {'rowData': cryproDetector, 'repo': repo, }
    if(isRepoDataLoaded){
      return (<DashboardCryptoDetector params={params}/>);}
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

      {isRepoDataLoaded ?(
        <header> <h2 className='App' style={{paddingTop: '5%'}}>Scan Report</h2></header>) : null}
      <div tabIndex="0" ref={scanResultReference} className='left-rigt-ag-grid'>
      
      { isRepoDataLoaded ? (<div tabIndex="0"  className='ag-theme-alpine' style={{width: '100%', height: '600px', paddingTop: '1%'}} id="repoResult">
        
        {renderCryptos} </div>) : null}
              
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

export default RepoDashboard;
