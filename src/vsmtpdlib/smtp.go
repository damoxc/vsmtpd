//
// src/vsmtpdlib/smtp.go
//

package vsmtpdlib

import (
    "fmt"
    "strings"
)

var smtpCommands = map[string] func(*Connection, string) (*SMTPResponse, error) {
    "helo": Helo,
    "ehlo": Ehlo,
    "mail": Mail,
    "rcpt": Rcpt,
    "data": Data,
    "rset": Rset,
    "vrfy": Vrfy,
    "quit": Quit,
}

func DispatchCommand(c *Connection, name, rest string) (*SMTPResponse, error) {
    name = strings.ToLower(name)
    handler := smtpCommands[name]
    if handler == nil {
        return nil, fmt.Errorf("no command %q exists", name)
    }
    return handler(c, rest)
}

// Add a command to the SMTP command handler. This is used to simplify extending
// vsmtpd.
func RegisterCommand(name string, handler func(*Connection, string) (*SMTPResponse, error)) error {
    name = strings.ToLower(name)
    cmd := smtpCommands[name]
    if cmd != nil {
        return fmt.Errorf("command %q already exists", name)
    }

    smtpCommands[name] = handler
    return nil
}

func Helo(c *Connection, rest string) (*SMTPResponse, error) {
    if c.Hello() != "" {
        return &SMTPResponse{Code: 503, Message: "But you already said HELO..."}, nil
    }
    c.hello = "helo"
    c.helloHost = rest
    return &SMTPResponse{
        Code:    250,
        Message: fmt.Sprintf("%s Hi %s [%s]; I am so happy to meet you.",
                             c.Hostname(), c.RemoteHost(), c.RemoteIP()),
    }, nil
}

func Ehlo(c *Connection, rest string) (*SMTPResponse, error) {

    if c.Hello() != "" {
        return &SMTPResponse{Code: 503, Message: "But you already said HELO..."}, nil
    }

    c.hello = "ehlo"
    c.helloHost = rest

    args := []string{"SIZE 25000000"}

    return &SMTPResponse{
        Code:    250,
        Message: fmt.Sprintf("%s Hi %s [%s]; I am so happy to meet you.\n",
                             c.Hostname(), c.RemoteHost(), c.RemoteIP()) + strings.Join(args, "\n"),
    }, nil
}

func Mail(c *Connection, rest string) (*SMTPResponse, error) {

    // We don't want anyone who hasn't identified themselves starting a transaction
    if c.Hello() == "" {
        return &SMTPResponse{Code: 503, Message: "Manners? You haven't said hello..."}, nil
    }

    return &SMTPResponse{
        Code:    250,
        Message: fmt.Sprintf("%s sender OK - how exciting to get mail from you!", rest),
    }, nil
}

func Rcpt(c *Connection, rest string) (*SMTPResponse, error) {
    if c.Hello() == "" {
        return &SMTPResponse{Code: 503, Message: "Use MAIL before RCPT"}, nil
    }
    return &SMTPResponse{Code: 550, Message: "Relaying denied"}, nil
}

func Data(c *Connection, rest string) (*SMTPResponse, error) {
    c.state = STATE_DATA
    return &SMTPResponse{Code: 354, Message: "go ahead"}, nil
}

func Vrfy(c *Connection, rest string) (*SMTPResponse, error) {
    return nil, nil
}

func Rset(c *Connection, rest string) (*SMTPResponse, error) {
    return &SMTPResponse{Code: 250, Message: "OK"}, nil
}

func Quit(c *Connection, rest string) (*SMTPResponse, error) {
    return &SMTPResponse{
        Code:       221,
        Message:    fmt.Sprintf("%s closing connection. Have a wonderful day.", c.Hostname()),
        Disconnect: true,
    }, nil
}
