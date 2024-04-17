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

const DashboardFileSystemDetector = ({params}) => {

    const [rowData, setRowData] = useState([]);
    

    const columnDefs = [
        {headerName: "#", field: 'id', width:65, cellRenderer: (params)=>{return <span>{params.rowIndex+1}</span>}},
        {headerName: "Algorithm", field: "name", wrapText: true, autoHeight: true, width:160},
        {headerName: "Key Size (Min - Max)", field: "keysize", wrapText: true, autoHeight: true, width:100},
        {headerName: "Quantum Safe", field: "quantum_safe", wrapText: true, autoHeight: true, width:110},
        {headerName: "Risk Factor", field: "risk_factor", wrapText: true, autoHeight: true, width:100},
        {headerName: "Remediation", field: "remediation", wrapText: true, autoHeight: true, width:160},
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
        paginationPageSize: 5
    }

    
    useEffect(() => {
         setRowData(params.rowData[0]);
    },[params]);


    return(
        <div className="ag-theme-alpine" style={{width: '100%', height: '100%'}}>
            <h3>Encryption Algorithm Details</h3>
                        <AgGridReact
                            columnDefs={columnDefs}
                            rowData={rowData}
                            defaultColDef={defaultColDef}
                            gridOptions={gridOptions}
                            suppressRowTransform={true}
                            overlayLoadingTemplate={
                                '<span class="ag-overlay-loading-center">Please wait while your rows are loading</span>'
                              }
                              overlayNoRowsTemplate={
                                '<span style="padding: 10px; border: 2px solid #444; background: lightgoldenrodyellow">No data found!!</span>'
                              }
                            >
                        </AgGridReact>
                </div>

    );
}
export default DashboardFileSystemDetector;
