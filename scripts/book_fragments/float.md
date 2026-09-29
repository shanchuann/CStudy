### 浮点数的存储与比较

`float` 和 `double` 用二进制科学计数法保存实数。以常见的 IEEE 754 单精度为例，一个 `float` 有 1 位符号、8 位指数和 23 位有效小数位。指数采用偏置值 127 保存，因此位模式并不是把小数点“挪到内存里”那么简单。

```c
#include <stdint.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    float x = 13.25f;
    uint32_t bits;
    memcpy(&bits, &x, sizeof bits);
    printf("x = %.2f\\n", x);
    printf("bits = 0x%08x\\n", bits);
    printf("sign=%u exponent=%u fraction=0x%06x\\n",
           bits >> 31, (bits >> 23) & 0xffu, bits & 0x7fffffu);
}
```

这里用 `memcpy` 读取对象表示，避免通过不兼容的指针类型直接解引用。浮点数比较也要留出误差：

```c
#include <math.h>
int nearly_equal(double a, double b, double eps) {
    return fabs(a - b) <= eps * fmax(1.0, fmax(fabs(a), fabs(b)));
}
```

不要用 `a == b` 判断两个计算结果是否“数学上相等”，除非你明确知道它们来自同一条无舍入误差的路径。金额、计数和文件大小优先使用整数；浮点数适合测量值、几何计算和统计结果。

![在 /home/shanchuan/CStudy 中运行的示例](assets/c-language/wsl-cstudy-run.png)
