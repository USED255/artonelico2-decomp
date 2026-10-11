/* Mixed build: the external symbol declarations that src/matched/*.c share.

 * 混合构建：src/matched/*.c 共用的外部符号声明。
 *
 * The names agree with the names that splat writes in asm/.
 * 这些名字与 splat 在 asm/ 里用的**完全一致**。
 * When the C type of a symbol differs from the target type, ee-gcc emits different
 * instructions, and objdiff shows the difference at once.
 * 若同名符号在 C 侧的类型与目标不一致，ee-gcc 生成的指令会变，objdiff 立刻能看出来。
 *
 * This header only declares. It defines nothing. It holds no content that enters
 * .rodata, .data, or .bss. build_mixed.sh checks that a compiled object has no
 * non-empty allocatable section other than .text*.
 * 本头文件只声明、不定义；不含任何会进入 .rodata/.data/.bss 的内容
 * （build_mixed.sh 会检查编译产物里除 .text* 外没有非空的可分配段）。
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
