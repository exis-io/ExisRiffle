//
//  Utils.swift
//  RiffleTest
//
//  Created by damouse on 12/9/15.
//  Copyright © 2015 exis. All rights reserved.
//

import Foundation
import CoreFoundation
import Mantle

extension String {
    func cString() -> UnsafeMutablePointer<Int8> {
        var ret: UnsafeMutablePointer<Int8> = UnsafeMutablePointer<Int8>()
        
        self.withCString { p in
            var c = 0
            while p[c] != 0 {
                c += 1
            }
            c += 1
            let a = UnsafeMutablePointer<Int8>.alloc(c)
            a.initialize(0)
            for i in 0..<c {
                a[i] = p[i]
            }
            a[c-1] = 0
            ret = a
        }
        
        return ret
    }
}

// Decode arbitrary returns from the mantle
func decode(p: UnsafePointer<Int8>) -> (UInt64, [Any]) {
    let dataString = String.fromCString(p)!
    
    guard let data = try! JSONParser.parse(dataString) as? [Any] else {
        print("DID NOT RECEIVE ARRAY BACK!")
        return (UInt64(0), [])
    }
    
    if let args = data[1] as? [Any] {
        return (UInt64(data[0] as! Double), args)
    } else {
        return (UInt64(data[0] as! Double), [])
    }
}

// Marshalls some set of arguments into Json, then a c string for core consumption
func marshall(args: [Any]) -> UnsafeMutablePointer<Int8> {
    let json = JSON.from(args)
    let jsonString = json.serialize(DefaultJSONSerializer())
    //print("Args: \(args) Json: \(json) String: \(jsonString)")
    return jsonString.cString()
}

// Do we still need this here? D
func serializeArguments(args: [Any]) -> [Any] {
    var ret: [Any] = []
    
    for a in args {
        if let arg = a as? Property {
            ret.append(arg.serialize())
        }
    }
    
    return ret
}

func serializeArguments(args: [Property]) -> [Any] {
    //    Riffle.debug("Serializing: \(args.dynamicType) \(args)")
    //    return args.map { $0.serialize() }
    
    #if os(OSX)
        let c =  args.map { $0.unsafeSerialize() }
        return c
    #else
        return args.map { $0.serialize() }
    #endif
}


// Technically this is part of the generic shotgun-- please merge
// Convert any kind of handler return to an array of Any
func serializeResults(args: ()) -> [Any] {
    return []
}

func serializeResults<A: PR>(args: (A)) -> [Any] {
    return [args.serialize()]
}

func serializeResults<A: PR, B: PR>(args: (A, B)) -> [Any] {
    return [args.0.serialize(), args.1.serialize()]
}

func serializeResults<A: PR, B: PR, C: PR>(args: (A, B, C)) -> [Any] {
    return [args.0.serialize(), args.1.serialize(), args.2.serialize()]
}

func serializeResults<A: PR, B: PR, C: PR, D: PR>(args: (A, B, C, D)) -> [Any] {
    return [args.0.serialize(), args.1.serialize(), args.2.serialize(), args.3.serialize()]
}

func serializeResults<A: PR, B: PR, C: PR, D: PR, E: PR>(args: (A, B, C, D, E)) -> [Any] {
    return [args.0.serialize(), args.1.serialize(), args.2.serialize(), args.3.serialize(), args.4.serialize()]
}

func serializeResults(results: Property...) -> Any {
    // Swift libraries are not technically supported on OSX targets-- Swift gets linked against twice
    // Functionally this means that type checks in either the library or the app fail when the
    // type originates on the other end
    // This method switches app types back to library types by checking type strings. Only runs on OSX
    
    #if os(OSX)
        return results.map { $0.unsafeSerialize() }
    #else
        return results
    #endif
}

func switchTypes<A>(x: A) -> Any {
    // Converts app types to riffle types because of the osx bug (see above)
    
    #if os(OSX)
        // return recode(x, switchTypeObject(x))
        switch "\(x.dynamicType)" {
        case "Int":
            return recode(x, Int.self)
        case "String":
            return recode(x, String.self)
        case "Double":
            return recode(x, Double.self)
        case "Float":
            return recode(x, Float.self)
        case "Bool":
            return recode(x, Bool.self)
        default:
            Riffle.warn("Unable to switch o/Applications/Utilities/Script Editor.apput app type: \(x.dynamicType)")
            return x
        }
    #else
        return x
    #endif
}

func switchTypeObject<A>(x: A) -> Any.Type {
    // Same as the function above, but operates on types
    // Converts app types to riffle types because of the osx bug (see above)
    
    #if os(OSX)
        switch "\(x)" {
        case "Int":
            return Int.self
        case "String":
            return String.self
        case "Double":
            return Double.self
        case "Float":
            return Float.self
        case "Bool":
            return Bool.self
        default:
            Riffle.warn("Unable to switch out type object: \(x)")
            return x as! Any.Type
        }
    #else
        return x as! Any.Type
    #endif
}

func encode<A>(var v:A) -> NSData {
    // Returns the bytes from a swift variable
    return withUnsafePointer(&v) { p in
        // print("Original: \(p), type: \(A.self), size: \(strideof(A.self))")
        return NSData(bytes: p, length: strideof(A))
    }
}


func recode<A, T>(value: A, _ t: T.Type) -> T {
    // encode and decode a value, magically transforming its type to the appropriate version
    // This is a workaround for OSX crap, again
    
    // print("From \(A.self) \(value) to \(T.self)")
    
    if T.self == Bool.self {
        func encodeBool<A>(var v:A) -> Bool {
            // Returns the bytes from a swift variable
            return withUnsafePointer(&v) { p in
                let s = unsafeBitCast(p, UnsafePointer<Bool>.self)
                
                return s.memory == true
            }
        }
        
        return encodeBool(value) as! T
    }
    
    if T.self == String.self  {
        
        // Grab the pointer, copy out the bytes into a new string, and return it
        func encodeString<A>(var v:A) -> String {
            return withUnsafePointer(&v) { p in
                let s = unsafeBitCast(p, UnsafePointer<String>.self)
                
                let dat = s.memory.dataUsingEncoding(NSUTF8StringEncoding)!
                let ret = NSString(data: dat, encoding: NSUTF8StringEncoding)
                
                return ret as! String
            }
        }
        
        let r = encodeString(value)
        return r as! T
    }
    
    // copy the value as to not disturb the original
    let copy = value
    let data = encode(copy)
    
    let pointer = UnsafeMutablePointer<T>.alloc(sizeof(T.Type))
    
    data.getBytes(pointer)
    return pointer.move()
}


// Makes configuration calls a little cleaner when accessed from the top level
// as well as keeping them all in one place
public class Riffle {
    public class func setFabric(url: String) {
        sendCore("Fabric", [url])
    }
    
    public class func application(s: String){
        sendCore("MantleApplication", [s])
    }
    
    public class func debug(s: String){
        sendCore("MantleDebug", [s])
    }
    
    public class func info(s: String){
        sendCore("MantleInfo", [s])
    }
    
    public class func warn(s: String){
        sendCore("MantleWarn", [s])
    }
    
    public class func error(s: String){
        sendCore("MantleError", [s])
    }
    
    public class func setLogLevelApp() { sendCore("SetLogLevelApp", [])  }
    public class func setLogLevelOff() { sendCore("SetLogLevelOff", [])  }
    public class func setLogLevelErr() { sendCore("SetLogLevelErr", [])  }
    public class func setLogLevelWarn() { sendCore("SetLogLevelWarn", [])  }
    public class func setLogLevelInfo() { sendCore("SetLogLevelInfo", [])  }
    public class func setLogLevelDebug() { sendCore("SetLogLevelDebug", [])  }
    
    public class func setFabricDev() { sendCore("SetFabricDev", []) }
    public class func setFabricSandbox() { sendCore("SetFabricSandbox", []) }
    public class func setFabricProduction() { sendCore("SetFabricProduction", []) }
    public class func setFabricLocal() { sendCore("SetFabricLocal", []) }
    
    public class func setCuminStrict() { sendCore("SetCuminStrict", []) }
    public class func setCuminLoose() { sendCore("SetCuminLoose", []) }
    public class func setCuminOff() { sendCore("SetCuminOff", []) }
}




// Create CBIDs on this side of the boundary. Note this makes them doubles, should be using byte arrays or
// uint64
// TODO: Use this but convert to byte slices first
//// Biggest random number that can be choosen
//let randomMax = UInt32(pow(Double(2), Double(32)) - 1)
//
//func CBID() -> Double {
//    // Create a random callback id
//    let r = arc4random_uniform(randomMax);
//    return Double(r)
//}
//
//// Hahahahah. No.
//// Pass bytes and avoid this nonsense.
//extension Double {
//    func go() -> String {
//        return String(UInt64(self))
//    }
//}

