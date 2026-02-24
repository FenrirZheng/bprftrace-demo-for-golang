# signature 怎麽確立

```shell
nm myapp
nm myserver
```

## 輸出

```shell
0000000000477280 T type:.eq.runtime.workbuf
000000000047d8a0 T type:.eq.sync/atomic.Bool
00000000004800e0 T type:.eq.sync/atomic.Pointer[go.shape.struct { internal/sync.isEntry bool }]
000000000048b880 T type:.eq.sync/atomic.Pointer[internal/bisect.dedup]
000000000048c880 T type:.eq.sync/atomic.Pointer[internal/godebug.value]
0000000000480000 T type:.eq.sync/atomic.Pointer[internal/sync.entry[go.shape.interface {},go.shape.interface {}]]
000000000047fea0 T type:.eq.sync/atomic.Pointer[internal/sync.entry[interface {},interface {}]]
000000000047fd60 T type:.eq.sync/atomic.Pointer[internal/sync.indirect[interface {},interface {}]]
000000000047ff00 T type:.eq.sync/atomic.Pointer[internal/sync.node[interface {},interface {}]]
0000000000490d40 T type:.eq.sync/atomic.Pointer[os.dirInfo]
000000000047fc00 T type:.eq.sync/atomic.Pointer[sync.poolChainElt]
000000000047d8c0 T type:.eq.sync/atomic.Uint32
000000000047d8e0 T type:.eq.sync/atomic.Uint64
000000000047fbe0 T type:.eq.sync.Mutex
000000000047ff20 T type:.eq.sync.Once
000000000047fd40 T type:.eq.sync.poolChain
000000000047fc20 T type:.eq.sync.poolLocal
000000000047fcc0 T type:.eq.sync.poolLocalInternal
00000000005705b0 B unicode.FoldCategory
000000000056afd0 D unicode.foldCommon
000000000056afd8 D unicode.foldGreek
000000000056afe0 D unicode.foldInherited
000000000056afa0 D unicode.foldL
000000000056afa8 D unicode.foldLl
000000000056afb0 D unicode.foldLt
```

# 純計算觀測

## build

```shell
go build -o myapp main.go
```

## 觀測

```shell
cd bprftrace
bprftrace trace.bt
```

## 自認爲手巧的觀測方式

```shell
bpftrace -e 'uprobe:./myapp:main.Calculate { printf("被呼叫了！參數 a=%d, b=%d\n", reg("ax"), reg("bx")); }'
```

# server.go ( 簡單的http server)

## build

```shell
go build -o myserver server.go
```

## 測試

```shell
http 127.0.0.1:8080/hello?name=1234   
```

## 觀測

```shell
cd bprftrace
bprftrace trace_server.bt
```


#  測試Struct

```shell
http http://localhost:8080/hello/struct?name=Alice
```

## 觀測

```shell
bpftrace trace_service.bt
```



# PTR 

```shell
bpftrace trace_ptr.bt 
```

## 測試

```shell
fenrir@fenrir:~/code/lc/bprf_demo/bprftrace$ http http://localhost:8080/hello/ptr?name=ptr_input
HTTP/1.1 200 OK
Content-Length: 17
Content-Type: text/plain; charset=utf-8
Date: Tue, 24 Feb 2026 03:35:21 GMT

Hello, ptr_input!

```