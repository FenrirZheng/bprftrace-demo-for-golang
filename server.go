package main

import (
	"bprf_demo/service"
	"fmt"
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("/hello", service.Hello)

	http.HandleFunc("/hello/struct", service.HelloStruct)
	http.HandleFunc("/hello/ptr", service.HelloPtr)
	fmt.Println("Server starting on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
