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
import { Icon, Input, Button, Dimmer, Header, Table  } from 'semantic-ui-react'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import  {myClientConfig, myConfig, myScanConfig} from '../GraphConfig';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import DashboardDatabaseDetector from './DashboardDatabaseDetector';
import DashboardFileSystemDetector from './DashboardFileSystemDetector';
import DashboardStatementDetector from './DashboardStatementDetector';


// Rendering the Dashboard component 
const DataAtRestDashboard = () => {
  
    const scanResultReference = useRef(null);
    const [scanGraphVals, setScanGraph] = useState({'nodes':[], 'edges':[]});
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
    const [scanType, setScanType] = useState('database');
    const [scanTarget, setScanTarget] = useState('');
    const [scanTargetPort, setScanTargetPort] = useState('');
    const [scanTargetCloudOwner, setScanTargetCloudOwner] = useState('');
    const [scanTargetType, setScanTargetType] = useState('');
    const [msg, setMsg] = useState('');
    const [isError, setError] = useState(false);
    const [btnState, setButState] = useState(true);
    const [active, setActive] = useState(false);
    const [isDatabaseDataLoaded, setIsDatabaseDataLoaded] = useState(false);
    const [isCloudDataLoaded, setIsCloudDataLoaded] = useState(false);
    const [cloudTarget, setCloudTarget] = useState('');
    const [cloudTargetEncryptionStatus, setCloudTargetEncryptionStatus] = useState('');
    const [cloudTargetEncryptionAlgo, setCloudTargetEncryptionAlgo] = useState('');
    const [cloudTargetPQCSecure, setCloudTargetPQCSecure] = useState('');
    const [isFileSystemDataLoaded, setIsFileSystemDataLoaded] = useState(false);
    const [fileSystemDetector, setFileSystemDetectorRow] = useState([]);
    const [scanInformationSource, setScanInformationSource] = useState('');
    const [DatabaseDetectorRow, setDatabaseDetectorRow] = useState([]);
    const [scanTargetStatement, setScanTargetStatement] = useState('');
    const [isStatementDataLoaded, setIsStatementDataLoaded] = useState(false);
    const [statementDetectorData, setStatementDetectorData] = useState({});
    

    const databases = [
      {
        "name" : "Select a Database type",
        "value" : ""
      },
        {
        "name": "MySQL",
        "value": "mysql"
        }
    ]

    const cloud_storages = [
      {
        "name" : "Select a cloud storage type",
        "value" : ""
      },
        {
        "name": "S3",
        "value": "s3"
        }
    ]

    const file_storage_os = [
      {
        "name" : "Select a file storage OS type",
        "value" : ""
      },
        {
        "name": "Ubuntu",
        "value": "ubuntu"
        },
        {
        "name": "Red Hat",
        "value": "red hat"
        },
        {
        "name": "Windows",
        "value": "windows"
        }
    ]

    const handleHide = (e) => {
      setActive(false);
    }

    let getOptions = null;

    

    const SubmitUrl = async (e) => { 
      toast.warning("Fetching details..!");
      setActive(true);
      e.preventDefault();
      renderClientPiePlot(scanTarget);
      setMsg('');
      setError(false);
      if(true){
        if(isScanGraphDataLoaded || isCloudDataLoaded || isDatabaseDataLoaded || isStatementDataLoaded || isFileSystemDataLoaded){
          toast.info("Removing previous scan..!");
          setScanGraphDataLoaded(false);
          setIsDatabaseDataLoaded(false);
          setIsStatementDataLoaded(false);
          setIsCloudDataLoaded(false);
          setIsFileSystemDataLoaded(false);
        }
        
        try{

          if(scanType === "statement"){
            try{
              const response = await axios.post('http://localhost:5000/scan', {
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
              
            /* const response = await axios.post("http://"+`${host}`+":"+`${port}`+'/getServerSecurity', {
                server: validateUrl(gitrepo),
                ratelimits: ratelimits,
                graphQlParam: graphQlParam,
                pullRequests: pullRequests,
                commitsMessages: commitsMessages,
                dependencies: dependencies
            }); */
            
            const response = await axios.post('http://localhost:5000/scan', {
              scan_type: scanType,
              target: scanTarget,
              scan_target_port : scanTargetPort,
              scan_target_cloud_owner : scanTargetCloudOwner,
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
              /* setButState(true);
              console.log(response.data.nodes);
              console.log(response.data.edges);
              setGitRepo('');*/
              if(scanType==="cloud")
              {
                setIsCloudDataLoaded(true);
                setCloudTarget(response.data.cloud_target);
                setCloudTargetEncryptionStatus(response.data.status);
                setCloudTargetEncryptionAlgo(response.data.algo);
                setCloudTargetPQCSecure(response.data.pqc_secure);
              }
              else if(scanType==="database"){
                setIsDatabaseDataLoaded(true);
                setDatabaseDetectorRow(response.data.scan_result);
              }
              else if(scanType==="fs"){
                setIsFileSystemDataLoaded(true);
                setFileSystemDetectorRow(response.data.scan_result);
                setScanGraph(response.data.graph);
                setScanPieData(response.data.scan_result[1]);
                setScanSafe(response.data.scan_result[1][0].value);
                setScanUnsafe(response.data.scan_result[1][1].value);
                setTargetScanStatus(response.data.scan_details[0].values);
                setScanGraphDataLoaded(true);
                setScanRiskFactor(response.data.scan_details[1].values);
                setScanInformationSource(response.data.scan_details[2].values);
              }
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
          setIsCloudDataLoaded(false);
          setIsDatabaseDataLoaded(false);
        }
        else{
          setError(false);
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
          setButState(true);
          setMsg("");
        }
    }

    const handleOwnerChange = (e) => {
      if(e.target.value !== undefined){
          setScanTargetCloudOwner(e.target.value);
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

    const handleRadioChange = (e) => {
      if(e.target.value !== undefined){
        setScanType(e.target.value);
        setScanTargetType('');
        if(scanType==="database"){

          getOptions = null;
          getOptions = databases.map((database) => 
                <option onClick={handleTypeChange} value={database.value}>{database.name} </option>);
        }
        else if(scanType === "cloud"){
          getOptions = null;
          getOptions = cloud_storages.map((cloud) => 
                <option onClick={handleTypeChange} value={cloud.value}>{cloud.name} </option>);
        }
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
          setButState(true);
          setMsg("");
        }
    }

    if(scanType === "database" || scanType === "statement"){
      getOptions = null;
      getOptions = databases.map((database) => 
            <option onClick={handleTypeChange} value={database.value}>{database.name} </option>);
    }
    else if(scanType === "cloud"){
      getOptions = null;
      getOptions = cloud_storages.map((cloud) => 
            <option onClick={handleTypeChange} value={cloud.value}>{cloud.name} </option>);
    }
    else if(scanType === "fs"){
      getOptions = null;
      getOptions = file_storage_os.map((fs) => 
            <option onClick={handleTypeChange} value={fs.value}>{fs.name} </option>);
    }
  
    const renderClientPiePlot = async (target) => {
      var port = '443';
      if(scanTargetPort){
        port = scanTargetPort;
      }
      try{
        const response = await axios.post('http://localhost:5000/scan', {
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

  const scanGraphData = {
    nodes: scanGraphVals.nodes,
    links: scanGraphVals.edges,
  }

  const scanGraphConfig = myScanConfig;


  const renderCryptos = useMemo(() => {
    if (isFileSystemDataLoaded){
      let params = {'rowData': fileSystemDetector}
    return (<DashboardFileSystemDetector params={params}/>);}
    else if(isDatabaseDataLoaded){
      let params = {'rowData': DatabaseDetectorRow}
      return (<DashboardDatabaseDetector params={params}/>);
    }
    else if(isStatementDataLoaded){
      let params = {'rowData': statementDetectorData}
      return (<DashboardStatementDetector params={params}/>);
    }
  },[fileSystemDetector,DatabaseDetectorRow, statementDetectorData]);

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
                  <Table.Cell><b>Scan Type</b></Table.Cell>
                  <Table.Cell><label><b>Database</b></label>
                    <Input focus type="radio" 
                      required 
                      value="database" 
                      name="scan-type"
                      onChange={handleRadioChange}
                      checked={scanType === "database"}
                      style = {{width: "10%"}}
                    />
                   <label><b>Cloud</b></label>
                    <Input focus type="radio" 
                      required 
                      value="cloud" 
                      name="scan-type"
                      onChange={handleRadioChange}
                      checked={scanType === "cloud"}
                      style = {{width: "10%"}}
                    />
                  <label><b>File System</b></label>
                    <Input focus type="radio" 
                      required 
                      value="fs" 
                      name="scan-type"
                      onChange={handleRadioChange}
                      checked={scanType === "fs"}
                      style = {{width: "10%"}} 
                    />
                    <label><b>SQL Statement</b></label>
                    <Input focus type="radio" 
                      required 
                      value="statement" 
                      name="scan-type"
                      onChange={handleRadioChange}
                      checked={scanType === "statement"}
                      style = {{width: "10%"}} 
                    /></Table.Cell>
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
                <Table.Cell><b>{scanType === "database" ? "Scan Target Port" : scanType === "cloud" ? "Resource Owner" : scanType === "statement" ? "SQL Statement" : "Scan Target Port/Resource Owner"} </b></Table.Cell>
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
                              />) : scanType === "cloud" ? (<Input focus type="text"
                              required
                              placeholder="cloud resource owner ID" 
                              value={scanTargetCloudOwner} 
                              name={scanTargetCloudOwner}
                              onChange={handleOwnerChange}
                              style = {{width: "100%"}}
                            />) : scanType === "statement" ? (<div><input type="file"
                            name="scanTargetStatement"
                            accept=".txt, .sql" 
                            placeholder="Upload a file containing SQL statement"
                            onChange={uploadFile} 
                            style = {{width: "300px"}}
                          /> <textarea 
                            name="scanTargetStatement" 
                            rows="4" 
                            cols="50" 
                            placeholder="Upload a file containing SQL statement"
                            onChange={handleFileChange} 
                            style = {{width: "300px"}}>
                          </textarea></div>) : 'N/A'} 
                </Table.Cell>
            </Table.Row>
            <Table.Row >
                <Table.Cell><b>{(scanType === "database" || scanType === "statement") ? "Scan Target Database Type" : scanType === "cloud" ? "Scan Target Cloud Type" : "Scan Target OS Type"} </b></Table.Cell>
                
                <Table.Cell><select
                              name={scanTargetType}
                              onChange={handleTypeChange}
                              style = {{width: "100%"}}
                            >
                              {getOptions}
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

      {(isDatabaseDataLoaded || isFileSystemDataLoaded) ?(
        <header> <h2 className='App' style={{ marginTop: '1%', paddingTop: '2%'}}>Scan Report</h2></header>) : null}
      {(isStatementDataLoaded) ?(
      <header> <h2 className='App' style={{ marginTop: '5%', paddingTop: '2%'}}>Scan Report</h2></header>) : null}
      {isCloudDataLoaded ?(
        <header> <h2 className='App' style={{ marginTop: '1%', paddingTop: '4%'}}>Scan Report</h2></header>) : null}  
      <div tabIndex="0" ref={scanResultReference} className='left-rigt-ag-grid' style={{marginTop : '1%', display: 'flex', justifyContent: 'center'}}>
        { isDatabaseDataLoaded ? (<div tabIndex="0"  className='ag-theme-alpine' style={{width: '100%', height: '600px', paddingTop: '1%'}} id="repoResult">

                {renderCryptos} </div>) : null}
        {isCloudDataLoaded ? (<div tabIndex="0"  className='ag-theme-alpine' style={{width: '50%', height: '50px', paddingTop: '1%'}}>
        <Table celled striped fixed size='small' focus>
            <Table.Header>
              <Table.Row>
                <Table.HeaderCell textAlign='center'>Response Parameter</Table.HeaderCell>
                <Table.HeaderCell>Value</Table.HeaderCell>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              <Table.Row>
                <Table.Cell textAlign='center'>Target</Table.Cell>
                <Table.Cell>{cloudTarget}</Table.Cell>
              </Table.Row>
            </Table.Body>
            <Table.Body>
              <Table.Row  textAlign='center'>
                <Table.Cell>Encryption Status</Table.Cell>
                <Table.Cell>{cloudTargetEncryptionStatus}</Table.Cell>
              </Table.Row>
            </Table.Body>
            <Table.Body>
              <Table.Row  textAlign='center'>
                <Table.Cell>Encryption Algorithm</Table.Cell>
                <Table.Cell>{cloudTargetEncryptionAlgo}</Table.Cell>
              </Table.Row>
            </Table.Body>
            <Table.Body>
              <Table.Row  textAlign='center'>
                <Table.Cell>PQC Secure</Table.Cell>
                <Table.Cell>{cloudTargetPQCSecure}</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
          </div>) : null}

          {isFileSystemDataLoaded ?(
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
              <Table.Row>
                <Table.HeaderCell textAlign='center'>Information Source</Table.HeaderCell>
                <Table.HeaderCell>{scanInformationSource}</Table.HeaderCell>
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
                                    layout={ {title: isClientGraphDataLoaded ? 'Cipher Suite Dependency Graph' : ''} }
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
        {(isFileSystemDataLoaded) ?(<div className="ag-theme-alpine" style={{display: 'flex', justifyContent: 'center', width: '50%', height: '550px', paddingTop: '1%', marginLeft: '1%'}}>

               {renderCryptos} </div>): null}

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

export default DataAtRestDashboard;
