// File generated by github.com/ungerik/pkgreflect
package core

import "reflect"

var Types = map[string]reflect.Type{
	"App": reflect.TypeOf((*App)(nil)).Elem(),
	"Callback": reflect.TypeOf((*Callback)(nil)).Elem(),
	"Connection": reflect.TypeOf((*Connection)(nil)).Elem(),
	"Domain": reflect.TypeOf((*Domain)(nil)).Elem(),
	"IdGenerator": reflect.TypeOf((*IdGenerator)(nil)).Elem(),
	"InvalidURIError": reflect.TypeOf((*InvalidURIError)(nil)).Elem(),
	"Model": reflect.TypeOf((*Model)(nil)).Elem(),
	"NoDestinationError": reflect.TypeOf((*NoDestinationError)(nil)).Elem(),
	"Serialization": reflect.TypeOf((*Serialization)(nil)).Elem(),
	"Session": reflect.TypeOf((*Session)(nil)).Elem(),
}

var Functions = map[string]reflect.Value{
	"Application": reflect.ValueOf(Application),
	"Cumin": reflect.ValueOf(Cumin),
	"Debug": reflect.ValueOf(Debug),
	"DecodePrivateKey": reflect.ValueOf(DecodePrivateKey),
	"Error": reflect.ValueOf(Error),
	"GetValueOf": reflect.ValueOf(GetValueOf),
	"Info": reflect.ValueOf(Info),
	"MantleApplication": reflect.ValueOf(MantleApplication),
	"MantleCall": reflect.ValueOf(MantleCall),
	"MantleDebug": reflect.ValueOf(MantleDebug),
	"MantleError": reflect.ValueOf(MantleError),
	"MantleInfo": reflect.ValueOf(MantleInfo),
	"MantleMarshall": reflect.ValueOf(MantleMarshall),
	"MantleModel": reflect.ValueOf(MantleModel),
	"MantlePublish": reflect.ValueOf(MantlePublish),
	"MantleRegister": reflect.ValueOf(MantleRegister),
	"MantleSubscribe": reflect.ValueOf(MantleSubscribe),
	"MantleUnmarshal": reflect.ValueOf(MantleUnmarshal),
	"MantleUnmarshalMap": reflect.ValueOf(MantleUnmarshalMap),
	"MantleUnregister": reflect.ValueOf(MantleUnregister),
	"MantleUnsubscribe": reflect.ValueOf(MantleUnsubscribe),
	"MantleWarn": reflect.ValueOf(MantleWarn),
	"NewApp": reflect.ValueOf(NewApp),
	"NewDomain": reflect.ValueOf(NewDomain),
	"NewID": reflect.ValueOf(NewID),
	"NewSession": reflect.ValueOf(NewSession),
	"SetFabricDev": reflect.ValueOf(SetFabricDev),
	"SetFabricLocal": reflect.ValueOf(SetFabricLocal),
	"SetFabricProduction": reflect.ValueOf(SetFabricProduction),
	"SetFabricSandbox": reflect.ValueOf(SetFabricSandbox),
	"SetLogLevelApp": reflect.ValueOf(SetLogLevelApp),
	"SetLogLevelDebug": reflect.ValueOf(SetLogLevelDebug),
	"SetLogLevelErr": reflect.ValueOf(SetLogLevelErr),
	"SetLogLevelInfo": reflect.ValueOf(SetLogLevelInfo),
	"SetLogLevelOff": reflect.ValueOf(SetLogLevelOff),
	"SetLogLevelWarn": reflect.ValueOf(SetLogLevelWarn),
	"SetSession": reflect.ValueOf(SetSession),
	"SignString": reflect.ValueOf(SignString),
	"SoftCumin": reflect.ValueOf(SoftCumin),
	"Warn": reflect.ValueOf(Warn),
}

var Variables = map[string]reflect.Value{
	"CuminLevel": reflect.ValueOf(&CuminLevel),
	"ExternalGenerator": reflect.ValueOf(&ExternalGenerator),
	"Fabric": reflect.ValueOf(&Fabric),
	"LogLevel": reflect.ValueOf(&LogLevel),
	"Registrar": reflect.ValueOf(&Registrar),
	"ShouldLogLineNumber": reflect.ValueOf(&ShouldLogLineNumber),
	"UseUnsafeCert": reflect.ValueOf(&UseUnsafeCert),
}

var Consts = map[string]reflect.Value{
	"Connected": reflect.ValueOf(Connected),
	"CuminLoose": reflect.ValueOf(CuminLoose),
	"CuminOff": reflect.ValueOf(CuminOff),
	"CuminStrict": reflect.ValueOf(CuminStrict),
	"Disconnected": reflect.ValueOf(Disconnected),
	"ErrCloseSession": reflect.ValueOf(ErrCloseSession),
	"ErrInvalidArgument": reflect.ValueOf(ErrInvalidArgument),
	"ErrNoSuchRegistration": reflect.ValueOf(ErrNoSuchRegistration),
	"FabricDev": reflect.ValueOf(FabricDev),
	"FabricLocal": reflect.ValueOf(FabricLocal),
	"FabricProduction": reflect.ValueOf(FabricProduction),
	"FabricSandbox": reflect.ValueOf(FabricSandbox),
	"Leaving": reflect.ValueOf(Leaving),
	"LogLevelApp": reflect.ValueOf(LogLevelApp),
	"LogLevelDebug": reflect.ValueOf(LogLevelDebug),
	"LogLevelErr": reflect.ValueOf(LogLevelErr),
	"LogLevelInfo": reflect.ValueOf(LogLevelInfo),
	"LogLevelOff": reflect.ValueOf(LogLevelOff),
	"LogLevelWarn": reflect.ValueOf(LogLevelWarn),
	"MessageTimeout": reflect.ValueOf(MessageTimeout),
	"Ready": reflect.ValueOf(Ready),
	"RegistrarDev": reflect.ValueOf(RegistrarDev),
	"RegistrarLocal": reflect.ValueOf(RegistrarLocal),
	"RegistrarProduction": reflect.ValueOf(RegistrarProduction),
}

var Interfaces = map[string]reflect.Value{
}

