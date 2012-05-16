//
// src/vsmtpd/main.go
//

package main

import (
    "log"
    "vsmtpdlib"
)

func main() {
    server, err := vsmtpdlib.NewServer()
    if err != nil {
        log.Print(err)
        return
    }

    log.Print("Starting smtp server")

    err = server.Start()
    log.Print("error:", err)
}
