import React, { Component } from "react";

class LoginComponent extends Component {

    constructor(props) {
        super(props);
        this.state = {
            username: '',
            password: ''
        };
    }

    handleUsernameChange = (e) => {
        const { value } = e.target;
    this.setState({username: value})
    };

    handlePasswordChange = (e) => {
        const { value } = e.target;
        this.setState({password: value})
    };

    handleLoginSubmit = (e) => {
        e.preventDefault();
        this.props.handleLoginSubmit({...this.state});
    };

    render() {
        const { username, password } = this.state
        return (
            <div className="login-container frosty">
                <form onSubmit={(e) => this.handleLoginSubmit(e)}>
                <div className="label-container">
                    <label>Username:</label>
                </div>
                <input 
                    type="text" 
                    value={username}
                    placeholder="Type your admin username" 
                    onChange={(e) => this.handleUsernameChange(e)} 
                />
                <div className="label-container">
                    <label>Password:</label>
                </div>
                <input
                    type="password"
                    placeholder="Type your admin password"
                    value={password}
                    onChange={(e) => this.handlePasswordChange(e)}
                    />
                <br />
                <button className="login-button" type="submit">Login</button>
            </form>
            </div>
        );
    }
};

export default LoginComponent;