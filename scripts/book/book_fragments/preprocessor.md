### 预处理器：宏、断言与条件编译

预处理器在真正编译前处理 `#include`、宏和条件编译。宏参数必须加括号，否则调用者的运算符优先级可能改变结果：

```c
#define SQUARE(x) ((x) * (x))
```

即使写对了括号，`SQUARE(i++)` 仍会把 `i++` 求值两次。需要单次求值时，优先使用 `static inline` 函数；需要按类型选择实现时，可以使用 C11 `_Generic`。

```c
static inline int abs_int(int x) { return x < 0 ? -x : x; }
#define ABS(x) _Generic((x), int: abs_int)(x)
```

头文件应有保护宏，避免同一个声明被展开多次：

```c
#ifndef CONFIG_H
#define CONFIG_H
/* 类型、常量和函数声明 */
#endif
```

`assert` 用来检查程序员的内部假设，不应替代用户输入校验。定义 `NDEBUG` 后，断言会被移除，所以断言表达式里不要放必须执行的副作用。

预定义宏可以帮助定位错误：

```c
#define CHECK(expr) \\
    do { if (!(expr)) fprintf(stderr, "%s:%d: %s\\n", \\
            __FILE__, __LINE__, #expr); } while (0)
```

怀疑宏展开结果时，用 `gcc -E source.c` 生成预处理后的源码再看；编译器不会替你猜宏作者的本意。

