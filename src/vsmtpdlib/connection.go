//
// src/vsmtpdlib/connection.go
//

package vsmtpdlib

import (
    "bufio"
    "fmt"
    "io"
    "log"
    "net"
    "os"
    "strings"
)

const (
    STATE_NONE    = 1
    STATE_COMMAND = 2
    STATE_DATA    = 3
    STATE_AUTH    = 4
)

type Connection struct {
    conn     *net.TCPConn
    file     *os.File
    rdr      *bufio.Reader
    wtr      *bufio.Writer
    state     int
    hello     string
    helloHost string
    lHost     string
    rHost     string
}

type SMTPResponse struct {
    Code       int
    Message    string
    Error      error
    Disconnect bool
}

var SyntaxError = &SMTPResponse{
    Code:    500,
    Message: "Error: bad syntax",
}

var InternalError = &SMTPResponse{
    Code:    451,
    Message: "Internal error - try again later",
}

func getFqdn(ip net.IP) string {
    name, err := net.LookupAddr(ip.String())
    if err != nil {
        return ""
    }

    if len(name) == 0 {
        return ""
    }
    return name[0]
}

func NewConnection(c *net.TCPConn) (*Connection, error) {
    conn := new(Connection)
    conn.conn = c
    conn.state = STATE_NONE

    f, err := c.File()
    if err != nil {
        return nil, err
    }
    conn.file = f
    conn.rdr = bufio.NewReader(f)
    conn.wtr = bufio.NewWriter(f)

    laddr := c.LocalAddr().(*net.TCPAddr)
    conn.lHost = getFqdn(laddr.IP)

    raddr := c.RemoteAddr().(*net.TCPAddr)
    conn.rHost = getFqdn(raddr.IP)

    return conn, nil
}

// Returns the verb used to say helo by the client
func (c *Connection) Hello() string {
    return c.hello
}

// Returns the hostname provided by the the client
func (c *Connection) HelloHost() string {
    return c.helloHost
}

// Returns the hostname (either actual or helo_host) for the server
func (c *Connection) Hostname() string {
    return c.lHost
}

// Returns the server hostname for the connection
func (c *Connection) LocalHost() string {
    return c.lHost
}

// Returns the server IP address for the connection
func (c *Connection) LocalIP() string {
    laddr := c.conn.LocalAddr().(*net.TCPAddr)
    return laddr.IP.String()
}

// Returns the server port for the connection
func (c *Connection) LocalPort() int {
    laddr := c.conn.LocalAddr().(*net.TCPAddr)
    return laddr.Port
}

// Returns the client hostname for the connection
func (c *Connection) RemoteHost() string {
    return c.rHost
}

// Returns the client IP address for the connection
func (c *Connection) RemoteIP() string {
    raddr := c.conn.RemoteAddr().(*net.TCPAddr)
    return raddr.IP.String()
}

// Returns the client port for the connection
func (c *Connection) RemotePort() int {
    raddr := c.conn.RemoteAddr().(*net.TCPAddr)
    return raddr.Port
}

func (c *Connection) Transaction() *Transaction {
    return nil
}

func (c *Connection) Close() error {
    log.Print("Testing testing, 1, 2, 3")
    return nil
}

func (c *Connection) Handle() error {
    log.Print("Handling connection from ", c.conn.RemoteAddr())
    c.state = STATE_COMMAND
    c.SendCode(220, "smtp.uk-plc.net ESMTP")

    buffer := ""

    defer log.Print("Connection from ", c.conn.RemoteAddr(), " ended")
    defer c.file.Close()
    defer c.conn.Close()

MAIN: for {
        line, isPrefix, err := c.rdr.ReadLine()
        if err != nil {
            if err != io.EOF {
                log.Print(err)
            }
            return err
        }

        buffer += string(line)

        if isPrefix {
            continue
        }

        switch c.state {
            case STATE_AUTH:
                c.HandleAuth(buffer)
            case STATE_COMMAND:
                resp := c.HandleCommand(buffer)
                c.SendResponse(resp)
                if resp.Disconnect {
                    break MAIN
                }
            case STATE_DATA:
                c.HandleData(buffer)
        }
        buffer = ""
    }

    return nil
}

func (c *Connection) HandleCommand(line string) *SMTPResponse {
    line = strings.TrimSpace(line)

    if line == "" {
        return SyntaxError
    }

    parts := strings.SplitN(line, " ", 2)
    command := parts[0]

    rest := ""
    if len(parts) == 2 {
        rest = parts[1]
    }

    resp, err := DispatchCommand(c, command, rest)
    if err != nil {
        log.Print(err)
        return InternalError
    }

    if resp == nil {
        return InternalError
    }
    return resp
}

func (c *Connection) HandleData(line string) *SMTPResponse {
    log.Print(line)
    return nil
}

func (c *Connection) HandleAuth(line string) *SMTPResponse {
    log.Print(line)
    return nil
}

func (c *Connection) SendCode(code int, message string) error {
    return c.SendResponse(&SMTPResponse{Code: code, Message: message})
}

func (c *Connection) SendResponse(r *SMTPResponse) error {

    if r == nil {
        return nil
    }

    lines := strings.Split(r.Message, "\n")

    lineCount := len(lines) - 1
    for i, line := range lines {
        if i == lineCount {
            c.sendLine(fmt.Sprintf("%3.3d %s", r.Code, line))
        } else {
            c.sendLine(fmt.Sprintf("%3.3d-%s", r.Code, line))
        }
    }
    return nil
}

func (c *Connection) sendLine(line string) error {
    c.wtr.WriteString(line + "\r\n")
    c.wtr.Flush()
    log.Print(line)
    return nil
}
