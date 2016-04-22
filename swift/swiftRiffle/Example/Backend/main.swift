//
//  main.swift
//  Backend
//
//  Created by damouse on 3/7/16.
//  Copyright © 2016 CocoaPods. All rights reserved.
//

import Riffle

// Required helper method for OSX backends
initTypes(External(String.self, String.self), External(Int.self, Int.self), External(Double.self, Double.self), External(Float.self, Float.self), External(Bool.self, Bool.self))

Riffle.setLogLevelDebug()
Riffle.setFabricDev()

//// This is faking two seperate connections by creating another top level domain
//// Not intended for regular use
//let app = Domain(name: "xs.tester")
//let receiver = Receiver(name: "receiver", superdomain: app)
//
//let app2 = Domain(name: "xs.tester")
//let sender2 = Sender(name: "sender", superdomain: app2)
//let receiver2 = Receiver(name: "receiver", superdomain: app2)
//
//sender2.receiver = receiver2
//
//receiver.joinFinished = {
//    sender2.join()
//}
//
//receiver.join()
//
NSRunLoop.currentRunLoop().run()
