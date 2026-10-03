#### 位运算的掩码方法

位运算常用来管理一组开关。先给每个开关分配互不重叠的位，再用掩码操作它们：

```c
enum {
    FLAG_READ  = 1u << 0,
    FLAG_WRITE = 1u << 1,
    FLAG_DEBUG = 1u << 2
};

unsigned flags = 0;
flags |= FLAG_READ | FLAG_WRITE; /* 设置 */
flags &= ~FLAG_DEBUG;             /* 清除 */
if (flags & FLAG_WRITE) {         /* 测试 */
    puts("writable");
}
flags ^= FLAG_READ;               /* 翻转 */
```

移位的左操作数最好使用无符号类型。移位量必须小于类型宽度；对负数右移的结果由实现决定；有符号数左移溢出则是未定义行为。下面的程序把低八位打印出来，适合观察 `&`、`|`、`^` 和左移的实际结果：

```c
static void print_bits(unsigned char value) {
    for (int bit = 7; bit >= 0; --bit)
        putchar((value & (1u << bit)) ? '1' : '0');
}
```

```mermaid
flowchart LR
    A[状态字 flags] --> B[& 测试或清除]
    A --> C[| 设置]
    A --> D[^ 翻转]
    A --> E[<< / >> 移位]
    B --> F[设备状态或权限集合]
    C --> F
    D --> F
    E --> F
```
