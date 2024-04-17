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
import { Table } from 'semantic-ui-react';
import { PieChart } from 'react-minimal-pie-chart';

const DashboardDatabaseDetector = ({params}) => {

    const [rowData, setRowData] = useState([]);
    const [pieData, setPieData] = useState();
    const [tableData, setTableData] = useState('');

    const columnDefs = [
        {headerName: "Row#", field: 'id', width:'100', cellRenderer: (params)=>{return <span>{params.rowIndex+1}</span>}},
        {headerName: "Feature", field: "key", wrapText: true, autoHeight: true, width:'300'},
        {headerName: "Configuration", field: "value", wrapText: true, autoHeight: true,},
        {headerName: "Quantum-safe", field: "safe", wrapText: true, autoHeight: true,},
        
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

    
    useEffect(() => {
         setRowData(params.rowData[0]);
         let piData = params.rowData[1];
         setPieData(piData);
         setTableData(params.rowData[2][0]);
    },[params]);

    console.log(rowData);


    return(
        <div>
            {/* <header>
                <h1>Crypto Detector of {gitrepo}</h1>
            </header> */}
            
            <div className='left-rigt-ag-grid'>

                <div className="ag-theme-alpine" style={{width: '70%', height: '600px', paddingTop: '1%', textAlign: 'center', border: '1px solid gray'}}>
                    <h3>Relevant Components List</h3> 
                        <AgGridReact
                            columnDefs={columnDefs}
                            rowData={rowData}
                            defaultColDef={defaultColDef}
                            gridOptions={gridOptions}
                            suppressRowTransform={true}
                            >
                        </AgGridReact>
                </div>

                <div style={{width: '50%', height: '300px', paddingTop: '1%', marginLeft: '1%', textAlign: 'center'}}>
                    <h3> Quantum Safe/Unsafe Components Pie Plot</h3>
                <PieChart style={{marginTop:'5%'}}
                                        data={pieData}
                                      />
                <div style={{fontSize: '14px', margin: '10%'}}>
                <Table celled>
                    <Table.Body>
                        <Table.Row >
                            <Table.Cell positive><b>Safe:</b> {tableData.Safe}</Table.Cell>
                            <Table.Cell warning><b>Unsafe:</b> {tableData.Unsafe}</Table.Cell>
                        </Table.Row>
                    </Table.Body>
                </Table> 
                </div>
                </div>

            </div>

        </div>
    );
}
export default DashboardDatabaseDetector;
