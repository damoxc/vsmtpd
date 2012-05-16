//
// src/vsmtpdlib/transaction.go

package vsmtpdlib

type spool struct {
    pos   int
    buf []byte
    file *os.File
}

type Transaction struct {
    connection  *Connection
    sender      *Address
    spool       *Spool
}

func NewTransaction() *Transaction {
    return new(Transaction)
}

// Return the Connection that this transaction belongs to
func (t *Transaction) Connection() *Connection {
    return t.connection
}


