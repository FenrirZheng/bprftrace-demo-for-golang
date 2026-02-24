package service

import (
	"fmt"
	"net/http"
)

//go:noinline
func HandleHello(name string) string {
	if name == "" {
		return "Hello, World!"
	}
	return fmt.Sprintf("Hello, %s!", name)
}

type CC struct {
	index int
	name  string
}

//go:noinline
func inputStruct(cc CC) string {
	if cc.name == "" {
		return "Hello, World!"
	}
	return fmt.Sprintf("Hello, %s!", cc.name)
}

//go:noinline
func inputPtr(cc *CC) string {
	if cc.name == "" {
		return "Hello, World!"
	}
	return fmt.Sprintf("Hello, %s!", cc.name)
}

func Hello(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	result := HandleHello(name)
	fmt.Fprint(w, result)
}

func HelloStruct(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	result := inputStruct(CC{index: 1, name: name})
	fmt.Fprint(w, result)
}

func HelloPtr(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	c := CC{index: 1, name: name}
	result := inputPtr(&c)
	fmt.Fprint(w, result)
}
