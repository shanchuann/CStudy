#include <stdio.h>

// 将24小时制转换为12小时制
// "%02d:%02d %cM"
void convert_time(int hour, int minute, int *hour_12, int *minute_12, char *period) {
    if (hour == 0) {
        *hour_12 = 12;
        *period = 'A';
    } else if (hour == 12) {
        *hour_12 = 12;
        *period = 'P';
    } else if (hour < 12) {
        *hour_12 = hour;
        *period = 'A';
    } else {
        *hour_12 = hour - 12;
        *period = 'P';
    }
    *minute_12 = minute;
}