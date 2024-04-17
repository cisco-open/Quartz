// # MIT License

// # Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

// # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

// # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

// # THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



export const myClientConfig = {
    automaticRearrangeAfterDropNode: false,
    staticGraphWithDragAndDrop: false,
    nodeHighlightBehavior: true,
    freezeAllDragEvents: false,
    collapsible: false,
    staticGraph: false,
    d3:{
      linkLength: 150,
      gravity: -150
    },
    node: {
      color: "lightblue",
      size: 100,
      labelProperty: 'id',
      highlightStrokeColor: "blue",
      mouseCursor: 'crosshair',
      opacity: 0.9,
      renderLabel: true,
      freezeAllDragEvents:false,
      labelPosition: 'top',
      symbolType: "circle",
    },
    link: {
      type: "CURVE_SMOOTH",
      highlightColor: "red",
      mouseCursor: 'pointer',
      selfLinkDirection:"TOP_RIGHT",
      renderLabel: false,
    },
    directed: true,
    width: 300,
    height: 250
  };

  export const myScanConfig = {
    automaticRearrangeAfterDropNode: false,
    staticGraphWithDragAndDrop: false,
    nodeHighlightBehavior: true,
    freezeAllDragEvents: false,
    collapsible: false,
    staticGraph: false,
    d3:{
      linkLength: 150,
      gravity: -150
    },
    node: {
      color: "lightblue",
      size: 100,
      labelProperty: 'id',
      highlightStrokeColor: "blue",
      mouseCursor: 'crosshair',
      opacity: 0.9,
      renderLabel: true,
      freezeAllDragEvents:false,
      labelPosition: 'top',
      symbolType: "circle",
    },
    link: {
      type: "CURVE_SMOOTH",
      highlightColor: "red",
      mouseCursor: 'pointer',
      selfLinkDirection:"TOP_RIGHT",
      renderLabel: false,
    },
    directed: true,
    width: 300,
    height: 350
  };
