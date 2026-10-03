#include <stdio.h>
#include <stdint.h>

int main(void) {
    _Bool ok = 1;
    /* TODO: 用 _Static_assert 断言 int32_t 与 int64_t 的大小，并在断言通过时输出 ok */
    (void)ok;
    return 0;
}

// Done
