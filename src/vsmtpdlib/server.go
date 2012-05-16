//
// src/vsmtpdlib/server.go
//

package vsmtpdlib

import (
    "net"
)

type Server struct {
    listener *net.TCPListener
}

func NewServer() (*Server, error) {
    server := new(Server)

    return server, nil
}

func (server *Server) Start() error {

    addr, err := net.ResolveTCPAddr("tcp", ":2500")
    if err != nil {
        return err
    }

    server.listener, err = net.ListenTCP("tcp", addr)
    if err != nil {
        return err
    }

    defer server.listener.Close()

    for {
        c, err := server.listener.AcceptTCP()
        if err != nil {
            continue
        }

        conn, err := NewConnection(c)
        if err != nil {
            continue
        }
        go conn.Handle()
    }

    return nil
}
