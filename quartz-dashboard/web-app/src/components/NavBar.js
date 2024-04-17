// # MIT License

// # Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

// # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

// # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

// # THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import '../App.css';
import { useHistory } from 'react-router-dom';
import { Menu, Image } from 'semantic-ui-react';


const  NavBar = () => {

    const history = useHistory();

    const handleItemClick = (e, {name}) =>{
        e.preventDefault();
        if (name === 'Home'){
            history?.push("/");
        }else if(name === 'Dashboard'){
            history?.push("/dashboard");
        }else if(name === 'Algo-Dashboard'){
            history?.push("/algo-dashboard");
        }else if(name === 'Data-At-Rest-Dashboard'){
            history?.push("/data-at-rest-dashboard");
        }else if(name === 'Server'){
            history?.push("/server");
        }
        else if(name === 'Server'){
            history?.push("/server");
        }
        else if(name === 'API'){
            history?.push("/api");
        }
        else if(name === 'Repository'){
            history?.push("/repository");
        }
        else if(name === 'Cloud'){
            history?.push("/cloud");
        }
        else if(name === 'Database'){
            history?.push("/database");
        }
        else if(name === 'File System'){
            history?.push("/file-system");
        }
        else if(name === 'Terraform'){
            history?.push("/terraform");
        }
        else if(name === 'CloudApplication'){
            history?.push("/cloudApplication");
        }
        // else if(name === 'Config File'){
        //     history?.push("/configFile");
        // }
    }


    return (
            <Menu size="large" stackable borderless>
                <Menu.Item>
                    {/* <a  href='/'>
                    <Image src={logo} width='60px'/>
                    </a> */}
                </Menu.Item>
                <Menu.Item
                name='Home'
                // active={activeItem === "Home"}
                onClick={handleItemClick}
                />
                <Menu.Item
                name='Server'
                // active={activeItem === "Server"}
                onClick={handleItemClick}
                />
                <Menu.Item
                name='API'
                // active={activeItem === "API"}
                onClick={handleItemClick}
                />
                <Menu.Item
                name='Repository'
                // active={activeItem === "API"}
                onClick={handleItemClick}
                />
                <Menu.Item
                name='Cloud'
                // active={activeItem === "Server"}
                onClick={handleItemClick}
                />
                <Menu.Item
                name='Database'
                // active={activeItem === "Server"}
                onClick={handleItemClick}
                />
                <Menu.Item
                name='File System'
                // active={activeItem === "Server"}
                onClick={handleItemClick}
                />
                <Menu.Item
                name='Terraform'
                // active={activeItem === "Server"}
                onClick={handleItemClick}
                />
                <Menu.Item
                name='CloudApplication'
                // active={activeItem === "Server"}
                onClick={handleItemClick}
                />
                <Menu.Item
                name='Algo-Dashboard'
                // active={activeItem === "Dashboard"}
                onClick={handleItemClick}
                />
                {/* <Menu.Item
                name='Config File'
                // active={activeItem === "Dashboard"}
                onClick={handleItemClick}
                /> */}
            </Menu>
    )
}
export default NavBar;
