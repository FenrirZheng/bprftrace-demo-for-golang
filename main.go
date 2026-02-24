package main

import (
	"fmt"
	"time"
)

func Multiply(a int, b int) int {
	c := b*2 + a
	return c
}

//go:noinline  // <--- 非常重要！這告訴編譯器不要把這個函數內聯 (inline)
func Calculate(a int, b int) {
	c := Multiply(a, b*2)
	fmt.Printf("正在計算... %d + %d + %d \n", a, b, c)
}

func main() {
	for i := 1; ; i++ {
		Calculate(i, i*10)
		time.Sleep(2 * time.Second)
	}
}
