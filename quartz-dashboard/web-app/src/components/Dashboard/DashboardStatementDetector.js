// # MIT License

// # Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

// # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

// # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

// # THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import React, { useEffect, useMemo, useState } from 'react';
import '../../App.css';
import {AgGridReact} from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import Highlighter from "react-highlight-words";

const DashboardStatementDetector = ({params}) => {

    const [encryptionRowData, setEncryptionRowData] = useState([]);
    const [hashRowData, setHashRowData] = useState([]);
    const [searchStrings, setSearchStrings] = useState([]);
    const [sqlStatement, setSqlStatement] = useState("");

    const encryptionColumnDefs = [
        {headerName: "Row#", field: 'id', width:'100', cellRenderer: (params)=>{return <span>{params.rowIndex+1}</span>}},
        {headerName: "Algorithm", field: "algorithm", wrapText: true, width:'300'},
        {headerName: "Remediation", field: "remediation", wrapText: true, autoHeight: true},
        {headerName: "Text | Column", field: "encrypted_value", wrapText: true},
        {headerName: "Key", field: "key", wrapText: true},
        {headerName: "IV", field: "iv", wrapText: true},
        {headerName: "Key Derivation Function", field: "kdf", wrapText: true},
        {headerName: "Salt", field: "salt", wrapText: true},
        {headerName: "Info | Iterations", field: "iterations", wrapText: true},
    ];

    const hashingColumnDefs = [
        {headerName: "Row#", field: 'id', width:'100', cellRenderer: (params)=>{return <span>{params.rowIndex+1}</span>}},
        {headerName: "Algorithm", field: "algorithm", wrapText: true},
        {headerName: "Remediation", field: "remediation", wrapText: true, autoHeight: true},
        {headerName: "Text | Column", field: "encrypted_value", wrapText: true},
        {headerName: "Hash Length", field: "hash_length", wrapText: true},
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

    const gridOptions2 = {
        enableCellTextSelection: true,
        ensureDomOrder: true,
        pagination: true,
        paginationAutoPageSize: false,
        paginationPageSize: 5
    }

    
    useEffect(() => {
         setEncryptionRowData(params.rowData.encryption_references);
         setHashRowData(params.rowData.hashing_references);
         setSqlStatement(params.rowData.statement);
         setSearchStrings(params.rowData.search_strings);
    },[params]);


    return(
        <div>
            {/* <header>
                <h1>Crypto Detector of {gitrepo}</h1>
            </header> */}
                <div className="ag-theme-alpine" style={{paddingTop: '1%', textAlign: 'center'}}>
                    <h3>Scanned SQL Statement</h3> 
                        
                            <Highlighter
                                className="App-highlight"
                                searchWords={searchStrings}
                                autoEscape={true}
                                textToHighlight={sqlStatement}
                            />
                        
                </div>


                <div className="ag-theme-alpine" style={{height: '350px', paddingTop: '1%', textAlign: 'center'}}>
                    <h3>Scanned Encryption Calls</h3> 
                        <AgGridReact
                            columnDefs={encryptionColumnDefs}
                            rowData={encryptionRowData}
                            defaultColDef={defaultColDef}
                            gridOptions={gridOptions}
                            suppressRowTransform={true}
                            >
                        </AgGridReact>
                </div>

               <div className="ag-theme-alpine" style={{width: '65%', marginLeft: 'auto', marginRight: 'auto', height: '350px', paddingTop: '5%', textAlign: 'center'}}>
                    <h3>Scanned Hashing Calls</h3> 
                        <AgGridReact
                            columnDefs={hashingColumnDefs}
                            rowData={hashRowData}
                            defaultColDef={defaultColDef}
                            gridOptions={gridOptions2}
                            suppressRowTransform={true}
                            >
                        </AgGridReact>
                </div>


        </div>
    );
}
export default DashboardStatementDetector;
