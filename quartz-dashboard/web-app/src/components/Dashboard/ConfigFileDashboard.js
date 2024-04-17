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
import { Button, Icon, Dimmer, Header,Table  } from 'semantic-ui-react'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import  {myClientConfig} from '../GraphConfig';
import {AgGridReact} from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';


// Rendering the Dashboard component 
const ConfigFileDashboard = () => {
  
    const scanResultReference = useRef(null);
    const [clientGraphVals, setClientGraph] = useState({'nodes':[], 'edges':[]});
    const [clientPieData, setClientPieData] = useState([{ "title": 'safe', "value": 0, "color": '#90EE90' }, { "title": 'unsafe', "value": 0, "color": '#F75D59' }]);
    const [isClientGraphDataLoaded, setClientGraphDataLoaded] = useState(false);
    const [clientRiskFactor, setClientRiskFactor] = useState('');
    const [clientScanStatus, setClientScanStatus] = useState('No scan initiated yet..!');
    const [clientSafe, setClientSafe] = useState('');
    const [clientUnsafe, setClientUnsafe] = useState('');
    const [scanTargetType, setScanTargetType] = useState('');
    const [msg, setMsg] = useState('');
    const [isError, setError] = useState(false);
    const [btnState, setButState] = useState(true);
    const [active, setActive] = useState(false);
    const [isConfigDataLoaded, setIsConfigDataLoaded] = useState(false);
    const [scanTargetStatement, setScanTargetStatement] = useState('');
    const [high, setHigh] = useState('');
    const [medium, setMedium] = useState('');
    const [low, setLow] = useState('');
    const [scanTerraformRowData, setScanTerraformRowData] = useState([]);
    const [scanSBOMRowData, setScanSBOMRowData] = useState([]);
    const [scanVulnRowData, setScanVulnRowData] = useState([]);
    const [scanPieData, setScanPieData] = useState([]);
    const [policiesValidated, setPoliciesValidated] = useState('');
    const [violatedPolicies, setViolatedPolicies] = useState('');
    
    const handleHide = (e) => {
        setActive(false);
    }

    const SubmitUrl = async (e) => { 
      toast.warning("Fetching details..!");
      setActive(true);
      e.preventDefault();
      setMsg('');
      setError(false);
      if(true){
        if(isConfigDataLoaded){
          toast.info("Removing previous scan..!");
          setIsConfigDataLoaded(false);
        }
        
        try{

          const response = await axios.post('http://172.18.0.1:6000/scan', {
              scan_type: 'configFile',
              target: 'none',
              scan_target_statement: scanTargetStatement,
              scan_target_type: scanTargetType
            }, 30000);

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
              setIsConfigDataLoaded(true);
              setHigh(response.data.high);
              setLow(response.data.low);
              setMedium(response.data.medium);
              setScanTerraformRowData(response.data.violations);
              setScanPieData(response.data.pie_chart_data);
              setPoliciesValidated(response.data.policies_validated);
              setViolatedPolicies(response.data.violated_policies);
              setScanSBOMRowData(response.data.sbom);
              setScanVulnRowData(response.data.vulns);
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
            setIsConfigDataLoaded(false);
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

    if(!isClientGraphDataLoaded){
      renderClientPiePlot('cisco.com');
      setClientGraphDataLoaded(!isClientGraphDataLoaded);
    }
  
    /* Dependency Graph - Cipher suites supported on Client and Scan Target */
    const clientGraphData = {
      nodes: clientGraphVals.nodes,
      links: clientGraphVals.edges,
    };

  const clientGraphConfig = myClientConfig;

    const columnDefs = [
        {headerName: "Row#", field: 'id', width:'100', cellRenderer: (params)=>{return <span>{params.rowIndex+1}</span>}},
        {headerName: "Resource Name", field: "resource_name", wrapText: true, autoHeight: true,},
        {headerName: "Resource Type", field: "resource_type", wrapText: true, autoHeight: true,},
        {headerName: "Description", field: "description", wrapText: true, autoHeight: true},
        {headerName: "Severity", field: "severity", wrapText: true, autoHeight: true,},
    ];

    const sbomColumnDefs = [
        {headerName: "Row#", field: 'id', width:'100', cellRenderer: (params)=>{return <span>{params.rowIndex+1}</span>}},
        {headerName: "Name", field: "name", wrapText: true, autoHeight: true,},
        {headerName: "Version", field: "version", wrapText: true, autoHeight: true,},
        {headerName: "Type", field: "type", wrapText: true, autoHeight: true},
    ];

    const vulnColumnDefs = [
        {headerName: "Row#", field: 'id', width:'100', cellRenderer: (params)=>{return <span>{params.rowIndex+1}</span>}},
        {headerName: "ID", field: "cve_id", wrapText: true, autoHeight: true,},
        {headerName: "URL", field: "url", wrapText: true, autoHeight: true,},
        {headerName: "Description", field: "description", wrapText: true, autoHeight: true},
    ];

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
        paginationPageSize: 6
    }

  /* const panes2 = [
    { menuItem: 'Scan Plots', render: () => <Tab.Pane > { renderGraphData } </Tab.Pane> }
  ] */
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
                <Table.Cell><b>Config File</b></Table.Cell>
                <Table.Cell><input type="file"
                            name="scanTargetStatement"
                            //accept=".txt, .sql" 
                            placeholder="Upload a file containing Terraform config"
                            onChange={uploadFile} 
                            style = {{width: "300px"}}
                          /> <textarea 
                            name="scanTargetStatement" 
                            rows="4" 
                            cols="50" 
                            placeholder="Paste config file here"
                            onChange={handleFileChange} 
                            style = {{width: "300px"}}>
                          </textarea>
                </Table.Cell>
            </Table.Row>
            <Table.Row >
                <Table.Cell><b>Scan Target Config File Type</b></Table.Cell>
                
                <Table.Cell><select
                              name={scanTargetType}
                              onChange={handleTypeChange}
                              style = {{width: "100%"}}
                            >
                              <option onClick={handleTypeChange} value="">Select a Config File Type</option>;
                              <option onClick={handleTypeChange} value="docker">Docker</option>;
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
            <div style={{display: 'flex', justifyContent: 'center', width: '50%', height: '350px', marginLeft: '1%'}}>
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
          
            {/* <Tab panes={panes2} style={{width:'90%', margin:'0 auto'}}/> */}
            </div>
            
                  
      </div>

      {isConfigDataLoaded ?(
        <header> <h2 className='App' style={{ marginTop: '1%', paddingTop: '4%'}}>Scan Report</h2></header>) : null}  
      <div tabIndex="0" ref={scanResultReference} className='left-rigt-ag-grid' style={{marginTop : '1%', display: 'flex', justifyContent: 'center'}}>
        
        {isConfigDataLoaded ? (
            
                <div className="ag-theme-alpine" style={{width: '85%', height: '600px', paddingTop: '1%', textAlign: 'center', border: '1px solid gray'}}>
                    <h3>Validated Policies</h3> 
                        <AgGridReact
                            columnDefs={columnDefs}
                            rowData={scanTerraformRowData}
                            defaultColDef={defaultColDef}
                            gridOptions={gridOptions}
                            suppressRowTransform={true}
                            >
                        </AgGridReact>
                </div>) : null}
        {isConfigDataLoaded ? (
            <div style={{width: '50%', height: '300px', paddingTop: '1%', marginLeft: '1%', textAlign: 'center'}}>
                <h3> Distribution of Violations</h3>
            <PieChart style={{marginTop:'5%'}}
                                    data={scanPieData}
                                    />
            <div style={{fontSize: '14px', margin: '10%'}}>
            <Table celled>
                <Table.Body>
                    <Table.Row >
                        <Table.Cell negative><b>High:</b> {high}</Table.Cell>
                        <Table.Cell warning><b>Medium:</b> {medium}</Table.Cell>
                        <Table.Cell positive><b>Low:</b> {low}</Table.Cell>
                    </Table.Row>
                </Table.Body>
            </Table> 
            </div>
            </div>) : null}

        </div>

        <div tabIndex="0" ref={scanResultReference} className='left-rigt-ag-grid' style={{marginTop : '1%', display: 'flex', justifyContent: 'center'}}>

            {isConfigDataLoaded ? (
            
                <div className="ag-theme-alpine" style={{width: '85%', height: '600px', paddingTop: '1%', textAlign: 'center', border: '1px solid gray'}}>
                    <h3>SBOM</h3> 
                        <AgGridReact
                            columnDefs={sbomColumnDefs}
                            rowData={scanSBOMRowData}
                            defaultColDef={defaultColDef}
                            gridOptions={gridOptions}
                            suppressRowTransform={true}
                            >
                        </AgGridReact>
                </div>) : null}

        </div>
        <div tabIndex="0" ref={scanResultReference} className='left-rigt-ag-grid' style={{marginTop : '1%', display: 'flex', justifyContent: 'center'}}>
        {isConfigDataLoaded ? (
            
            <div className="ag-theme-alpine" style={{width: '85%', height: '600px', paddingTop: '1%', textAlign: 'center', border: '1px solid gray'}}>
                <h3>Vulnerabilities</h3> 
                    <AgGridReact
                        columnDefs={vulnColumnDefs}
                        rowData={scanVulnRowData}
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

export default ConfigFileDashboard;
