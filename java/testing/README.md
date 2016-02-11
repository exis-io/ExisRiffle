
# Testing and Experimental 

## TODO

Java with Core 

- Check all type passing
- Verify object passing
- Create JAR or AAR from mantle and crust
- Upload jar/aar to maven or jcentral
- Make sure jnr-ffi can import on ARM

Problems

- 1.8 vs 1.7 incompatabilities when importing the backend

Closures

- Generics dont work. Object casting does, but this abandons type safety


## Getting GO to build DLLs on Windows 

- Download patch
- Bootstrapped off existing install (but could possible also patch it in)


## Building Java backends from command line

- Make sure the gradle wrapper exists: 'gradle wrapper' at root
- Create a new module as a java library
- Apply plugin "application" and set the main class
- Run ./gradlew run -p [MODULENAME]

Optional note: to import model objects to both sides, put them in the backend! Cant import
 the android app into the backend
 