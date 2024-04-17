// # MIT License

// # Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

// # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

// # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

// # THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import React, { useMemo, useState } from 'react';
import '../../App.css';
import axios from 'axios';
import { Input, Button } from 'semantic-ui-react'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {AgGridReact} from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

// Rendering the Dashboard component 
const AlgoDashboard = () => {

  // Local variables to store response and conditional values

    const[isAlgoDataLoaded, setAlgoDataLoaded] = useState(false);
    const [algoName, setAlgoName] = useState('');
    const [pqcSafe, setPqcSafe] = useState('');
    const [riskFactor, setRiskFactor] = useState('');
    const [recommendation, setRecommendation] = useState('');
    const [keyExchange, setKeyEchange] = useState('');
    const [encryption, setEncryption] = useState('');
    const [hash, setHash] = useState('');
    const [msg, setMsg] = useState('');
    const [isError, setError] = useState(false);
    const [btnState, setButState] = useState(true);
    const [rowDataLeft, setRowDataLeft] = useState([]);


    // Delete algorithm entry from database
    const deleteAlgo = async (e) => {
        toast.warning("Deleting algo..!");
        try{ 
            const response = await axios.post('http://localhost:5000/deleteAlgoSpec', {
                algo_name: e.currentTarget.value
            }, 3000);
  
            if(typeof response.data === "string"){
              if(response.data === 'Failed to delete record.'){
                setError(true);
                setMsg("Unable to delete algorithm information..!");
                setButState(true);
              }
              else{
                setError(true);
                setButState(true);
                setMsg("Check FLask API..!");
              }
            }
            else{
              setMsg('Deleted algorithm information successfully..!');
              setButState(true);
              listAlgo();
            }
  
          }catch (error) {
            console.log(error);
            setMsg(error.message+' Check server connection..!');
            setError(true);
          }
    }
    

    // Request to list all available algorithm information
    const listAlgo = async (e) => {
        toast.warning("Fetching algo details..!");
        try{ 
            const response = await axios.post('http://localhost:5000/listAllAlgoSpec', {}, 3000);
  
            if(typeof response.data === "string"){
              if(response.data === 'Failed to fetch records'){
                setError(true);
                setMsg("Unable to fetch algorithm information..!");
                setButState(true);
              }
              else{
                setError(true);
                setButState(true);
                setMsg("Check FLask API..!");
              }
            }
            else{
              setRowDataLeft(response.data);
              setMsg('');
            }
  
          }catch (error) {
            console.log(error);
            setMsg(error.message+' Check server connection..!');
            setError(true);
          }
    }

    if(!isAlgoDataLoaded){
        listAlgo();
        setAlgoDataLoaded(true);
    }

    // Request to update algorithm specifications
    const SubmitUrl = async (e) => { 
      toast.warning("Updating algo details..!");
      e.preventDefault();
      if(true){
        try{

          const response = await axios.post('http://localhost:5000/algoSpec', {
            algo_name: algoName,
            pqc_safe: pqcSafe,
            risk_factor : riskFactor,
            recommendation: recommendation,
            key_exchange: keyExchange,
            encryption:encryption,
            hash:hash
          }, 3000);

          if(typeof response.data === "string"){
            setError(true);
            setButState(true);
            setMsg(response.data);
          }
          else{
            setMsg(response.data.message);
          }

        }catch (error) {
          console.log(error);
          setMsg(error.message+' Check database/server connection..!');
          setError(true);
        }
      }
      listAlgo();
    }


    // Handling changes in form fields
    const handleNameChange = (e) => {
      if(e.target.value !== undefined){
          setAlgoName(e.target.value);
          setButState(false);
          setMsg("");
        }
        else{
          setError(false);
          setButState(true);
          setMsg("");
        }
    }
    const handleRecommendationChange = (e) => {
        if(e.target.value !== undefined){
            setRecommendation(e.target.value);
            setButState(false);
            setMsg("");
          }
          else{
            setError(false);
            setButState(true);
            setMsg("");
          }
      }
      const handleKxChange = (e) => {
        if(e.target.value !== undefined){
            setKeyEchange(e.target.value);
            setButState(false);
            setMsg("");
          }
          else{
            setError(false);
            setButState(true);
            setMsg("");
          }
      }
      const handleEncryptionChange = (e) => {
        if(e.target.value !== undefined){
            setEncryption(e.target.value);
            setButState(false);
            setMsg("");
          }
          else{
            setError(false);
            setButState(true);
            setMsg("");
          }
      }
      const handleHashChange = (e) => {
        if(e.target.value !== undefined){
            setHash(e.target.value);
            setButState(false);
            setMsg("");
          }
          else{
            setError(false);
            setButState(true);
            setMsg("");
          }
      }

      const handleRiskFactorChange = (e) => {
        if(e.target.value !== undefined){
            setRiskFactor(e.target.value);
            setButState(false);
            setMsg("");
          }
          else{
            setError(false);
            setButState(true);
            setMsg("");
          }
      }

    const handleRadioChange = (e) => {
      if(e.target.value !== undefined){
        setPqcSafe(e.target.value);
        }
        else{
          setError(false);
          setButState(true);
          setMsg("");
        }
    }


  // Set configuration options for AG Grid
  const gridOptions1 = {
      enableCellTextSelection: true,
      ensureDomOrder: true,
      pagination: true,
      paginationAutoPageSize: false,
      paginationPageSize: 10
  }

  const renderActions = (algo_name) => {
    const id = algo_name.valueFormatted ? algo_name.valueFormatted : algo_name.value;
    return ( <Button primary size='tiny' value={id} onClick={deleteAlgo}>Delete</Button> );
    
  }
  // Left side Grid column defenisions
  const columnDefs1 = [
    {headerName: "Name", field:'name', wrapText: true, autoHeight: true},
    {headerName: "PQC Safe", field:'pqc_safe', width: 130},
    {headerName: "Risk Factor", field:'risk_factor', wrapText: true, autoHeight: true, width: 130},
    {headerName: "Remediation", field:'comments', wrapText: true, autoHeight: true},
    {headerName: "Assymetric Encryption", field:'key_exchange', wrapText: true, autoHeight: true, widrth: 100},
    {headerName: "Symmetric Encryption", field:'encryption', wrapText: true, autoHeight: true, width: 200},
    {headerName: "Hash", field:'hash', wrapText: true, autoHeight: true, width: 100},
    {headerName: "", field:'name', cellRenderer: renderActions}
  ];
  
  // Default configurations of AG-Grid 
  const defaultColDef = useMemo(() => {
    return {
        resizable: true,
        filter: true,
        // flex: 1,
    };
  }, []);

  // Dashboard Grid styles
  const agGridStyle = {
      height: '600px', 
      width: '95%', 
      textAlign: 'center',
  }

  return (
    <div>

        <header className='App'>
            <h1>Quartz: Post Quantum Security (Algo Dashboard)</h1>
        </header>

      {/* Input form for GitHub url and toast message */}
      <div className='App'>
        <br/>
        <h2> Add/Update Algo Information</h2>
        <form onSubmit={SubmitUrl} method="post">
          <table className='algo-table' style={{border: "solid 1px", margin:"auto"}}>
            <tr style={{border: "solid 1px"}}>
              <th style={{border: "1px solid gray"}}>Label</th>
              <th style={{border: "1px solid gray"}}>Input</th>
            </tr>
            <tr>
              <td style={{border: "1px solid gray"}}><label><b>Algo Name</b> </label></td>
              <td style={{border: "1px solid gray"}}><Input focus type="text" 
                  required
                  placeholder="algo name" 
                  value={algoName} 
                  name={algoName}
                  onChange={handleNameChange}
                  style = {{width: "200px"}}
                />&nbsp;&nbsp;</td>
            </tr>
            <tr>
              <td style={{border: "1px solid gray"}}><label><b>PQC Safe</b></label></td>
              <td style={{border: "1px solid gray"}}>Yes <Input focus type="radio" 
                  required 
                  value="1" 
                  name="pqcSafe"
                  onChange={handleRadioChange}
                  checked={pqcSafe === "1"}
                  style = {{width: "30px"}}
                />
            <label>&nbsp;&nbsp;No</label>
                <Input focus type="radio" 
                  required 
                  value="0" 
                  name="pqcSafe"
                  onChange={handleRadioChange}
                  checked={pqcSafe === "0"}
                  style = {{width: "30px"}}
                /></td>
            </tr>
            <tr>
              <td style={{border: "1px solid gray"}}><label><b>Risk Factor</b> </label></td>
              <td style={{border: "1px solid gray"}}><Input focus type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  required
                  placeholder="risk factor (0-1.0)" 
                  value={riskFactor} 
                  name={riskFactor}
                  onChange={handleRiskFactorChange}
                  style = {{width: "200px"}}
                /></td>
            </tr>
            <tr>
              <td style={{border: "1px solid gray"}}><label><b>Remediation</b> </label></td>
              <td style={{border: "1px solid gray"}}><textarea focus
                  required
                  placeholder="Suggested Remediation"
                  rows="2" 
                  cols="50" 
                  value={recommendation} 
                  name={recommendation}
                  onChange={handleRecommendationChange}
                  style = {{width: "200px"}}
                ></textarea></td>
            </tr>
            <tr>
              <td style={{border: "1px solid gray"}}><label><b>Key Exchange Mechanism</b> </label></td>
              <td style={{border: "1px solid gray"}}><select
                    placeholder="Assymetric Encryption Algorithm, e.g. ECDHE-RSA"  
                    name={keyExchange}
                    onChange={handleKxChange}
                    style = {{width: "300px"}}
                  >
                    <option value="" default>Select KX</option>
                    <option value="RSA">RSA</option>
                    <option value="ECDHE-RSA">ECDHE-RSA</option>
                    <option value="CRYSTALS-KYBER">CRYSTALS-KYBER</option>
                    <option value="SIKE">SIKE</option>
                  </select></td>
            </tr>
            <tr>
              <td style={{border: "1px solid gray"}}><label><b>Encryption Algorithm</b> </label></td>
              <td style={{border: "1px solid gray"}}><select
                    placeholder="Symmetric Encryption Algorithm, e.g. AES, RSA"  
                    name={encryption}
                    onChange={handleEncryptionChange}
                    style = {{width: "300px"}}
                  >
                    <option value="" default>Select Encryption</option>
                    <option value="3DES">3DES</option>
                    <option value="RSA">RSA</option>
                    <option value="AES128">AES128</option>
                    <option value="AES256">AES256</option>
                  </select></td>
            </tr>
            <tr>
              <td style={{border: "1px solid gray"}}><label><b>Hashing Algorithm</b> </label></td>
              <td style={{border: "1px solid gray"}}><select
                    placeholder="Hashing Algorithm, e.g. MD5, SHA"  
                    name={hash}
                    onChange={handleHashChange}
                    style = {{width: "300px"}}
                  >
                    <option value="" default>Select Hash</option>
                    <option value="MD5">MD5</option>
                    <option value="SHA">SHA</option>
                    <option value="SHA256">SHA256</option>
                    <option value="SHA384">SHA384</option>
                  </select></td>
            </tr>
            <tr>
              <td style={{border: "1px solid gray"}}></td>
              <td style={{border: "1px solid gray"}}><Button primary size='small' disabled={btnState}> Submit </Button></td>
            </tr>
          </table>
          
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
        </form>
        <p  id="msg" style={{padding:'1%'}} className={isError ? 'error' : 'success'}>{msg}</p>
        <h2>Algorithm Information</h2><br/>
      </div>
      
      {/* Rendering the two Ag-Grids */}
      <div className='left-rigt-ag-grid'>
            <div className="ag-theme-alpine" style={agGridStyle}>
                  <AgGridReact
                        columnDefs={columnDefs1}
                        rowData={rowDataLeft}
                        defaultColDef={defaultColDef}
                        gridOptions={gridOptions1}
                        >
                    </AgGridReact>
            </div>
      </div>




    </div>
  );
}

export default AlgoDashboard;
