// # MIT License

// # Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

// # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

// # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

// # THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import React, { useMemo, useState, useRef, useEffect } from 'react';
import '../../App.css';
import axios from 'axios';
import {AgGridReact} from 'ag-grid-react';
import { Graph } from "react-d3-graph";
import { PieChart } from 'react-minimal-pie-chart';
import { Input, Button, Icon, Dimmer, Header,Table  } from 'semantic-ui-react'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import  {myClientConfig} from '../GraphConfig';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';


// Rendering the Dashboard component 
const CloudApplicationDashboard = () => {
  
    // Local variables to store response and conditional values
    
    const scanResultReference = useRef(null);
    const [clientGraphVals, setClientGraph] = useState({'nodes':[], 'edges':[]});
    const [clientPieData, setClientPieData] = useState([{ "title": 'safe', "value": 0, "color": '#90EE90' }, { "title": 'unsafe', "value": 0, "color": '#F75D59' }]);
    const [isClientGraphDataLoaded, setClientGraphDataLoaded] = useState(false);
    const [clientRiskFactor, setClientRiskFactor] = useState('');
    const [clientScanStatus, setClientScanStatus] = useState('No scan initiated yet..!');
    const [clientSafe, setClientSafe] = useState('');
    const [clientUnsafe, setClientUnsafe] = useState('');
    const [scanTarget, setScanTarget] = useState('');
    const [scanTargetCloudAccessKeyId, setScanTargetCloudAccessKeyId] = useState('');
    const [scanTargetCloudSecretAccessKey, setScanTargetCloudSecretAccessKey] = useState('');
    const [scanTargetType, setScanTargetType] = useState('');
    const [msg, setMsg] = useState('');
    const [isError, setError] = useState(false);
    const [btnState, setButState] = useState(true);
    const [active, setActive] = useState(false);
    const [isCloudApplicationDataLoaded, setIsCloudApplicationDataLoaded] = useState(false);
    const [scanGraph, setScanGraph] = useState({});
    const [scanCheckRows, setScanCheckRows] = useState([]);
    
    const handleHide = (e) => {
        setActive(false);
    }

    const columnDefs = [
        {headerName: "Row#", field: 'id', width: '100', cellRenderer: (params)=>{return <span>{params.rowIndex+1}</span>}},
        {headerName: "Check Title", field: "check_title", wrapText: true, autoHeight: true},
        {headerName: "Service", field: "service_name", wrapText: true, autoHeight: true},
        {headerName: "Status", field: "status", wrapText: true, autoHeight: true},
        {headerName: "Region", field: "region", wrapText: true, autoHeight: true},
        {headerName: "Resource ID", field: "resource_id", wrapText: true, autoHeight: true},
        {headerName: "ARN", field: "resource_arn", wrapText: true, autoHeight: true}
        
    ];

    const SubmitUrl = async (e) => { 
      toast.warning("Fetching details..!");
      setActive(true);
      e.preventDefault();
      if(scanTargetType === "aws"){
        setScanTarget("https://aws.amazon.com/");
      }
      renderClientPiePlot(scanTarget);
      setMsg('');
      setError(false);
      if(true){
        if(isCloudApplicationDataLoaded){
          toast.info("Removing previous scan..!");
          setIsCloudApplicationDataLoaded(false);
        }
        
        try{

          const response = await axios.post('http://localhost:5000/scanCloudApplication', {
              scan_type: 'cloudApplication',
              target: scanTarget,
              scan_target_cloud_access_key_id : scanTargetCloudAccessKeyId,
              scan_target_cloud_secret_access_key : scanTargetCloudSecretAccessKey,
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
              setIsCloudApplicationDataLoaded(true);
              setScanGraph(response.data.graph);
              setScanCheckRows(response.data.scan_result);
            }

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

    const handleAccessKeyIdChange = (e) => {
      if(e.target.value !== undefined){
          setScanTargetCloudAccessKeyId(e.target.value);
          setButState(false);
          setMsg("");
          setIsCloudApplicationDataLoaded(false);
        }
        else{
          setError(false);
          setButState(true);
          setMsg("");
        }
    }

    const handleSecretAccessKeyChange = (e) => {
        if(e.target.value !== undefined){
            setScanTargetCloudSecretAccessKey(e.target.value);
          }
          else{
            setError(false);
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

    const scanGraphData = {
        nodes: scanGraph.nodes,
        links: scanGraph.edges,
      };

      const defaultColDef = useMemo(() => {
        return {
            resizable: true,
            filter: true,
            wrapHeaderText: true,
            autoHeaderHeight: true,
        };
        }, []);

    const gridOptions = {
        enableCellTextSelection: true,
        ensureDomOrder: true,
        pagination: true,
        paginationAutoPageSize: false,
        paginationPageSize: 3
    }

  const clientGraphConfig = myClientConfig;

  const scanGraphConfig = myClientConfig;


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
                <Table.Cell><b>Access Key ID</b></Table.Cell>
                <Table.Cell><Input focus type="text"
                              required
                              placeholder="cloud access key ID" 
                              value={scanTargetCloudAccessKeyId} 
                              name={scanTargetCloudAccessKeyId}
                              onChange={handleAccessKeyIdChange}
                              style = {{width: "100%"}}
                            />
                </Table.Cell>
            </Table.Row>
            <Table.Row >
                <Table.Cell><b>Secret Access Key</b></Table.Cell>
                <Table.Cell><Input focus type="text"
                              required
                              placeholder="cloud access key ID" 
                              value={scanTargetCloudSecretAccessKey} 
                              name={scanTargetCloudSecretAccessKey}
                              onChange={handleSecretAccessKeyChange}
                              style = {{width: "100%"}}
                            />
                </Table.Cell>
            </Table.Row>
            <Table.Row >
                <Table.Cell><b>Scan Target Cloud Type</b></Table.Cell>
                
                <Table.Cell><select
                              name={scanTargetType}
                              onChange={handleTypeChange}
                              style = {{width: "100%"}}
                            >
                              <option onClick={handleTypeChange} value="">Select a Cloud Service Provider</option>;
                              <option onClick={handleTypeChange} value="aws">AWS</option>;
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
          
              <Tab panes={panes2} style={{width:'90%', margin:'0 auto'}}/> 
            </div> */}
            
                  
      </div>

      {isCloudApplicationDataLoaded ?(
        <header> <h2 className='App' style={{ marginTop: '1%', paddingTop: '4%'}}>Scan Report</h2>
        <h3 className='App' style={{ marginTop: '1%', paddingTop: '4%'}}>Cloud Resources</h3></header>) : null}  
        
      <div tabIndex="0" ref={scanResultReference} className='left-rigt-ag-grid' style={{width: '50%', marginTop : '1%', display: 'flex', justifyContent: 'center'}}>
        {isCloudApplicationDataLoaded ? (<div tabIndex="0"  className='ag-theme-alpine' style={{width: '100%', height: '350px', paddingTop: '1%', display: 'flex', justifyContent: 'center', border: '1px solid gray'}}>
            <Graph 
                id="scan-graph-id" // id is mandatory
                data={scanGraphData}
                config={scanGraphConfig}
                layout={ {title: 'Deployed Resources Plot'} }
                />
          </div>) : null}
          </div>
          <div tabIndex="0" ref={scanResultReference} className='left-rigt-ag-grid' style={{marginTop : '1%', display: 'flex', justifyContent: 'center'}}>
          {isCloudApplicationDataLoaded ? (<div tabIndex="0"  className='ag-theme-alpine' style={{width: '92%', height: '450px', paddingTop: '1%'}}>
                <h3>Scan Checks</h3>
                <AgGridReact
                    columnDefs={columnDefs}
                    rowData={scanCheckRows}
                    defaultColDef={defaultColDef}
                    gridOptions={gridOptions}
                    suppressRowTransform={true}
                    >
                </AgGridReact>
          </div>) : null}
              
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

export default CloudApplicationDashboard;
