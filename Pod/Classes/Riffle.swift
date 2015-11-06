//
//  Riffle.swift
//  Pods
//
//  Created by Mickey Barboi on 9/25/15.
//
//

import Foundation

var NODE = "wss://node.exis.io:8000/wss"

public let rifflog = RiffleLogger()

// Sets itself as the delegate if none provided
@objc public protocol RiffleDelegate {
    func onJoin()
    func onLeave()
}


// Seting URL-- Better to use a singleton.
public func setFabric(url: String) {
    NODE = url
}


// Base connection for all agents connecting to a fabric
class RiffleConnection: NSObject, MDWampClientDelegate {
    var agents: [RiffleAgent] = []
    
    var open = false
    var opening = false
    
    var socket: MDWampTransportWebSocket?
    var session: MDWamp?

    
    func mdwamp(wamp: MDWamp!, sessionEstablished info: [NSObject : AnyObject]!) {
        if !open { _ = agents.map { $0.delegate?.onJoin() } }
        open = true
        opening = false
    }
    
    func mdwamp(wamp: MDWamp!, closedSession code: Int, reason: String!, details: [NSObject : AnyObject]!) {
        if open { _ = agents.map { $0.delegate?.onLeave() } }
        open = false
        opening = false
    }
    
    func addAgent(agent: RiffleAgent) {
        
        if agents.contains(agent) {
            print("Agent \(agent.domain) is already connected.")
            return
        }
        
        agents.append(agent)
        
        if open {
            agent.delegate?.onJoin()
        }
    }
    
    func connect(agent: RiffleAgent, token: String?) {
        
        if !open && !opening {
            socket = MDWampTransportWebSocket(server:NSURL(string: NODE), protocolVersions:[kMDWampProtocolWamp2msgpack, kMDWampProtocolWamp2json])
            session = MDWamp(transport: socket, realm: agent.domain, delegate: self)
            
            if let t = token {
                session!.token = t
            }
            
            rifflog.debug("Opening new session.")
            session!.connect()
            opening = true
        } else {
            print("Cant connection. Connection open: \(open), opening: \(opening)")
        }
    }
    
    func removeAgent(agent: RiffleAgent) {
        if !agents.contains(agent) {
            print("Agent \(agent.domain) is not connected.")
            return
        }
        
        // remove agent from array
    }
}

public class RiffleAgent: NSObject, RiffleDelegate {
    public var domain: String
    public var delegate: RiffleDelegate?
    
    var connection: RiffleConnection
    var superdomain: RiffleAgent?
    
    var registrations: [String] = []
    var subscriptions: [String] = []
    
    
    // MARK: Initialization
    public init(domain d: String) {
        // Initialize this agent as the Application domain, or the root domain
        // for this instance of the application
        
        domain = d
        connection = RiffleConnection()
        
        super.init()
        unowned let weakSelf = self
        delegate = weakSelf
    }
    
    public init(name: String, superdomain: RiffleAgent) {
        // Initialize this agent as a subdomain of the given domain. Does not
        // connect. If "connect" is called on either the superdomain or this domain
        // both will be connected
        
        domain = superdomain.domain + "." + name
        connection = superdomain.connection
        
        super.init()
        delegate = self
        unowned let weakSelf = self
        connection.addAgent(weakSelf)
    }
    
    deinit {
        rifflog.debug("\(domain) going down")
        //self.leave()
    }
    
    public func join(token: String? = nil) -> RiffleAgent {
        // Connect this agent and any agents connected to this one
        // superdomains and subdomains
        
        unowned let weakSelf = self
        connection.addAgent(weakSelf)
        
        if superdomain != nil && superdomain!.connection.open {
            superdomain!.join()
        } else {
            connection.connect(weakSelf, token: token)
        }
        
        return self
    }
    
    public func leave() {
        _ = registrations.map { self.unregister($0) }
        _ = subscriptions.map { self.unsubscribe($0) }
    }
    
    
    // MARK: Real Calls
    func _subscribe(action: String, fn: ([AnyObject]) throws -> ()) {
        let endpoint = makeEndpoint(action)
        rifflog.debug("\(domain) SUB: \(endpoint)")
        
        connection.session!.subscribe(endpoint, onEvent: { (event: MDWampEvent!) -> Void in
            do {
                try fn(event.arguments)
            } catch CuminError.InvalidTypes(let expected, let recieved) {
                rifflog.warn(": cumin unable to convert: expected \(expected) but received \"\(recieved)\"[\(recieved.dynamicType)] for function \(fn) subscribed at endpoint \(endpoint)")
            } catch {
                rifflog.panic(" Unknown exception!")
            }
            
            })
        { (err: NSError!) -> Void in
            if let e = err {
                print("An error occured: ", e)
            } else {
                self.subscriptions.append(endpoint)
            }
        }
    }
    
    func _register(action: String, fn: ([AnyObject]) throws -> ()) {
        let endpoint = makeEndpoint(action)
        rifflog.debug("\(domain) REG: \(endpoint)")
        
        connection.session!.registerRPC(endpoint, procedure: { (wamp: MDWamp!, invocation: MDWampInvocation!) -> Void in
            
            rifflog.debug("INVOCATION: \(endpoint)")
            
            do {
                try fn(invocation.arguments)
            } catch CuminError.InvalidTypes(let expected, let recieved) {
                rifflog.warn(": cumin unable to convert: expected \(expected) but received \"\(recieved)\"[\(recieved.dynamicType)] for function \(fn) registered at endpoint \(endpoint)")
            } catch {
                rifflog.panic(" Unknown exception!")
            }
            
            wamp.resultForInvocation(invocation, arguments: [], argumentsKw: [:])
            
            }, cancelHandler: { () -> Void in
                print("Register Cancelled!")
            })
        { (err: NSError!) -> Void in
            if err != nil {
                print("Error registering endoint: \(endpoint), \(err)")
            } else {
                self.registrations.append(endpoint)
            }
        }
    }
    
    func _register<R>(action: String, fn: ([AnyObject]) throws -> (R)) {
        let endpoint = makeEndpoint(action)
        rifflog.debug("\(domain) REG: \(endpoint)")
        
        connection.session!.registerRPC(endpoint, procedure: { (wamp: MDWamp!, invocation: MDWampInvocation!) -> Void in
            var result: R?
            
            rifflog.debug("INVOCATION: \(endpoint)")
            
            do {
                result = try fn(invocation.arguments)
            } catch CuminError.InvalidTypes(let expected, let recieved) {
                rifflog.warn(": cumin unable to convert: expected \(expected) but received \"\(recieved)\"[\(recieved.dynamicType)] for function \(fn) registered at endpoint \(endpoint)")
                result = nil
            } catch {
                rifflog.panic(" Unknown exception!")
            }
            
            if let autoArray = result as? [AnyObject] {
                wamp.resultForInvocation(invocation, arguments: serialize(autoArray), argumentsKw: [:])
            } else {
                wamp.resultForInvocation(invocation, arguments: serialize([result as! AnyObject]), argumentsKw: [:])
            }
            
            }, cancelHandler: { () -> Void in
                print("Register Cancelled!")
            })
        { (err: NSError!) -> Void in
            if err != nil {
                print("Error registering endoing: \(endpoint), \(err)")
            } else {
                self.registrations.append(endpoint)
            }
        }
    }
    
    func _call(action: String, args: [AnyObject], fn: (([AnyObject]) throws -> ())?) {
        let endpoint = makeEndpoint(action)
        rifflog.debug("\(domain) CALL: \(endpoint)")
        
        connection.session!.call(endpoint, payload: serialize(args)) { (result: MDWampResult!, err: NSError!) -> Void in
            if err != nil {
                print("Call Error for endpoint \(endpoint): \(err)")
            }
            else {
                if let h = fn {
                    do {
                        //rifflog.debug("Arguments for call: \(result.arguments.count)")
                        try h(result.arguments == nil ? [] : result.arguments)
                    } catch CuminError.InvalidTypes(let expected, let recieved) {
                        rifflog.warn(": cumin unable to convert: expected \(expected) but received \"\(recieved)\"[\(recieved.dynamicType)] for function \(fn) subscribed at endpoint \(endpoint)")
                    } catch {
                        rifflog.panic(" Unknown exception!")
                    }
                    
                }
            }
        }
    }
    
    public func publish(action: String, _ args: AnyObject...) {
        let endpoint = makeEndpoint(action)
        rifflog.debug("\(domain) PUB: \(endpoint)")
        
        connection.session!.publishTo(endpoint, args: serialize(args), kw: [:], options: [:]) { (err: NSError!) -> Void in
            if let e = err {
                print("Error: ", e)
                print("Publish Error for endpoint \"\(endpoint)\": \(e)")
            }
        }
    }
    
    public func unregister(action: String) {
        let endpoint = makeEndpoint(action)
        rifflog.debug("\(domain) UNREG: \(endpoint)")
        
        connection.session!.unregisterRPC(endpoint) { (err: NSError!) -> Void in
            if err != nil {
                print("Error unregistering endoint: \(endpoint), \(err)")
            } else {
                self.registrations.removeObject(endpoint)
            }
        }
    }
    
    public func unsubscribe(action: String) {
        let endpoint = makeEndpoint(action)
        rifflog.debug("\(domain) UNSUB: \(endpoint)")
        
        connection.session!.unsubscribe(endpoint) { (err: NSError!) -> Void in
            if err != nil {
                print("Error unsubscribing endoint: \(endpoint), \(err)")
            } else {
                self.subscriptions.removeObject(endpoint)
            }
        }
    }
    
    
    // MARK: Delegate Calls
    public func onJoin() {
        
    }
    
    public func onLeave() {
        
    }
    
    
    // MARK: Utilities
    func makeEndpoint(action: String) -> String {
        if action.containsString("xs.") {
            return action
        }
        
        return domain + "/" + action
    }
}


extension RangeReplaceableCollectionType where Generator.Element : Equatable {
    
    // Remove first collection element that is equal to the given `object`:
    mutating func removeObject(object : Generator.Element) {
        if let index = self.indexOf(object) {
            self.removeAtIndex(index)
        }
    }
}
