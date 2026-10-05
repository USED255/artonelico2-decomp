/* hybrid 构建：src/matched/*.c 共用的外部符号声明。
 *
 * 这些名字与 splat 在 asm/ 里用的**完全一致**，也和 src/m2_probe.c 里的声明一致。
 * 若同名符号在 C 侧的类型与目标不一致，ee-gcc 生成的指令会变，objdiff 立刻能看出来。
 *
 * 本头文件只声明、不定义；不含任何会进入 .rodata/.data/.bss 的内容
 * （build_hybrid.sh 会检查编译产物里除 .text* 外没有非空的可分配段）。
 */
#ifndef AT2_MATCHED_EXTERNS_H
#define AT2_MATCHED_EXTERNS_H

extern int       D_007AF2D0;
extern void      func_00106028(void);
extern void      func_0011a93c(int, int, int, int, int);
extern void      func_0035b0f8(int, int, long long *);
extern long long func_0035aa10(long long, long long, long long);
extern void      func_00360918(void);

#endif /* AT2_MATCHED_EXTERNS_H */
