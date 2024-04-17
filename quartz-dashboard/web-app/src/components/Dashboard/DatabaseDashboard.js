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
import { Input, Button, Icon, Dimmer, Header,Table  } from 'semantic-ui-react'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import  {myClientConfig} from '../GraphConfig';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import DashboardDatabaseDetector from './DashboardDatabaseDetector';
import DashboardStatementDetector from './DashboardStatementDetector';


// Rendering the Dashboard component 
const DatabaseDashboard = () => {
  
    const scanResultReference = useRef(null);
    const [clientGraphVals, setClientGraph] = useState({'nodes':[], 'edges':[]});
    const [clientPieData, setClientPieData] = useState([{ "title": 'safe', "value": 0, "color": '#90EE90' }, { "title": 'unsafe', "value": 0, "color": '#F75D59' }]);
    const [isClientGraphDataLoaded, setClientGraphDataLoaded] = useState(false);
    const [clientRiskFactor, setClientRiskFactor] = useState('');
    const [clientScanStatus, setClientScanStatus] = useState('No scan initiated yet..!');
    const [clientSafe, setClientSafe] = useState('');
    const [clientUnsafe, setClientUnsafe] = useState('');
    const [scanType, setScanType] = useState('database');
    const [scanTarget, setScanTarget] = useState('');
    const [scanTargetPort, setScanTargetPort] = useState('');
    const [scanTargetType, setScanTargetType] = useState('');
    const [msg, setMsg] = useState('');
    const [isError, setError] = useState(false);
    const [btnState, setButState] = useState(true);
    const [active, setActive] = useState(false);
    const [isDatabaseDataLoaded, setIsDatabaseDataLoaded] = useState(false);
    const [DatabaseDetectorRow, setDatabaseDetectorRow] = useState([]);
    const [scanTargetStatement, setScanTargetStatement] = useState('');
    const [isStatementDataLoaded, setIsStatementDataLoaded] = useState(false);
    const [statementDetectorData, setStatementDetectorData] = useState({});
    
    const handleHide = (e) => {
        setActive(false);
    }

    const SubmitUrl = async (e) => { 
      toast.warning("Fetching details..!");
      setActive(true);
      e.preventDefault();
      renderClientPiePlot(scanTarget);
      setMsg('');
      setError(false);
      if(true){
        if(isDatabaseDataLoaded || isStatementDataLoaded){
          toast.info("Removing previous scan..!");
          setIsDatabaseDataLoaded(false);
          setIsStatementDataLoaded(false);
        }
        
        try{

            if(scanType === "statement"){
                try{
                  const response = await axios.post('http://localhost:5000/scanDatabase', {
                    scan_type: scanType,
                    target: scanTarget,
                    scan_target_statement: scanTargetStatement,
                    scan_target_type: scanTargetType
                  }, 3000);
    
                  if(typeof response.data === "string"){
                    setError(true);
                    setMsg(response.data);
                  }
                  else{
                    setActive(false);
                    setIsStatementDataLoaded(true);
                    setStatementDetectorData(response.data);
                  }
                }catch (error) {
                  console.log(error);
                  setMsg(error.message);
                  setError(true);
                }
              }
              else{
                const response = await axios.post('http://localhost:5000/scanDatabase', {
                  scan_type: scanType,
                  target: scanTarget,
                  scan_target_port : scanTargetPort,
                  scan_target_type: scanTargetType
                }, 3000);
    
                if(typeof response.data === "string"){
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
                  setIsDatabaseDataLoaded(true);
                  setDatabaseDetectorRow(response.data.scan_result);
                }}

        }catch (error) {
          console.log(error);
          setMsg(error.message+' Failed to scan target..!');
          setError(true);
          handleHide();
        }
      }
      else{
        setError(current => !current);
        setMsg("You must select GraphQL parameter, to avoid the GraphQL API error..!");
      }
    }

    const handleChange = (e) => {
      if(e.target.value !== undefined){
          setScanTarget(e.target.value);
          setButState(false);
          setMsg("");
          setIsDatabaseDataLoaded(false);
          setIsStatementDataLoaded(false);
        }
        else{
          setError(false);
          setIsDatabaseDataLoaded(false);
          setIsStatementDataLoaded(false);
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
            setIsDatabaseDataLoaded(false);
            setIsStatementDataLoaded(false); 
            setButState(true);
            setMsg("");
        }
    }

    const handleTypeChange = (e) => {
      if(e.target.value !== undefined){
          setScanTargetType(e.target.value);
          console.log(scanTargetType);
        }
        else{
          setError(false);
          setButState(true);
          setIsDatabaseDataLoaded(false);
          setIsStatementDataLoaded(false);
          setMsg("");
        }
    }

    const handleRadioChange = (e) => {
        if(e.target.value !== undefined){
          setScanType(e.target.value);
          setScanTargetType('');
        }
        else{
          setError(false);
          setIsDatabaseDataLoaded(false);
          setIsStatementDataLoaded(false);
          setButState(true);
          setMsg("");
        }
      }
  
      const uploadFile = (e) => {
        const fileReader = new FileReader();
        fileReader.readAsText(e.target.files[0], "UTF-8");
        fileReader.onload = e => {
          console.log("e.target.result", e.target);
          const target = e.target;
          setScanTargetStatement(target?.result);
          setButState(false);
        }
      }
  
      const handleFileChange = (e) => {
        if(e.target.value !== undefined){
            setScanTargetStatement(e.target.value);
            setButState(false);
          }
          else{
            setError(false);
            setIsDatabaseDataLoaded(false);
            setIsStatementDataLoaded(false);
            setButState(true);
            setMsg("");
          }
      }
  
    const renderClientPiePlot = async (target) => {
      var port = '443';

      try{
        const response = await axios.post('http://localhost:5000/scanClient', {
          scan_type: 'host',
          target: target,
          scan_target_port: port,
          scan_target_protocol: '',
        }, 3000);
  
        if(typeof response.data === "string"){
          setError(true);
          setMsg(response.data);
          handleHide();
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

  const renderCryptos = useMemo(() => {
    if(isDatabaseDataLoaded){
      let params = {'rowData': DatabaseDetectorRow}
      return (<DashboardDatabaseDetector params={params}/>);
    }
    else if(isStatementDataLoaded){
      let params = {'rowData': statementDetectorData}
      return (<DashboardStatementDetector params={params}/>);
    }
  },[DatabaseDetectorRow, statementDetectorData]);


  useEffect(() => {
    scanResultReference.current.focus();
  }, [])
  

  return (
    <div>
      
        <header className='App'>
            <h1>Quartz: Post Quantum Security of Data At Rest (Threat Analysis Dashboard)</h1>
        </header>

    {/* Input form for GitHub url and toast message */}
      <div className='App'>
        <p  id="msg" style={{padding:'2%'}} className={isError ? 'error' : 'success'}>{msg}</p>
      </div>

      {/* Rendering the two Ag-Grids */}
      <div className='left-rigt-ag-grid'>
            <div className="ag-theme-alpine" style={{display: 'flex', justifyContent: 'center', width: '50%', height: '350px'}}>
        <form onSubmit={SubmitUrl} method="post">  
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
                  <Table.Cell><b>Scan Type</b></Table.Cell>
                  <Table.Cell>
                    <Input focus type="radio" 
                      required 
                      value="database" 
                      name="scan-type"
                      onChange={handleRadioChange}
                      checked={scanType === "database"}
                      style = {{width: "10%"}}
                    /><label><b>Database</b></label>
                    <Input focus type="radio" 
                      required 
                      value="statement" 
                      name="scan-type"
                      onChange={handleRadioChange}
                      checked={scanType === "statement"}
                      style = {{width: "10%"}} 
                    /><label><b>SQL Statement</b></label></Table.Cell>
              </Table.Row>
              <Table.Row >
                <Table.Cell><b>Scan Target</b></Table.Cell>
                <Table.Cell><Input focus type="text" 
                                required
                                placeholder="Scan Target (URL | IP)" 
                                value={scanTarget} 
                                name={scanTarget}
                                onChange={handleChange}
                                style = {{width: "100%"}}
                              />
                </Table.Cell>
            </Table.Row>
            <Table.Row >
            <Table.Cell><b>{scanType === "database" ? "Scan Target Port" : "SQL Statement"} </b></Table.Cell>
                <Table.Cell>{scanType === "database" ? (<Input focus type="number"
                                required
                                step="1"
                                min="1"
                                max="65535"
                                placeholder="target port (for API scans)" 
                                value={scanTargetPort} 
                                name={scanTargetPort}
                                onChange={handlePortChange}
                                style = {{width: "100%"}}
                              />) : (<div><input type="file"
                            name="scanTargetStatement"
                            accept=".txt, .sql" 
                            placeholder="Upload a file containing SQL statement"
                            onChange={uploadFile} 
                            style = {{width: "300px"}}
                          /> <textarea 
                            name="scanTargetStatement" 
                            rows="4" 
                            cols="50" 
                            placeholder="Paste SQL statement here"
                            onChange={handleFileChange} 
                            style = {{width: "300px"}}>
                          </textarea></div>)} 
                </Table.Cell>
            </Table.Row>
            <Table.Row >
                <Table.Cell><b>Scan Target Database Type</b></Table.Cell>
                
                <Table.Cell><select
                              name={scanTargetType}
                              onChange={handleTypeChange}
                              style = {{width: "100%"}}
                            >
                              <option onClick={handleTypeChange} value="">Select a Database Type</option>;
                              <option onClick={handleTypeChange} value="mysql">MySQL</option>;
                            </select>
                </Table.Cell>
            </Table.Row>
            <Table.Row >
                <Table.Cell></Table.Cell>
                <Table.Cell><div style={{textAlign:'center'}}><Button primary size='large' disabled={btnState} onClick={SubmitUrl}> Scan </Button></div></Table.Cell>
            </Table.Row>
          </Table.Body>
      </Table> 
        </form>
        {/* </form> */}
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
            </div>
             */}
                  
      </div>

      {isDatabaseDataLoaded || isStatementDataLoaded ?(
        <header> <h2 className='App' style={{ marginTop: '1%', paddingTop: '4%'}}>Scan Report</h2></header>) : null}  
      <div tabIndex="0" ref={scanResultReference} className='left-rigt-ag-grid' style={{marginTop : '1%', display: 'flex', justifyContent: 'center'}}>
        
      { isDatabaseDataLoaded ? (<div tabIndex="0"  className='ag-theme-alpine' style={{width: '100%', height: '600px', paddingTop: '1%'}} id="repoResult">

        {renderCryptos} </div>) : null}

      {(isStatementDataLoaded) ?(<div className="ag-theme-alpine" style={{width: '100%', height: '350px', paddingTop: '1%', marginLeft: '1%'}}>

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

export default DatabaseDashboard;
