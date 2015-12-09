// package name: riffle
package main

import (
	"C"
    "fmt"
    "unsafe"
    "encoding/json"

	"github.com/exis-io/core"
	"github.com/exis-io/core/goRiffle"
)

/*
This is the lowest level core, just exposes the C API. Used for python, swift-linux, and osx.

You are responsible for cleaning up C references!


Every function here is reactive: it returns two indicies to callbacks to be triggered later.
*/


type mantle struct {
	app   core.App
	conn *goRiffle.WebsocketConnection
    recv chan []byte
}

var man = new(mantle)

// Required main method
func main() {}

//export NewDomain
func NewDomain(name *C.char) unsafe.Pointer {
	if man.app == nil {
		man.app = core.NewApp()
	}

	d := man.app.NewDomain(C.GoString(name), man)

    return unsafe.Pointer(&d)
}


//export Subscribe
func Subscribe(pdomain unsafe.Pointer, endpoint *C.char) []byte {
    d := *(*core.Domain)(pdomain)
    cb, eb := core.NewID(), core.NewID()

    go func() {
        d.Subscribe(C.GoString(endpoint), cb, make([]interface{}, 0))
    }()

    return marshall([]uint{cb, eb})
}

//export Register
func Register(pdomain unsafe.Pointer, endpoint *C.char)  {
    d := *(*core.Domain)(pdomain)
    cb, _ := core.NewID(), core.NewID()

    go func() {
        d.Register(C.GoString(endpoint), cb, make([]interface{}, 0))
    }()
}

//export Yield
func Yield(args []byte) {
    // core.Yield(C.GoString(e))
}

//export Publish
func Publish(pdomain unsafe.Pointer, endpoint *C.char) {
    d := *(*core.Domain)(pdomain)
    cb, _ := core.NewID(), core.NewID()

    go func() {
        d.Publish(C.GoString(endpoint), cb, make([]interface{}, 0))
    }()
}

//export Call
func Call(pdomain unsafe.Pointer, endpoint *C.char) {
    d := *(*core.Domain)(pdomain)
    cb, _ := core.NewID(), core.NewID()

    go func() {
        d.Call(C.GoString(endpoint), cb, make([]interface{}, 0))
    }()
}

//export Unsubscribe
func Unsubscribe(pdomain unsafe.Pointer, e *C.char) {
    d := *(*core.Domain)(pdomain)
    d.Unsubscribe(C.GoString(e))
}

//export Unregister
func Unregister(pdomain unsafe.Pointer, e *C.char) {
    d := *(*core.Domain)(pdomain)
    d.Unregister(C.GoString(e))
}

//export Join
func Join(pdomain unsafe.Pointer) {
    d := *(*core.Domain)(pdomain)
    
    if man.conn != nil {
        fmt.Println("Connection is already open!")
    }

    if c, err := goRiffle.Open(core.SandboxFabric); err != nil {
        core.Warn("Unable to open connection! Err: %s", err.Error())
    } else {
        man.conn = c
        d.Join(c)
    }
}

//export Leave
func Leave(pdomain unsafe.Pointer, ) {
    d := *(*core.Domain)(pdomain)
    d.Leave()
}

//export Recieve
func Recieve() []byte {
    data := <- man.recv
    return data
}

func marshall(data interface{}) []byte {
    if r, e := json.Marshal(data); e == nil {
        return r
    } else {
        fmt.Println("Unable to marshall data!")
        return nil 
    }
}

func unmarshall() {

}

// Unexported Functions
func (m mantle) Invoke(id uint, args []interface{}){
    fmt.Println("Invoke called: ", id, args)

    man.recv <- marshall(map[string]interface{}{
        "id": id, 
        "args": args,
    })
}

func (m mantle) OnJoin(string) {
    fmt.Println("Domain joined!")
}

func (m mantle) OnLeave(string) {
    fmt.Println("Domain left!")
}

// export Hello
// func Hello(pdomain unsafe.Pointer) {
//     // Testing returning go callbacks into the C bridge
//     d := *(*domain)(pdomain)
//     d.hello()
// }

// func (d *domain) hello() {
//     fmt.Println(d.name + " called from swift!")
// }

